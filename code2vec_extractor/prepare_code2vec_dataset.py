import argparse
import os
import pathlib
import random
import subprocess
from collections import defaultdict

from tqdm import tqdm


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('labeled_bc_dir', help='Directory where labelled llvm .bc files are stored')
    parser.add_argument('output_dir', help='Output directory for train, val, test directories')
    return parser.parse_args()


def read_bc_files(labeled_bc_dir):
    res_dict = defaultdict(list)
    for sub_dir in labeled_bc_dir.iterdir():
        for obfs_dir in sub_dir.iterdir():
            for file in obfs_dir.iterdir():
                if file.suffix == '.bc':
                    res_dict[file.name.split('-')[0].split('.')[0]].append(file)
    return res_dict


def disassemble(out_path):
    subprocess.check_call(['llvm-dis-10', str(out_path)])


def copy_file(bc_path, out_path):
    with open(bc_path, 'rb') as inp:
        with open(out_path, 'wb') as out:
            out.write(inp.read())


def write_programs(bc_files, data_keys, data_dir):
    os.makedirs(data_dir, exist_ok=True)
    for key in tqdm(data_keys, desc=f'processing {data_dir.name} data'):
        paths = bc_files[key]
        for bc_path in paths:
            out_path = data_dir / '__'.join(bc_path.parts[-2:])
            copy_file(bc_path, out_path)
            disassemble(out_path)


def main():
    args = parse_args()
    labeled_bc_dir = pathlib.Path(args.labeled_bc_dir)
    bc_files = read_bc_files(labeled_bc_dir)
    out_dir = pathlib.Path(args.output_dir)

    random.seed(42)
    keys = list(bc_files.keys())
    random.shuffle(keys)
    train, val, test = keys[:39], keys[39: 49], keys[49:]
    write_programs(bc_files, train, out_dir / 'train')
    write_programs(bc_files, val, out_dir / 'val')
    write_programs(bc_files, test, out_dir / 'test')


if __name__ == '__main__':
    main()
