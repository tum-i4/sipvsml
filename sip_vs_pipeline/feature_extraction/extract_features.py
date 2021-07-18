import argparse
import pathlib
from concurrent.futures import ProcessPoolExecutor

from tqdm import tqdm

from sip_vs_pipeline.feature_extraction.code2vec import Code2VecExtractor
from sip_vs_pipeline.feature_extraction.extractor_base import CompositeExtractor, BlockFeatureExtractor
from sip_vs_pipeline.feature_extraction.ir2vec import IR2VecExtractor
from sip_vs_pipeline.feature_extraction.tfidf import extract_tf_idf_memory_friendly
from sip_vs_pipeline.utils import get_fold_dirs, CODE2VEC_REPOSITORY_PATH

TF_IDF_FEATURE_EXTRACTOR = 'tf_idf'
IR2VEC_FEATURE_EXTRACTOR = 'ir2vec'
SEG_FEATURE_EXTRACTOR = 'seg'
CODE2VEC_FEATURE_EXTRACTOR = 'code2vec'
IR2VEC_VOCAB_PATH = pathlib.Path(__file__).parent / 'ir2vec_seed_embeddings.txt'


class TfIdfExtractor(BlockFeatureExtractor):
    def __init__(self, name, rewrite=False, feature_count=200) -> None:
        super().__init__(name, rewrite)
        self._feature_count = feature_count

    def extract_using_blocks_df(self, blocks_df):
        tf_idf_df = extract_tf_idf_memory_friendly(blocks_df['w_63'], maxfeatures=self._feature_count, data_path='/tmp')
        tf_idf_df = tf_idf_df.rename(columns=lambda x: 'w_' + str(int(x) + 64))
        tf_idf_df['uid'] = blocks_df.index
        tf_idf_df.set_index('uid', inplace=True)
        return tf_idf_df


class SegExtractor(BlockFeatureExtractor):
    def __init__(self, name, rewrite=False, num_features=63, cleanup_blocks=True) -> None:
        super().__init__(name, rewrite)
        self._num_features = num_features
        self._cleanup_blocks = cleanup_blocks

    def extract_using_blocks_df(self, blocks_df):
        features_df = blocks_df[[f'w_{i}' for i in range(63)]]
        if self._cleanup_blocks:
            blocks_df.drop(columns=[col for col in blocks_df.columns if col.startswith('w')], inplace=True)
        return features_df


def parse_args():
    parser = argparse.ArgumentParser(description='Extract features from protected binaries')
    parser.add_argument('--path_to_ir2vec_vocab', help='Path to ir2vec vocabulary', default=IR2VEC_VOCAB_PATH)
    parser.add_argument('--feature_extractor', choices=[
        CODE2VEC_FEATURE_EXTRACTOR, TF_IDF_FEATURE_EXTRACTOR, IR2VEC_FEATURE_EXTRACTOR, SEG_FEATURE_EXTRACTOR, 'all'
    ], help='Name of the feature extractor to use')
    parser.add_argument(
        '--run_sequentially', default=False, action='store_true',
        help='Run processing sequentially, in a single process'
    )
    parser.add_argument(
        '--max_workers', default=None, required=False, type=int, help='Max worker processes to spawn for Process Pool'
    )
    parser.add_argument('labeled_bc_dir', help='Directory where labeled binaries are stored')
    args = parser.parse_args()
    return args


def create_feature_extractors(feature_extractor):
    if feature_extractor == TF_IDF_FEATURE_EXTRACTOR:
        return TfIdfExtractor(TF_IDF_FEATURE_EXTRACTOR)
    if feature_extractor == IR2VEC_FEATURE_EXTRACTOR:
        return IR2VecExtractor(IR2VEC_FEATURE_EXTRACTOR, IR2VEC_VOCAB_PATH)
    if feature_extractor == SEG_FEATURE_EXTRACTOR:
        return SegExtractor(SEG_FEATURE_EXTRACTOR)
    if feature_extractor == CODE2VEC_FEATURE_EXTRACTOR:
        return Code2VecExtractor(CODE2VEC_FEATURE_EXTRACTOR, CODE2VEC_REPOSITORY_PATH)

    if feature_extractor == 'all':
        return CompositeExtractor(
            'all',
            TfIdfExtractor(TF_IDF_FEATURE_EXTRACTOR),
            IR2VecExtractor(IR2VEC_FEATURE_EXTRACTOR, IR2VEC_VOCAB_PATH),
            SegExtractor(SEG_FEATURE_EXTRACTOR),
            Code2VecExtractor(CODE2VEC_FEATURE_EXTRACTOR, CODE2VEC_REPOSITORY_PATH)
        )


def process_blocks(args):
    extractor_name, k_fold_dirs = args
    extractor = create_feature_extractors(extractor_name)
    train_dir = k_fold_dirs / 'train'
    val_dir = k_fold_dirs / 'val'
    assert train_dir.exists() and val_dir.exists()
    extractor.extract(train_dir, val_dir)


def main():
    args = parse_args()
    labeled_bc_dir = pathlib.Path(args.labeled_bc_dir)
    all_fold_dirs = get_fold_dirs(labeled_bc_dir)
    all_fold_dirs = [x for x in all_fold_dirs if '/simple-cov/SUB/' in str(x)]

    extractor_name = args.feature_extractor

    if args.run_sequentially:
        for fold_dir in tqdm(list(all_fold_dirs), desc='extracting features'):
            process_blocks([extractor_name, fold_dir])
    else:
        with ProcessPoolExecutor(max_workers=args.max_workers) as process_pool:
            pool_args = [(extractor_name, fold_dir) for fold_dir in all_fold_dirs]
            list(tqdm(
                process_pool.map(process_blocks, pool_args),
                total=len(pool_args),
                desc='extracting features'
            ))


if __name__ == '__main__':
    main()
