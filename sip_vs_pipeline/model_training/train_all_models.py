import argparse
import multiprocessing
import os
import pathlib
import traceback
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

from tqdm import tqdm

from sip_vs_pipeline.model_training.data_reader import SIPDataSet
from sip_vs_pipeline.utils import write_json


def parse_args():
    parser = argparse.ArgumentParser(description='Train One ML model per obfuscation for attacking SIP')
    parser.add_argument('labeled_bc_dir', help='Directory where feature files are stored')
    parser.add_argument(
        '--model', choices=['graph_sage'], help='Which model to use', default='graph_sage'
    )
    parser.add_argument(
        '--use_features', type=str, nargs='+', choices=['ir2vec', 'seg', 'tf_idf'],
        help='Names of the features to use', required=True
    )
    parser.add_argument(
        '--results_file_name', type=str, required=True,
        help='Names for the results file (graph_sage model creates one per obfuscation)'
    )
    parser.add_argument(
        '--num_processes', type=int, help='Number of parallel processes to start for model training',
        default=multiprocessing.cpu_count()
    )
    args = parser.parse_args()
    return args


def run_train_in_subprocess(sub_dataset, features, model_name, results_file_name, p_bar):
    try:
        cmd = [
            'python',
            'train_model.py',
            str(sub_dataset.data_dir),
            '--model', model_name,
            '--use_features', *features,
            '--results_file_name', results_file_name
        ]
        os.system(' '.join(cmd) + ' > ' + f'{sub_dataset.data_dir / "training.log"}')
    except:
        traceback.print_exc()
    finally:
        p_bar.update(1)


def run_train_parallel(dataset, features, model_name, results_file_name, num_processes):
    sub_datasets = list(dataset.iter_sub_datasets())
    with tqdm(total=len(sub_datasets), desc='Training parallel models') as p_bar:
        with ThreadPoolExecutor(num_processes) as thread_pool:
            for ds in sub_datasets:
                thread_pool.submit(
                    run_train_in_subprocess, ds, features, model_name, results_file_name, p_bar
                )


def run(labeled_bc_dir, model_name, features, results_file_name, num_processes):
    dataset = SIPDataSet(labeled_bc_dir, features)
    start_time = datetime.now()

    run_train_parallel(dataset, features, model_name, results_file_name, num_processes)

    elapsed = datetime.now() - start_time
    training_results_path = f"training_run_{start_time.strftime('%Y-%M-%d_%H-%m-%S')}.json"
    write_json({
        'datetime': start_time.isoformat(),
        'labeled_bc_dir': str(labeled_bc_dir),
        'model_name': model_name,
        'features': features,
        'training_time_seconds': elapsed.total_seconds(),
        'results_file_name': results_file_name
    }, training_results_path)


def main():
    args = parse_args()
    data_dir = pathlib.Path(args.labeled_bc_dir)
    model_name = args.model
    features = args.use_features
    results_file_name = args.results_file_name
    num_processes = args.num_processes
    run(data_dir, model_name, features, results_file_name, num_processes)


if __name__ == '__main__':
    main()
