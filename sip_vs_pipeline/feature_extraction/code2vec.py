import pathlib
import subprocess

import pandas as pd

from sip_vs_pipeline.feature_extraction.extractor_base import FeatureExtractor

CODE2VEC_REPOSITORY_PATH = pathlib.Path('/home/nika/Desktop/Thesis/code2vec')
CODE2VEC_LOAD_MODEL_PATH = CODE2VEC_REPOSITORY_PATH / 'models' / 'llir-full' / 'saved_model_iter4'
CODE2VEC_EXTRACTOR_PATH = pathlib.Path('/home/nika/Desktop/Thesis/sip_vs_ml/code2vec_extractor/extract.py')
CODE2VEC_DATA_PATH = pathlib.Path('/media/nika/Data/SIP_DATA/code2vec_data/')
LLVM_MODULE_LABELLING_PASS_SO_PATH = pathlib.Path(__file__).parent.parent.parent / 'code2vec_extractor' / \
                                     'llvm_labelling_pass' / 'build' / 'libModuleLabelling.so'


class Code2VecExtractor(FeatureExtractor):
    def __init__(self, name, llvm_so_path, code2vec_path, code2vec_extractor_path, rewrite=False) -> None:
        super().__init__(name, rewrite)
        self.llvm_so_path = llvm_so_path
        self.code2vec_path = code2vec_path
        self.code2vec_extractor_path = code2vec_extractor_path
        self.binaries_dir = None

    def extract(self, binaries_dir, blocks_df):
        self.binaries_dir = binaries_dir
        return super().extract(binaries_dir, blocks_df)

    def _extract_features(self, blocks_df):
        bc_paths = [x for x in self.binaries_dir.iterdir() if x.suffix == '.bc']
        features = []
        all_block_uids = set(blocks_df.index)
        for bc_path in bc_paths:
            code2vec_vectors_path = self._extract_code2vec_vectors(bc_path)
            df = self._read_feature_vectors(bc_path, code2vec_vectors_path)
            assert len(set(df[0]) & all_block_uids) > 0
            features.append(df)
        return pd.concat(features)

    def _generate_c2v_file(self, bc_path):
        self._disassemble(bc_path)
        raw_c2v_path = self._extract_ast_paths(bc_path)
        out_path = self._preprocess_c2v_ast_paths(bc_path, raw_c2v_path)
        return out_path

    def _extract_code2vec_vectors(self, bc_path):
        code2vec_vectors = bc_path.parent / f'{bc_path.name.split(".")[0]}.preprocessed.c2v.vectors'
        if not code2vec_vectors.exists() or self.rewrite:
            c2v_file_path = self._generate_c2v_file(bc_path)
            cmd = [
                'python',
                str(self.code2vec_path / 'code2vec.py'),
                '--load',
                str(CODE2VEC_LOAD_MODEL_PATH),
                '--framework',
                'tensorflow',
                '--export_code_vectors',
                '--test',
                str(c2v_file_path)
            ]
            subprocess.check_call(cmd)
        return code2vec_vectors

    def _preprocess_c2v_ast_paths(self, bc_path, raw_c2v_path):
        out_path = bc_path.parent / f'{bc_path.name.split(".")[0]}.preprocessed.c2v'
        if not out_path.exists() or self.rewrite:
            cmd = [
                'python', str(self.code2vec_path / 'preprocess_sip_vs_ml.py'),
                '--file_path', str(raw_c2v_path),
                # '--train_data', str(CODE2VEC_DATA_PATH / 'code2vec_llir.train.raw.txt'),
                # '--test_data', str(CODE2VEC_DATA_PATH / 'code2vec_llir.test.raw.txt'),
                # '--val_data', str(CODE2VEC_DATA_PATH / 'code2vec_llir.val.raw.txt'),
                # '--max_contexts', '200',
                # '--word_vocab_size', '1301136',
                # '--path_vocab_size', '911417',
                # '--target_vocab_size', '261245',
                '--word_histogram', str(CODE2VEC_DATA_PATH / 'code2vec_llir.histo.ori.c2v'),
                '--path_histogram', str(CODE2VEC_DATA_PATH / 'code2vec_llir.histo.path.c2v'),
                '--target_histogram', str(CODE2VEC_DATA_PATH / 'code2vec_llir.histo.tgt.c2v')
            ]
            subprocess.check_call(cmd, cwd=str(raw_c2v_path.parent))
        return out_path

    def _extract_ast_paths(self, bc_path):
        raw_c2v_path = bc_path.with_suffix('.raw_c2v')
        if not raw_c2v_path.exists() or self.rewrite:
            cmd = [
                'python', str(self.code2vec_extractor_path),
                '--file', str(bc_path.with_suffix('.ll'))
            ]
            c2v_text = subprocess.check_output(cmd)
            with open(raw_c2v_path, 'wb') as out:
                out.write(c2v_text)
        return raw_c2v_path

    def _disassemble(self, bc_path):
        if not bc_path.with_suffix('.ll').exists() or self.rewrite:
            subprocess.check_call(['llvm-dis-10', str(bc_path)])

    def _read_feature_vectors(self, bc_file_path, code2vec_vectors_path):
        code2vec_vectors = []
        with open(code2vec_vectors_path) as inp:
            for line in inp:
                code2vec_vectors.append([float(x) for x in line.split()])

        cmd = [
            'opt-10',
            '-load',
            str(self.llvm_so_path),
            f'-bc-file-path=LABELED-BCs/{bc_file_path.parent.parent.name}/{bc_file_path.parent.name}/',
            '-legacy-module-labelling',
            '-disable-output',
            str(bc_file_path)
        ]
        llvm_pass_labels = subprocess.check_output(cmd, stderr=subprocess.STDOUT).decode().splitlines(keepends=False)

        assert len(code2vec_vectors) == len(llvm_pass_labels)

        features = []
        for feature_vector, llvm_pass_line in zip(code2vec_vectors, llvm_pass_labels):
            block_name, block_uid, _ = llvm_pass_line.split('\t')
            features.append([block_uid] + feature_vector)
        return pd.DataFrame(features)
