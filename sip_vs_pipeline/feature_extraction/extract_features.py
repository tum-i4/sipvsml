import argparse
import pathlib
import subprocess
from concurrent.futures import ProcessPoolExecutor

import pandas as pd
from tqdm import tqdm

from sip_vs_pipeline.feature_extraction.extractor_base import FeatureExtractor, CompositeExtractor
from sip_vs_pipeline.feature_extraction.ir2vec import IR2VecExtractor
from sip_vs_pipeline.feature_extraction.tfidf import extract_tf_idf_memory_friendly
from sip_vs_pipeline.utils import write_blocks_df, read_blocks_df, get_files_from_bc_dir

TF_IDF_FEATURE_EXTRACTOR = 'tf_idf'
IR2VEC_FEATURE_EXTRACTOR = 'ir2vec'
SEG_FEATURE_EXTRACTOR = 'seg'
CODE2VEC_FEATURE_EXTRACTOR = 'code2vec'
IR2VEC_VOCAB_PATH = pathlib.Path(__file__).parent / 'ir2vec_seed_embeddings.txt'

LLVM_MODULE_LABELLING_PASS_SO_PATH = pathlib.Path(__file__).parent.parent.parent / 'code2vec_extractor' / \
                                     'llvm_labelling_pass' / 'build' / 'libModuleLabelling.so'
CODE2VEC_REPOSITORY_PATH = pathlib.Path('/home/nika/Desktop/Thesis/code2vec')
CODE2VEC_LOAD_MODEL_PATH = CODE2VEC_REPOSITORY_PATH / 'models' / 'llir-full' / 'saved_model_iter4'
CODE2VEC_EXTRACTOR_PATH = pathlib.Path('/home/nika/Desktop/Thesis/sip_vs_ml/code2vec_extractor/extract.py')
CODE2VEC_DATA_PATH = pathlib.Path('/media/nika/Data/SIP_DATA/code2vec_data/')


class TfIdfExtractor(FeatureExtractor):
    def __init__(self, name, rewrite=False, feature_count=200) -> None:
        super().__init__(name, rewrite)
        self._feature_count = feature_count

    def _extract_features(self, blocks_df):
        tf_idf_df = extract_tf_idf_memory_friendly(blocks_df['w_63'], maxfeatures=self._feature_count, data_path='/tmp')
        tf_idf_df = tf_idf_df.rename(columns=lambda x: 'w_' + str(int(x) + 64))
        tf_idf_df['uid'] = blocks_df.index
        tf_idf_df.set_index('uid', inplace=True)
        return tf_idf_df


class SegExtractor(FeatureExtractor):
    def __init__(self, name, rewrite=False, num_features=63, cleanup_blocks=True) -> None:
        super().__init__(name, rewrite)
        self._num_features = num_features
        self._cleanup_blocks = cleanup_blocks

    def _extract_features(self, blocks_df):
        features_df = blocks_df[[f'w_{i}' for i in range(63)]]
        if self._cleanup_blocks:
            blocks_df.drop(columns=[col for col in blocks_df.columns if col.startswith('w')], inplace=True)
        return features_df


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


def parse_args():
    parser = argparse.ArgumentParser(description='Extract features from protected binaries')
    parser.add_argument('--path_to_ir2vec_vocab', help='Path to ir2vec vocabulary', default=IR2VEC_VOCAB_PATH)
    parser.add_argument('--path_to_llvm_labelling_so', help='Path to llvm module labelling pass shared object',
                        default=LLVM_MODULE_LABELLING_PASS_SO_PATH)
    parser.add_argument('--feature_extractor', choices=[
        CODE2VEC_FEATURE_EXTRACTOR, TF_IDF_FEATURE_EXTRACTOR, IR2VEC_FEATURE_EXTRACTOR, SEG_FEATURE_EXTRACTOR, 'all'
    ], help='Name of the feature extractor to use')
    parser.add_argument('labeled_bc_dir', help='Directory where labeled binaries are stored')
    args = parser.parse_args()
    return args


def create_feature_extractors(feature_extractor):
    if feature_extractor == TF_IDF_FEATURE_EXTRACTOR:
        return TfIdfExtractor(TF_IDF_FEATURE_EXTRACTOR)
    if feature_extractor == IR2VEC_FEATURE_EXTRACTOR:
        return IR2VecExtractor(TF_IDF_FEATURE_EXTRACTOR, IR2VEC_VOCAB_PATH)
    if feature_extractor == SEG_FEATURE_EXTRACTOR:
        return SegExtractor(SEG_FEATURE_EXTRACTOR)
    if feature_extractor == CODE2VEC_FEATURE_EXTRACTOR:
        return Code2VecExtractor(
            CODE2VEC_FEATURE_EXTRACTOR,  LLVM_MODULE_LABELLING_PASS_SO_PATH, CODE2VEC_REPOSITORY_PATH,
            CODE2VEC_EXTRACTOR_PATH
        )
    if feature_extractor == 'all':
        return CompositeExtractor(
            'all',
            TfIdfExtractor(TF_IDF_FEATURE_EXTRACTOR),
            IR2VecExtractor(IR2VEC_FEATURE_EXTRACTOR, IR2VEC_VOCAB_PATH),
            SegExtractor(SEG_FEATURE_EXTRACTOR),
            Code2VecExtractor(
                CODE2VEC_FEATURE_EXTRACTOR, LLVM_MODULE_LABELLING_PASS_SO_PATH, CODE2VEC_REPOSITORY_PATH,
                CODE2VEC_EXTRACTOR_PATH
            )
        )


def process_blocks(args):
    extractor, blocks_file_path = args
    blocks_df = read_blocks_df(blocks_file_path)
    updated_block_df = extractor.extract(blocks_file_path.parent, blocks_df)
    write_blocks_df(blocks_file_path, updated_block_df)


def main():
    args = parse_args()
    labeled_bc_dir = pathlib.Path(args.labeled_bc_dir)
    all_block_files = get_files_from_bc_dir(labeled_bc_dir, 'blocks.csv.gz')
    extractor = create_feature_extractors(args.feature_extractor)

    with ProcessPoolExecutor() as process_pool:
        args = [(extractor, block_file) for block_file in all_block_files]
        list(tqdm(
            process_pool.map(process_blocks, args),
            total=len(args),
            desc='extracting features'
        ))


if __name__ == '__main__':
    main()
