import argparse
import json
import pathlib
from collections import Counter

import pandas as pd


def parse_args():
    parser = argparse.ArgumentParser(description='Generate plots from model training results binaries')
    parser.add_argument('labeled_bc_dir', help='Directory where labeled binaries are stored')
    args = parser.parse_args()
    return args


def find_results_json_files(path, filter_fn=None):
    if path.is_file():
        if path.name.endswith('results.json') and (filter_fn is None or filter_fn(path)):
            with open(path) as inp:
                yield json.load(inp)
    else:
        for child in path.iterdir():
            yield from find_results_json_files(child, filter_fn)


def get_obfs_label_from_data_dir(data_dir):
    return data_dir \
        .replace('sbb-', '') \
        .replace('sbb', '') \
        .replace('-', '+') \
        .replace('FLAs', 'CFF') \
        .replace('BCF', 'BC') \
        .replace('SUB', 'IS')


def reconcile_results_into_dataframe(results_list):
    data = []
    for res_data in results_list:
        obfuscation = get_obfs_label_from_data_dir(res_data['data_dir'])
        data.append({
            'data_source': res_data['data_source'],
            'obfuscation': obfuscation,
            'features': ' + '.join(res_data['features']),
            **res_data['results']['classifier']
        })
    return pd.DataFrame(data)


def get_protected_dirs(labeled_bc_dir):
    for src_data_dir in labeled_bc_dir.iterdir():
        for obfs_dir in src_data_dir.iterdir():
            yield obfs_dir


def count_lines(file_path):
    with open(file_path) as inp:
        return len(inp.readlines())


def get_label_stats(sip_labels_file_path):
    counter = Counter()
    with open(sip_labels_file_path) as inp:
        for line in map(str.strip, inp):
            label = line.split('\t')[-1]
            counter[label] += 1
    return counter


def get_obfuscation_stats(labeled_bc_dir):
    data = []
    for obfs_dir in get_protected_dirs(labeled_bc_dir):
        ll_files = [file for file in obfs_dir.iterdir() if file.suffix == '.ll']
        for file in ll_files:
            protection = file.name.split('-')[1:][0]
            if protection not in ('CFI', 'OH', 'SC'):
                protection = 'NONE'

            label_stats = get_label_stats(file.with_suffix('.sip_labels'))
            data.append({
                'file': file,
                'src_dataset': file.parts[-3],
                'obfs': get_obfs_label_from_data_dir(obfs_dir.name),
                'protection': protection,
                'num_lines': count_lines(file),
                'num_blocks': sum(label_stats.values()),
                'protection_blocks': sum([v for k, v in label_stats.items() if k != 'none'])
            })
    df = pd.DataFrame(data)
    stats = df[df['protection'] == 'NONE'] \
        .groupby(['obfs']) \
        .agg({'num_blocks': 'sum', 'num_lines': 'sum', 'file': 'count'}) \
        .reset_index().sort_values(['obfs'], ascending=False)

    stats['avg_ir_lines'] = stats['num_lines'] / stats['file']

    no_obfs_avg_lines = float(stats[stats['obfs'] == 'NONE']['avg_ir_lines'])

    stats['avg_ir_lines_increase'] = (stats['avg_ir_lines'] / no_obfs_avg_lines - 1.0) * 100
    stats.sort_values('avg_ir_lines', inplace=True)

    stats = stats[['obfs', 'num_blocks', 'avg_ir_lines', 'avg_ir_lines_increase']]
    # stats = stats[stats['obfs'].map(lambda x: '-' not in x)]
    stats.columns = ['Obfuscation', 'Blocks', 'Avg IR Lines / Program', 'Avg % IR Lines Incr.']
    return stats


def main():
    args = parse_args()
    labeled_bc_dir = pathlib.Path(args.labeled_bc_dir)
    result_files = find_results_json_files(labeled_bc_dir)
    res = list(result_files)
    df = reconcile_results_into_dataframe(res)
    print(df)


if __name__ == '__main__':
    main()
