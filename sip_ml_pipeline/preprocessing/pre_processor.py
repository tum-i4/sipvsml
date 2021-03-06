import gzip
import json
import os
import random
import re
import subprocess
from collections import defaultdict

from sip_ml_pipeline.preprocessing.ir_line_parser import generalize_ir_line
from sip_ml_pipeline.utils import read_blocks_df, write_blocks_df, write_relations_df, read_relations_df, \
    get_program_name_from_filename, CODE2VEC_REPOSITORY_PATH, LLVM_MODULE_LABELLING_PASS_SO_PATH


class PreProcessor:
    def run(self, protected_bc_dir):
        raise NotImplementedError


class ComposePP(PreProcessor):
    def __init__(self, *pps: PreProcessor) -> None:
        super().__init__()
        self.pps = pps

    def run(self, protected_bc_dir):
        for pp in self.pps:
            pp.run(protected_bc_dir)


class Ir2VecInstructionGen(PreProcessor):
    def __init__(self, ir_delimiter='|.|') -> None:
        super().__init__()
        self._ir_delimiter = ir_delimiter

    def _get_generalized_ir_block(self, ir_block_str):
        cleaned_irs = [x.strip() for x in ir_block_str.strip().split(self._ir_delimiter) if x.strip() != '']
        gen_irs = [generalize_ir_line(ci) for ci in cleaned_irs]
        return self._ir_delimiter.join(gen_irs)

    def run(self, protected_bc_dir):
        blocks_file_path = protected_bc_dir / 'blocks.csv.gz'
        blocks_df = read_blocks_df(blocks_file_path)
        blocks_df['generalized_block'] = blocks_df['w_63'].map(self._get_generalized_ir_block)
        write_blocks_df(blocks_file_path, blocks_df)


def get_default_block_columns():
    feature_names = [f'w_{i}' for i in range(64)]
    return ['uid'] + feature_names + ['program', 'subject']


class CompressToZip(PreProcessor):
    def run(self, protected_bc_dir):
        blocks_file_path = protected_bc_dir / 'blocks.csv'
        if blocks_file_path.exists():
            blocks_df = read_blocks_df(
                blocks_file_path,
                header=None,
                lineterminator='\r',
                sep=';',
                names=get_default_block_columns()
            )
            write_blocks_df(blocks_file_path.with_suffix('.csv.gz'), blocks_df)

        relations_file_path = protected_bc_dir / 'relations.csv'
        if relations_file_path.exists():
            relations_df = read_relations_df(
                relations_file_path,
                header=None,
                sep=';',
                names=['source', 'target', 'label'],
            )
            write_relations_df(
                relations_file_path.with_suffix('.csv.gz'),
                relations_df
            )


class RemoveRawBinaries(PreProcessor):
    def run(self, protected_bc_dir):
        for file in protected_bc_dir.iterdir():
            if file.suffix == '.bc':
                file.unlink()


class RemoveCsvFiles(PreProcessor):
    def run(self, protected_bc_dir):
        for file in protected_bc_dir.iterdir():
            if file.suffix == '.csv':
                file.unlink()


class DisassembleBC(PreProcessor):
    def __init__(self, llvm_dis_version='10') -> None:
        super().__init__()
        self.llvm_dis_version = llvm_dis_version

    def run(self, protected_bc_dir):
        for file in protected_bc_dir.iterdir():
            if file.suffix == '.bc':
                subprocess.check_call([f'llvm-dis-{self.llvm_dis_version}', str(file)])


class RemoveLLMetadata(PreProcessor):
    def __init__(self, llvm_dis_version='10') -> None:
        super().__init__()
        self.llvm_dis_version = llvm_dis_version
        self._metadata_re = re.compile(r', (![_a-zA-Z0-9 ,]+)+$')

    def run(self, protected_bc_dir):
        for file in protected_bc_dir.iterdir():
            if file.suffix == '.bc':
                file = file.with_suffix('.ll')
                with open(file) as inp:
                    content = inp.read()
                with open(file, 'w') as out:
                    out.write(self._remove_metadata(content))

    def _remove_metadata(self, ll_content):
        return '\n'.join(map(self._remove_line_metadata, ll_content.split('\n')))

    def _remove_line_metadata(self, ll_line):
        return self._metadata_re.sub('', ll_line)


def copy_file(src_path, dest_path):
    with open(src_path, 'rb') as inp, open(dest_path, 'wb') as out:
        out.write(inp.read())


class Code2VecPreProcessor(PreProcessor):
    def __init__(self, code2vec_repo_path=CODE2VEC_REPOSITORY_PATH) -> None:
        super().__init__()
        self.code2vec_repo_path = code2vec_repo_path

    def run(self, protected_bc_dir):
        bc_paths = [x for x in protected_bc_dir.iterdir() if x.suffix == '.bc']
        for bc_path in bc_paths:
            self._extract_ast_paths(bc_path)

    def _extract_ast_paths(self, bc_path):
        raw_c2v_path = bc_path.with_suffix('.raw_c2v.gz')

        if raw_c2v_path.exists() and raw_c2v_path.stat().st_size > 0:
            return raw_c2v_path

        ll_path = bc_path.with_suffix('.ll')
        assert ll_path.exists()

        cmd = [
            'python', str(self.code2vec_repo_path / 'LLIRExtractor' / 'extract.py'),
            '--file', str(ll_path)
        ]
        c2v_text = subprocess.check_output(cmd)
        assert len(c2v_text) > 0

        with gzip.open(raw_c2v_path, 'wb') as out:
            out.write(c2v_text)
        return raw_c2v_path


