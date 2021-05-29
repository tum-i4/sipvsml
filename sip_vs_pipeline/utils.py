import pandas as pd


def write_blocks_df(blocks_file_path, updated_block_df):
    updated_block_df.reset_index().to_csv(
        blocks_file_path,
        line_terminator='\r',
        sep=';',
        index=False
    )


def get_default_block_columns():
    feature_names = [f'w_{i}' for i in range(64)]
    return ['uid'] + feature_names + ['program', 'subject']


def read_blocks_df(blocks_file_path):
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
    return blocks_df


def get_all_block_files(labeled_bc_dir):
    for sub_folder in ['simple-cov', 'mibench-cov']:
        for data_dir in (labeled_bc_dir / sub_folder).iterdir():
            yield data_dir / 'blocks.csv'


def get_block_file_header(blocks_file_path):
    with open(blocks_file_path) as inp:
        first_line = inp.readline().strip()
        if first_line.startswith('uid'):
            return first_line.split(';')
        return None
