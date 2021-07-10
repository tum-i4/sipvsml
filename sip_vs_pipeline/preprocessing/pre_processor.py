import os
import pathlib
import random
import shutil
import subprocess
from collections import defaultdict

from sip_vs_pipeline.preprocessing.ir_line_parser import generalize_ir_line
from sip_vs_pipeline.utils import read_blocks_df, write_blocks_df, write_relations_df, read_relations_df

CODE2VEC_REPOSITORY_PATH = pathlib.Path('/home/nika/Desktop/Thesis/code2vec')


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


def copy_file(src_path, dest_path):
    with open(src_path, 'rb') as inp, open(dest_path, 'wb') as out:
        out.write(inp.read())


class Code2VecPreProcessor(PreProcessor):
    def __init__(self, code2vec_repo_path=CODE2VEC_REPOSITORY_PATH, k_folds=11, train_fraction_size=0.8) -> None:
        super().__init__()
        self.code2vec_repo_path = code2vec_repo_path
        self.k_folds = k_folds
        self.train_fraction = train_fraction_size

    def run(self, protected_bc_dir):
        bc_paths = [x for x in protected_bc_dir.iterdir() if x.suffix == '.bc']
        c2v_paths = [self._extract_ast_paths(bc_path) for bc_path in bc_paths]
        programs_dict = self._get_programs_dict(c2v_paths)

        folds_dir = (protected_bc_dir / 'folds')
        if folds_dir.exists():
            shutil.rmtree(folds_dir)

        fold_dirs = self._create_fold_dirs(folds_dir, programs_dict)
        for fold_dir in fold_dirs:
            self._preprocess_fold_dir(fold_dir)

    def _create_fold_dirs(self, folds_dir, programs_dict):
        program_names = list(programs_dict.keys())
        train_split_index = int(len(program_names) * self.train_fraction)
        fold_dirs = []
        random.seed(42)
        for k in range(self.k_folds):
            random.shuffle(program_names)
            train_keys, val_keys = program_names[:train_split_index], program_names[train_split_index:]
            k_fold_dir = folds_dir / f'k_fold_{k}'
            train_dir, val_dir = k_fold_dir / 'train', k_fold_dir / 'val'
            os.makedirs(train_dir, exist_ok=True)
            os.makedirs(val_dir, exist_ok=True)
            self._copy_files(programs_dict, train_dir, train_keys)
            self._copy_files(programs_dict, val_dir, val_keys)
            fold_dirs.append(k_fold_dir)
        return fold_dirs

    @staticmethod
    def _copy_files(programs_dict, dest_dir, keys):
        for key in keys:
            for bc_path in programs_dict[key]:
                copy_file(bc_path, dest_dir / bc_path.name)

    @staticmethod
    def _get_programs_dict(file_paths):
        programs_dict = defaultdict(list)
        for file in file_paths:
            programs_dict[file.name.split('-')[0].split('.')[0]].append(file)
        return programs_dict

    def _extract_ast_paths(self, bc_path):
        raw_c2v_path = bc_path.with_suffix('.raw_c2v')

        if raw_c2v_path.exists():
            return raw_c2v_path

        ll_path = bc_path.with_suffix('.ll')
        if not ll_path.exists():
            self._disassemble(bc_path)

        cmd = [
            'python', str(self.code2vec_repo_path / 'LLIRExtractor' / 'extract.py'),
            '--file', str(ll_path)
        ]
        c2v_text = subprocess.check_output(cmd)
        with open(raw_c2v_path, 'wb') as out:
            out.write(c2v_text)
        return raw_c2v_path

    @staticmethod
    def _disassemble(bc_path):
        subprocess.check_call(['llvm-dis-10', str(bc_path)])

    def _preprocess_fold_dir(self, fold_dir):
        cmd = [
            'bash',
            str(self.code2vec_repo_path / 'preprocess_llir_sip_vs_ml.sh'),
            str(fold_dir)
        ]
        subprocess.check_call(cmd, shell=True)


class PDGPreProcessor(PreProcessor):
    def __init__(self, labeled_bc_dir, docker_image_name='smwyg',
                 git_repo_url='https://github.com/mr-ma/smwyg-artifact.git') -> None:
        super().__init__()
        self.docker_image_name = docker_image_name
        self.git_repo_url = git_repo_url
        self.build_docker_image()
        self._compress_csv_files = CompressToZip()
        self._remove_csv_files = RemoveCsvFiles()
        self._pdg_script_path = pathlib.Path(__file__).absolute().parent / 'extract_pdg_files.sh'
        self.labeled_bc_dir = labeled_bc_dir

    def build_docker_image(self):
        subprocess.run(['docker', 'build', '-t', self.docker_image_name, self.git_repo_url], check=True)

    def run(self, protected_bc_dir):
        docker_run = f'docker run --rm -v "{self.labeled_bc_dir.parent}":/home/sip/paperback:rw ' \
                     f'--security-opt seccomp=unconfined {self.docker_image_name}'

        bc_files = [file for file in protected_bc_dir.iterdir() if file.suffix == '.bc']
        for bc_file in bc_files:
            container_labeled_bcs = '/'.join(bc_file.parts[bc_file.parts.index('LABELED-BCs'):])
            opt_command = 'opt-7 -load /home/sip/program-dependence-graph/build/libpdg.so -reg2mem -pdg-csv -append ' \
                          f'-relations "{container_labeled_bcs + "/relations.csv"}" ' \
                          f'-blocks "{container_labeled_bcs + "/blocks.csv"}" ' + \
                          container_labeled_bcs
            data_script = ' && '.join([
                'mkdir -p /home/sip/paperback/LABELED-BCs',
                'ln -s /home/sip/paperback/LABELED-BCs /home/sip/eval/LABELED-BCs',
                opt_command
            ])
            cmd = f'{docker_run} bash -c "{data_script}"'

            subprocess.run(cmd, shell=True, check=True)

        self._compress_csv_files.run(protected_bc_dir)
        self._remove_csv_files.run(protected_bc_dir)
