import argparse
import pathlib
import shutil
import traceback
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pandas as pd
from tqdm import tqdm

from ir_line_parser import get_instruction_embedding, read_vocab


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('path_to_vocabulary')
    parser.add_argument('labeled_bc_dir')
    return parser.parse_args()


def get_all_block_files(labeled_bc_dir):
    for sub_folder in ['simple-cov', 'mibench-cov']:
        for data_dir in (labeled_bc_dir / sub_folder).iterdir():
            yield data_dir / 'blocks.csv'


def get_ir_block_embedding(ir_block_str, vocab):
    cleaned_irs = [x.strip() for x in ir_block_str.strip().split('|.|') if x.strip() != '']
    embeddings = np.array([get_instruction_embedding(ir, vocab) for ir in cleaned_irs])
    return embeddings.sum(axis=0)


def read_blocks_df(blocks_file_path):
    feature_names = ["w_{}".format(ii) for ii in range(64)]
    column_names = ['uid'] + feature_names + ["program"] + ["subject"]
    blocks_df = pd.read_csv(
        blocks_file_path,
        lineterminator='\r',
        sep=';',
        header=None,
        index_col=False,
        dtype={'uid': object},
        names=column_names
    )
    blocks_df.set_index('uid', inplace=True)
    return blocks_df


def get_new_df(embeddings):
    data = []
    embedding_size = len(embeddings[0])
    for index, embedding in embeddings.items():
        row = {f'w_{i + 64}': num for i, num in zip(range(embedding_size), embedding)}
        row['uid'] = index
        data.append(row)
    new_df = pd.DataFrame(data).set_index('uid')
    return new_df


def write_new_df(blocks_file_path, new_blocks_df):
    new_blocks_df.reset_index().to_csv(
        blocks_file_path,
        line_terminator='\r',
        sep=';',
        header=False,
        index=False
    )


def save_old_file(blocks_file_path, saved_blocks_file_path):
    shutil.move(blocks_file_path, saved_blocks_file_path)


def process_df(args):
    try:
        blocks_file_path, saved_blocks_file_path, vocab = args
        blocks_df = read_blocks_df(blocks_file_path)
        embeddings = blocks_df['w_63'].map(lambda x: get_ir_block_embedding(x, vocab))
        new_df = get_new_df(embeddings)
        new_blocks_df = pd.concat([blocks_df, new_df], axis=1)
        del embeddings
        save_old_file(blocks_file_path, saved_blocks_file_path)
        write_new_df(blocks_file_path, new_blocks_df)
        return True
    except Exception:
        traceback.print_exc()


def get_processing_args(all_block_files, vocab):
    args = []
    for blocks_file_path in all_block_files:
        saved_blocks_file_path = blocks_file_path.with_name('blocks.csv.saved')
        if not blocks_file_path.exists():
            if saved_blocks_file_path.exists():
                shutil.move(saved_blocks_file_path, blocks_file_path)
        else:
            if saved_blocks_file_path.exists():
                continue
        args.append([blocks_file_path, saved_blocks_file_path, vocab])
    return args


def main():
    args = parse_args()
    all_block_files = list(get_all_block_files(pathlib.Path(args.labeled_bc_dir)))
    vocab = read_vocab(args.path_to_vocabulary)
    with ProcessPoolExecutor(max_workers=6) as pool:
        args = get_processing_args(all_block_files, vocab)
        print(sum(list(tqdm(pool.map(process_df, args)))))


if __name__ == '__main__':
    main()
