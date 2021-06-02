import argparse
import pathlib

from tqdm import tqdm

from ir_line_parser import generalize_ir_line
from sip_vs_pipeline.utils import write_blocks_df, read_blocks_df, get_files_from_bc_dir, read_relations_df, \
    write_relations_df


class PreProcessor:
    def update_block_df(self, blocks_df):
        raise NotImplementedError

    def update_relations_df(self, relations_df):
        raise NotImplementedError


class ComposePP(PreProcessor):
    def __init__(self, *pps: PreProcessor) -> None:
        super().__init__()
        self.pps = pps

    def update_block_df(self, blocks_df):
        for pp in self.pps:
            blocks_df = pp.update_block_df(blocks_df)
        return blocks_df

    def update_relations_df(self, relations_df):
        for pp in self.pps:
            relations_df = pp.update_relations_df(relations_df)
        return relations_df


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

    def update_relations_df(self, relations_df):
        return relations_df


def parse_args():
    parser = argparse.ArgumentParser(description='Preprocess protected binary programs')
    parser.add_argument('labeled_bc_dir', help='Directory where labeled binaries are stored')
    parser.add_argument(
        '--preprocessor', choices=['general_ir', 'all'], default='all',
        help='Which preprocessor to run'
    )
    parser.add_argument(
        '--input_format', choices=['.csv', '.feather'], default='.csv',
        help='Format for reading blocks and relations files'
    )
    parser.add_argument(
        '--output_format', choices=['.csv', '.feather'], default='.feather',
        help='Format for writing blocks and relations files'
    )
    args = parser.parse_args()
    return args


def process_df(preprocessor, blocks_file_path, relations_file_path, output_format):
    blocks_df = read_blocks_df(blocks_file_path)
    updated_block_df = preprocessor.update_block_df(blocks_df)
    write_blocks_df(blocks_file_path.with_suffix(output_format), updated_block_df)

    relations_df = read_relations_df(relations_file_path)
    relations_df = preprocessor.update_relations_df(relations_df)
    write_relations_df(relations_file_path.with_suffix(output_format), relations_df)
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
    input_format = args.input_format
    output_format = args.output_format

    all_block_files = get_files_from_bc_dir(labeled_bc_dir, f'blocks{input_format}')
    all_relation_files = get_files_from_bc_dir(labeled_bc_dir, f'relations{input_format}')
    preprocessor = create_preprocessor(args.preprocessor)
    all_files = list(zip(all_block_files, all_relation_files))
    for block_file, relation_file in tqdm(all_files, desc='preprocessing binaries'):
        process_df(preprocessor, block_file, relation_file, output_format)


if __name__ == '__main__':
    main()
