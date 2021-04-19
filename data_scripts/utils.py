import argparse
import pathlib
import pickle
import shutil

import pandas as pd
from tqdm import tqdm

pickle.HIGHEST_PROTOCOL = 4


def get_input_files(results_dir):
    for dataset_dir in results_dir.iterdir():
        for category_dir in dataset_dir.iterdir():
            nodes_file_path = category_dir / 'nodes.h5'
            yield nodes_file_path


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('results_ml_dir')
    return parser.parse_args()


def update_df_with_fn(input_files, update_fn, save_old_files=True):
    for nodes_file_path in tqdm(input_files):
        df = pd.read_hdf(nodes_file_path, key='node_data')
        df = update_fn(df)
        if save_old_files:
            save_path = nodes_file_path.with_name('nodes.h5.saved')
            shutil.move(nodes_file_path, save_path)
        df.to_hdf(nodes_file_path, key='node_data', mode='w')


def run_with_update_fn(update_fn):
    args = parse_args()
    results_dir = pathlib.Path(args.results_ml_dir)
    input_files = list(get_input_files(results_dir))
    update_df_with_fn(input_files, update_fn)
