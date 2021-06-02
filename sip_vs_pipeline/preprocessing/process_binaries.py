import argparse
import pathlib

from tqdm import tqdm

from sip_vs_pipeline.preprocessing.pre_processor import ComposePP, Ir2VecInstructionGen, \
    CompressToZip, RemoveCsvFiles, RemoveRawBinaries
from sip_vs_pipeline.utils import write_blocks_df, read_blocks_df, read_relations_df, \
    write_relations_df, get_protected_bc_dirs


def parse_args():
    parser = argparse.ArgumentParser(description='Preprocess protected binary programs')
    parser.add_argument('labeled_bc_dir', help='Directory where labeled binaries are stored')
    parser.add_argument(
        '--preprocessor', choices=[
            'compress_csv', 'general_ir' 'remove_raw_bc', 'remove_csv_files', 'all'
        ], default='all',
        help='Which preprocessor to run'
    )
    parser.add_argument(
        '--input_format', choices=['.csv', '.feather'], default='.csv',
        help='Format for reading blocks and relations files'
    )
    parser.add_argument(
        '--output_format', choices=['.csv', '.feather', '.csv.zip'], default='.csv.zip',
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
        return ComposePP(
            CompressToZip(),
            Ir2VecInstructionGen(),
            RemoveRawBinaries(),
            RemoveCsvFiles()
        )
    if preprocessor == 'compress_csv':
        return CompressToZip()
    if preprocessor == 'remove_raw_bc':
        return RemoveRawBinaries()
    if preprocessor == 'remove_csv_files':
        return RemoveCsvFiles()
    if preprocessor == 'general_ir':
        return Ir2VecInstructionGen()


def main():
    args = parse_args()
    labeled_bc_dir = pathlib.Path(args.labeled_bc_dir)

    preprocessor = create_preprocessor(args.preprocessor)
    bc_dirs = list(get_protected_bc_dirs(labeled_bc_dir))
    for protected_bc_dir in tqdm(bc_dirs, desc='preprocessing binaries'):
        preprocessor.run(protected_bc_dir)


if __name__ == '__main__':
    main()
