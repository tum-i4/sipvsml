import argparse
import pathlib
import pickle

import pandas as pd
from tqdm import tqdm

from extract_ml_features import get_all_block_files

pickle.HIGHEST_PROTOCOL = 4


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('labeled_bc_dir')
    return parser.parse_args()


def process_block_file(block_file_path):
    chunk_size = 975000000
    read_size = 0
    column_names = ['uid'] + ['w_{}'.format(ii) for ii in range(64)] + ['program', 'subject'] + \
                   ['w_{}'.format(64 + ii) for ii in range(300 + 200)]  # include tf-idf featues
    node_data = pd.read_csv(
        block_file_path, lineterminator='\r', sep=';', header=None,
        index_col=False, dtype={'uid': object}, names=column_names
    )
    node_data.set_index('uid', inplace=True)

    edges_path = pathlib.Path(str(block_file_path).replace('LABELED-BCs', 'RESULTS-ML')).with_name('edges.h5')

    store = pd.HDFStore(edges_path)
    relations_file_path = block_file_path.with_name('relations.csv')
    relations_df = pd.read_csv(
        relations_file_path, index_col=False, sep=';', header=None,
        names=["source", "target", "label"],
        dtype={'source': object, 'target': object}, chunksize=chunk_size
    )
    for chunk in relations_df:
        store.put('edges', chunk, format='t', append=True, data_columns=True)
        read_size = read_size + chunk_size
        print('Read node elements:', read_size)
    store.close()

    del node_data["w_63"]
    print('Writing to nodes.h5...')
    nodes_path = edges_path.with_name('nodes.h5')
    node_data.to_hdf(nodes_path, key='node_data', mode='w')
    print('Done, Bye!')


def main():
    args = parse_args()
    all_block_files = list(get_all_block_files(pathlib.Path(args.labeled_bc_dir)))
    for block_file_path in tqdm(all_block_files):
        process_block_file(block_file_path)


if __name__ == '__main__':
    main()
