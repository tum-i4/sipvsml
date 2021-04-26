import argparse
import os
import pathlib
import subprocess

from tqdm import tqdm

IR2VEC_BIN_PATH = os.getenv('IR2VEC_BIN_PATH', './ir2vec')


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('labeled_bc_dir')
    return parser.parse_args()


def get_bc_dirs(labeled_bc_dir):
    for sub_folder in ['mibench-cov', 'simple-cov']:
        for data_dir in (labeled_bc_dir / sub_folder).iterdir():
            yield data_dir


def get_all_bc_files(labeled_bc_dir):
    for data_dir in get_bc_dirs(labeled_bc_dir):
        for file in data_dir.iterdir():
            if file.name.endswith('.bc'):
                yield file


def write_generalized_instructions(bc_file_path, out_file_path):
    cmd = [
        IR2VEC_BIN_PATH,
        '-collectIR',
        '-o', out_file_path,
        bc_file_path
    ]
    resp_code = subprocess.call(cmd)
    if resp_code != 0 and out_file_path.exists():
        out_file_path.remove()


def generate_gin_files(labeled_bc_dir):
    all_bc_files = list(get_all_bc_files(labeled_bc_dir))
    for bc_file_path in tqdm(all_bc_files):
        out_file_path = bc_file_path.with_name(f'{bc_file_path.name[:-3]}.gin')
        if not out_file_path.exists():
            write_generalized_instructions(bc_file_path, out_file_path)


def main():
    args = parse_args()
    labeled_bc_dir = pathlib.Path(args.labeled_bc_dir)
    assert labeled_bc_dir.exists()
    generate_gin_files(labeled_bc_dir)


if __name__ == '__main__':
    main()