class PDGPreProcessor(PreProcessor):
    def __init__(self, labeled_bc_dir, docker_image_name='smwyg',
                 git_repo_url='https://github.com/mr-ma/smwyg-artifact.git') -> None:
        super().__init__()
        self.docker_image_name = docker_image_name
        self.git_repo_url = git_repo_url
        self.build_docker_image()
        self._compress_csv_files = CompressToZip()
        self._remove_csv_files = RemoveCsvFiles()
        self.labeled_bc_dir = labeled_bc_dir

    def build_docker_image(self):
        subprocess.run(['docker', 'build', '-t', self.docker_image_name, self.git_repo_url], check=True)

    def run(self, protected_bc_dir):
        docker_run = f'docker run --rm -v "{self.labeled_bc_dir.parent}":/home/sip/paperback:rw ' \
                     f'--security-opt seccomp=unconfined {self.docker_image_name}'

        bc_files = [file for file in protected_bc_dir.iterdir() if file.suffix == '.bc']
        for bc_file in bc_files:
            container_labeled_bcs = '/'.join(bc_file.parent.parts[bc_file.parts.index('LABELED-BCs'):])
            opt_command = 'opt-7 -load /home/sip/program-dependence-graph/build/libpdg.so -reg2mem -pdg-csv -append ' \
                          f'-relations "{container_labeled_bcs + "/relations.csv"}" ' \
                          f'-blocks "{container_labeled_bcs + "/blocks.csv"}" ' + \
                          f'-o "{container_labeled_bcs + f"/{bc_file.name}"}" ' + \
                          container_labeled_bcs + f'/{bc_file.name} > /dev/null'
            data_script = ' && '.join([
                'mkdir -p /home/sip/paperback/LABELED-BCs',
                'ln -s /home/sip/paperback/LABELED-BCs /home/sip/eval/LABELED-BCs',
                opt_command
            ])
            cmd = f'{docker_run} bash -c "{data_script}"'

            subprocess.run(cmd, shell=True, check=False)

        self._compress_csv_files.run(protected_bc_dir)
        self._remove_csv_files.run(protected_bc_dir)


class KFoldSplit(PreProcessor):
    def __init__(self, val_fraction=0.2, seed=42) -> None:
        super().__init__()
        self.seed = seed
        self.val_fraction = val_fraction

    def run(self, protected_bc_dir):
        programs_dict = self._get_programs_dict(protected_bc_dir)

        folds_dir = (protected_bc_dir / 'folds')
        random.seed(self.seed)
        program_names = list(programs_dict.keys())

        val_data_size = int(len(program_names) * self.val_fraction)
        fold_dirs = []
        for k in range(round(1 / self.val_fraction)):
            val_keys = program_names[val_data_size * k: val_data_size * (k + 1)]
            train_keys = [p for p in program_names if p not in val_keys]
            k_fold_dir = folds_dir / f'k_fold_{k}'

            train_dir, val_dir = k_fold_dir / 'train', k_fold_dir / 'val'
            os.makedirs(train_dir, exist_ok=True)
            os.makedirs(val_dir, exist_ok=True)

            self._write_json(train_dir / 'programs.json', train_keys)
            self._write_json(val_dir / 'programs.json', val_keys)

            fold_dirs.append(k_fold_dir)

        return fold_dirs

    @staticmethod
    def _write_json(file_path, json_data):
        with open(file_path, 'w', encoding='utf-8') as out:
            json.dump(json_data, out, indent=4, ensure_ascii=False)

    @staticmethod
    def split_and_write_csv_files(block_df, relations_df, out_dir, program):
        fold_blocks_df = block_df[block_df['program'].map(lambda x: x.split('-')[0]).isin(program)]
        write_blocks_df(out_dir / 'blocks.csv.gz', fold_blocks_df)
        fold_relations_df = relations_df[
            relations_df['source'].isin(fold_blocks_df.index) | relations_df['target'].isin(fold_blocks_df.index)
            ]
        write_relations_df(out_dir / 'relations.csv.gz', fold_relations_df)

    @staticmethod
    def _copy_files(programs_dict, dest_dir, keys):
        for key in keys:
            for bc_path in programs_dict[key]:
                copy_file(bc_path, dest_dir / bc_path.name)

    @staticmethod
    def _get_programs_dict(protected_bc_dir):
        programs_dict = defaultdict(list)
        for child in protected_bc_dir.iterdir():
            if child.name.endswith('.bc'):
                # programs_dict[child.name[:-3].split('-')[0]].append(child)
                programs_dict[get_program_name_from_filename(child.name)].append(child)
        return programs_dict


class LLVMPassLabels(PreProcessor):
    def __init__(self, llvm_so_path=LLVM_MODULE_LABELLING_PASS_SO_PATH) -> None:
        super().__init__()
        self.llvm_so_path = llvm_so_path

    def run(self, protected_bc_dir):
        bc_files = [x for x in protected_bc_dir.iterdir() if x.suffix == '.bc']
        for bc_file_path in bc_files:
            cmd = [
                'opt-10',
                '-load',
                str(self.llvm_so_path),
                f'-bc-file-path=LABELED-BCs/{bc_file_path.parent.parent.name}/{bc_file_path.parent.name}/',
                '-legacy-module-labelling',
                '-disable-output',
                str(bc_file_path)
            ]
            llvm_pass_labels = subprocess.check_output(cmd, stderr=subprocess.STDOUT).decode()
            with open(bc_file_path.with_suffix('.sip_labels'), 'w', encoding='utf-8') as out:
                out.write(llvm_pass_labels)
