import argparse
import pathlib
import traceback

import pandas as pd
from tqdm import tqdm

from ir_line_parser import generalize_ir_line


class PreProcessor:
    def update_block_df(self, blocks_df):
        raise NotImplementedError


class ComposePP(PreProcessor):
    def __init__(self, *pps: PreProcessor) -> None:
        super().__init__()
        self.pps = pps

    def update_block_df(self, blocks_df):
        for pp in self.pps:
            blocks_df = pp.update_block_df(blocks_df)
        return blocks_df


class Ir2VecInstructionGen(PreProcessor):
    def __init__(self, ir_delimiter='|.|') -> None:
        super().__init__()
        self._ir_delimiter = ir_delimiter

    def _get_generalized_ir_block(self, ir_block_str):
        cleaned_irs = [x.strip() for x in ir_block_str.strip().split(self._ir_delimiter) if x.strip() != '']
        gen_irs = [generalize_ir_line(ci) for ci in cleaned_irs]
        return self._ir_delimiter.join(gen_irs)

    def update_block_df(self, blocks_df):
        blocks_df['generalized_block'] = blocks_df['w_63'].map(self._get_generalized_ir_block)
        return blocks_df


def parse_args():
    parser = argparse.ArgumentParser(description='Preprocess protected binary programs')
    parser.add_argument('labeled_bc_dir', help='Directory where labeled binaries are stored')
    parser.add_argument(
        '--preprocessor', choices=['general_ir', 'all'], default='all', help='Which preprocessor to run'
    )
    args = parser.parse_args()
    return args


def get_all_block_files(labeled_bc_dir):
    for sub_folder in ['simple-cov', 'mibench-cov']:
        for data_dir in (labeled_bc_dir / sub_folder).iterdir():
            yield data_dir / 'blocks.csv'


def get_block_file_header(blocks_file_path):
    with open(blocks_file_path) as inp:
        first_line = inp.readline().strip()
        if first_line.startswith('uid'):
            return first_line.split(';')
        return None


def read_blocks_df(blocks_file_path):
    header = get_block_file_header(blocks_file_path)
    blocks_df = pd.read_csv(
        blocks_file_path,
        lineterminator='\r',
        sep=';',
        header=None if header is None else 'infer',
        index_col=False,
        dtype={'uid': object},
        names=get_default_block_columns() if header is None else None
    )
    blocks_df.set_index('uid', inplace=True)
    return blocks_df


def get_default_block_columns():
    feature_names = ["w_{}".format(ii) for ii in range(64)]
    return ['uid'] + feature_names + ["program"] + ["subject"]


def process_df(preprocessor, blocks_file_path):
    try:
        blocks_df = read_blocks_df(blocks_file_path)
        updated_block_df = preprocessor.update_block_df(blocks_df)
        write_blocks_df(blocks_file_path, updated_block_df)
        return True
    except Exception:
        traceback.print_exc()


def write_blocks_df(blocks_file_path, updated_block_df):
    updated_block_df.reset_index().to_csv(
        blocks_file_path,
        line_terminator='\r',
        sep=';',
        header=True,
        index=False
    )


def create_preprocessor(preprocessor):
    if preprocessor == 'all':
        ir2vec = Ir2VecInstructionGen()
        return ComposePP(ir2vec)
    if preprocessor == 'general_ir':
        return Ir2VecInstructionGen()


def main():
    args = parse_args()
    labeled_bc_dir = pathlib.Path(args.labeled_bc_dir)
    all_block_files = list(get_all_block_files(labeled_bc_dir))
    preprocessor = create_preprocessor(args.preprocessor)
    for block_file in tqdm(all_block_files, desc='preprocessing binaries'):
        process_df(preprocessor, block_file)


if __name__ == '__main__':
    main()
