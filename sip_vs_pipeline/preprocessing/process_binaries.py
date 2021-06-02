import argparse
import pathlib
from concurrent.futures import ProcessPoolExecutor

from tqdm import tqdm

from sip_vs_pipeline.preprocessing.pre_processor import ComposePP, Ir2VecInstructionGen, \
    CompressToZip, RemoveCsvFiles, RemoveRawBinaries
from sip_vs_pipeline.utils import get_protected_bc_dirs


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
    with ProcessPoolExecutor() as process_pool:
        list(tqdm(
            process_pool.map(preprocessor.run, bc_dirs),
            total=len(bc_dirs),
            desc='preprocessing binaries'
        ))


if __name__ == '__main__':
    main()
