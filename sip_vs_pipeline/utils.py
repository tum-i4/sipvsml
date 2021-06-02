import pandas as pd


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


def get_protected_bc_dirs(labeled_bc_dir):
    for sub_folder in labeled_bc_dir.iterdir():
        for data_dir in sub_folder.iterdir():
            yield data_dir
