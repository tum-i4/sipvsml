import argparse
import pathlib
from concurrent.futures import ProcessPoolExecutor

from tqdm import tqdm

from sip_vs_pipeline.feature_extraction.code2vec import Code2VecExtractor, CODE2VEC_REPOSITORY_PATH, \
    CODE2VEC_EXTRACTOR_PATH, LLVM_MODULE_LABELLING_PASS_SO_PATH
from sip_vs_pipeline.feature_extraction.extractor_base import FeatureExtractor, CompositeExtractor
from sip_vs_pipeline.feature_extraction.ir2vec import IR2VecExtractor
from sip_vs_pipeline.feature_extraction.tfidf import extract_tf_idf_memory_friendly
from sip_vs_pipeline.utils import write_blocks_df, read_blocks_df, get_files_from_bc_dir

TF_IDF_FEATURE_EXTRACTOR = 'tf_idf'
IR2VEC_FEATURE_EXTRACTOR = 'ir2vec'
SEG_FEATURE_EXTRACTOR = 'seg'
CODE2VEC_FEATURE_EXTRACTOR = 'code2vec'
IR2VEC_VOCAB_PATH = pathlib.Path(__file__).parent / 'ir2vec_seed_embeddings.txt'


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
