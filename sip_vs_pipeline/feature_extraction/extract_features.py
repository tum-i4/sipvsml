import argparse
import pathlib

from tqdm import tqdm

from sip_vs_pipeline.feature_extraction.extractor_base import FeatureExtractor, CompositeExtractor
from sip_vs_pipeline.feature_extraction.ir2vec import IR2VecExtractor
from sip_vs_pipeline.utils import write_blocks_df, read_blocks_df, get_all_block_files

TF_IDF_FEATURE_EXTRACTOR = 'tf_idf'
IR2VEC_FEATURE_EXTRACTOR = 'ir2vec'
SEG_FEATURE_EXTRACTOR = 'seg'
IR2VEC_VOCAB_PATH = pathlib.Path(__file__).parent / 'ir2vec_seed_embeddings.txt'


class TfIdfExtractor(FeatureExtractor):
    def __init__(self, name, rewrite=False) -> None:
        super().__init__(name, rewrite)

    def _extract_features(self, blocks_df, features_output_csv_path):
        return blocks_df


class SegExtractor(FeatureExtractor):
    def __init__(self, name, rewrite=False) -> None:
        super().__init__(name, rewrite)

    def _extract_features(self, blocks_df, features_output_csv_path):
        return blocks_df


def parse_args():
    parser = argparse.ArgumentParser(description='Extract features from protected binaries')
    parser.add_argument('--feature_extractor', choices=[
        TF_IDF_FEATURE_EXTRACTOR, IR2VEC_FEATURE_EXTRACTOR, SEG_FEATURE_EXTRACTOR, 'all'
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
    if feature_extractor == 'all':
        return CompositeExtractor(
            'all',
            TfIdfExtractor(TF_IDF_FEATURE_EXTRACTOR),
            IR2VecExtractor(TF_IDF_FEATURE_EXTRACTOR, IR2VEC_VOCAB_PATH),
            SegExtractor(SEG_FEATURE_EXTRACTOR)
        )


def process_blocks(extractor, blocks_file_path):
    blocks_df = read_blocks_df(blocks_file_path)
    updated_block_df = extractor.extract(blocks_file_path.parent, blocks_df)

    if updated_block_df.equals(blocks_df):
        write_blocks_df(blocks_file_path, updated_block_df)


def main():
    args = parse_args()
    labeled_bc_dir = pathlib.Path(args.labeled_bc_dir)

    all_block_files = list(get_all_block_files(labeled_bc_dir))
    extractor = create_feature_extractors(args.feature_extractor)
    for block_file in tqdm(all_block_files, desc='extracting features'):
        process_blocks(extractor, block_file)


if __name__ == '__main__':
    main()
