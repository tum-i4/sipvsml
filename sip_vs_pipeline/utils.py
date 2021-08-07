import json
import os
import pathlib

import pandas as pd

CODE2VEC_REPOSITORY_PATH = pathlib.Path(os.getenv('CODE2VEC_REPOSITORY_PATH', '/home/nika/Desktop/Thesis/code2vec'))
LLVM_MODULE_LABELLING_PASS_SO_PATH = CODE2VEC_REPOSITORY_PATH / 'LLIRExtractor' / \
                                     'llvm_labelling_pass' / 'build' / 'libModuleLabelling.so'


def write_blocks_df(blocks_file_path, updated_block_df, **kwargs):
    updated_block_df.reset_index().to_csv(
        blocks_file_path,
        index=False,
        **kwargs
    )


def write_relations_df(relations_file_path, relations_df, **kwargs):
    relations_df.to_csv(
        relations_file_path,
        index=False,
        **kwargs
    )


def read_blocks_df(blocks_file_path, **kwargs):
    blocks_df = pd.read_csv(
        blocks_file_path,
        index_col=False,
        dtype={'uid': object},
        **kwargs
    )
    blocks_df.set_index('uid', inplace=True)
    return blocks_df


def read_relations_df(relations_file_path, **kwargs):
    return pd.read_csv(
        relations_file_path,
        index_col=False,
        dtype={'source': object, 'target': object},
        **kwargs
    )


def get_files_from_bc_dir(labeled_bc_dir, file_name='blocks.csv'):
    for sub_folder in labeled_bc_dir.iterdir():
        for data_dir in (labeled_bc_dir / sub_folder).iterdir():
            yield data_dir / file_name


def get_protected_bc_dirs(labeled_bc_dir, dataset=None):
    datasets = [labeled_bc_dir / dataset] if dataset is not None else labeled_bc_dir.iterdir()
    for sub_folder in datasets:
        for data_dir in sub_folder.iterdir():
            yield data_dir


def get_fold_dirs(labeled_bc_dir, dataset=None):
    datasets = [labeled_bc_dir / dataset] if dataset is not None else labeled_bc_dir.iterdir()
    for sub_folder in datasets:
        for data_dir in sub_folder.iterdir():
            for sub_dir in (data_dir / 'folds').iterdir():
                if sub_dir.name.startswith('k_fold_'):
                    yield sub_dir


def write_json(training_res, training_results_path):
    with open(training_results_path, 'w', encoding='utf-8') as out:
        json.dump(training_res, out, ensure_ascii=False, indent=4)


def read_json(json_path):
    with open(json_path) as inp:
        return json.load(inp)


def blocks_for_fold(split_fold_path):
    json_path = split_fold_path / 'programs.json'
    split_programs = read_json(json_path)

    data_path = pathlib.Path('/'.join(split_fold_path.parts[:split_fold_path.parts.index('folds')]))
    blocks_df = read_blocks_df(data_path / 'blocks.csv.gz')
    return blocks_df[blocks_df['program'].map(get_program_name_from_filename).isin(split_programs)]


def get_program_name_from_filename(file_name):
    return file_name.split('-')[0].split('.')[0]
