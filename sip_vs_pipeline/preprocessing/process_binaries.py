import argparse
import pathlib

from tqdm import tqdm

from ir_line_parser import generalize_ir_line
from sip_vs_pipeline.utils import write_blocks_df, read_blocks_df, get_all_block_files


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


def process_df(preprocessor, blocks_file_path):
    blocks_df = read_blocks_df(blocks_file_path)
    updated_block_df = preprocessor.update_block_df(blocks_df)
    write_blocks_df(blocks_file_path, updated_block_df)
    return True


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
