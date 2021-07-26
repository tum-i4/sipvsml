import argparse
import json
import pathlib

import pandas as pd


def parse_args():
    parser = argparse.ArgumentParser(description='Generate plots from model training results binaries')
    parser.add_argument('labeled_bc_dir', help='Directory where labeled binaries are stored')
    args = parser.parse_args()
    return args


def find_results_json_files(path):
    if path.is_file():
        if path.name.endswith('results.json'):
            with open(path) as inp:
                yield json.load(inp)
    else:
        for child in path.iterdir():
            yield from find_results_json_files(child)


def reconcile_results_into_dataframe(results_list):
    data = []
    for res_data in results_list:
        obfuscation = res_data['data_dir']\
            .replace('sbb-', '')\
            .replace('sbb', '')\
            .replace('-', '+')\
            .replace('FLAs', 'CFF')\
            .replace('BCF', 'BC')\
            .replace('SUB', 'IS')
        data.append({
            'data_source': res_data['data_source'],
            'obfuscation': obfuscation,
            'features': ' + '.join(res_data['features']),
            **res_data['results']['classifier']
        })
    return pd.DataFrame(data)


def main():
    args = parse_args()
    labeled_bc_dir = pathlib.Path(args.labeled_bc_dir)
    result_files = find_results_json_files(labeled_bc_dir)
    res = list(result_files)
    df = reconcile_results_into_dataframe(res)
    print(df)


if __name__ == '__main__':
    main()
