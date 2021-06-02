import pandas as pd


def write_blocks_df(blocks_file_path, updated_block_df):
    file_format = blocks_file_path.suffix
    if file_format == '.csv':
        updated_block_df.reset_index().to_csv(
            blocks_file_path,
            line_terminator='\r',
            sep=';',
            index=False
        )
    elif file_format == '.feather':
        updated_block_df.reset_index().to_feather(blocks_file_path)
    else:
        raise RuntimeError(f'Unknown file_format: {file_format}')


def write_relations_df(relations_file_path, relations_df):
    file_format = relations_file_path.suffix
    if file_format == '.csv':
        relations_df.to_csv(
            relations_file_path,
            index_col=False,
            sep=';',
            header=None,
            names=['source', 'target', 'label'],
            dtype={'source': object, 'target': object},
        )
    elif file_format == '.feather':
        relations_df.to_feather(relations_file_path)
    else:
        raise RuntimeError(f'Unknown file_format: {file_format}')


def get_default_block_columns():
    feature_names = [f'w_{i}' for i in range(64)]
    return ['uid'] + feature_names + ['program', 'subject']


def read_blocks_df(blocks_file_path):
    file_format = blocks_file_path.suffix
    if file_format == '.csv':
        header = get_block_file_header(blocks_file_path)
        blocks_df = pd.read_csv(
            blocks_file_path,
            lineterminator='\r',
            sep=';',
            header=None if header is None else 'infer',
            index_col=False,
            dtype={'uid': object},
            names=get_default_block_columns() if header is None else None
        )
        blocks_df.set_index('uid', inplace=True)
    elif file_format == '.feather':
        blocks_df = pd.read_feather(blocks_file_path)
    else:
        raise RuntimeError(f'Unknown file_format: {file_format}')
    return blocks_df


def read_relations_df(relations_file_path):
    file_format = relations_file_path.suffix
    if file_format == '.csv':
        return pd.read_csv(
            relations_file_path,
            index_col=False,
            sep=';',
            header=None,
            names=['source', 'target', 'label'],
            dtype={'source': object, 'target': object},
        )
    elif file_format == '.feather':
        return pd.read_feather(relations_file_path)
    else:
        raise RuntimeError(f'Unknown file_format: {file_format}')


def get_files_from_bc_dir(labeled_bc_dir, file_name='blocks.csv'):
    for sub_folder in labeled_bc_dir.iterdir():
        for data_dir in (labeled_bc_dir / sub_folder).iterdir():
            yield data_dir / file_name


def get_block_file_header(blocks_file_path):
    with open(blocks_file_path) as inp:
        first_line = inp.readline().strip()
        if first_line.startswith('uid'):
            return first_line.split(';')
        return None
