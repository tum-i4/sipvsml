import argparse
import multiprocessing
import os
import pathlib
import traceback
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

from tqdm import tqdm

from sip_ml_pipeline.model_training.train_model import __file__ as __train_model_file__
from sip_ml_pipeline.utils import write_json, get_obfuscation_dirs


def parse_args():
    parser = argparse.ArgumentParser(description='Train One ML model per obfuscation for attacking SIP')
    parser.add_argument('labeled_bc_dir', help='Directory where feature files are stored')
    parser.add_argument(
        '--model', choices=['graph_sage'], help='Which model to use', default='graph_sage'
    )
    parser.add_argument(
        '--use_features', type=str, nargs='+', choices=['ir2vec', 'pdg', 'tf_idf', 'code2vec'],
        help='Names of the features to use', required=True
    )
    parser.add_argument(
        '--num_processes', type=int, help='Number of parallel processes to start for model training',
        default=multiprocessing.cpu_count()
    )
    parser.add_argument(
        '--run_parallel_data_experiment', type=bool, default=False,
        help='Train the dataset on mibench-cov and evaluate on simple-cov2'
    )
    args = parser.parse_args()
    return args


def run_train_in_subprocess(train_ds, val_ds, features, model_name, results_file_name, p_bar):
    try:
        cmd = [
            'python',
            str(pathlib.Path(__train_model_file__).absolute()),
            str(train_ds),
            '--model', model_name,
            '--use_features', *features,
            '--results_file_name', results_file_name
        ]

        if val_ds is not None:
            log_file = f'{val_ds / "training.log"}'
            cmd.append('--val_features_data_dir')
            cmd.append(str(val_ds))
        else:
            log_file = f'{train_ds / "training.log"}'

        os.system(' '.join(cmd) + ' > ' + log_file)
    except Exception:
        traceback.print_exc()
    finally:
        p_bar.update(1)


def run_train_parallel(dataset, features, model_name, results_file_name, num_processes):
    sub_datasets = list(dataset)
    with tqdm(total=len(sub_datasets), desc='Training parallel models') as p_bar:
        with ThreadPoolExecutor(num_processes) as thread_pool:
            for train_ds, val_ds in sub_datasets:
                # thread_pool.submit(
                #     run_train_in_subprocess, train_ds, val_ds, features, model_name, results_file_name, p_bar
                # )
                run_train_in_subprocess(train_ds, val_ds, features, model_name, results_file_name, p_bar)


def get_dataset(labeled_bc_dir, run_parallel_experiment):
    if run_parallel_experiment:
        train_obfs_dirs = get_obfuscation_dirs(labeled_bc_dir, 'mibench-cov')
        for data_dir in train_obfs_dirs:
            yield data_dir, labeled_bc_dir / 'simple-cov2' / data_dir.name
    else:
        for data_dir in get_obfuscation_dirs(labeled_bc_dir):
            yield data_dir, None


def run(labeled_bc_dir, model_name, features, results_file_name, num_processes, run_parallel_experiment=False):
    start_time = datetime.now()
    dataset = get_dataset(labeled_bc_dir, run_parallel_experiment)
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
    num_processes = args.num_processes
    results_file_name = f"{'_'.join(features)}_results.json"

    if args.run_parallel_data_experiment:
        results_file_name = f'parallel_{results_file_name}'

    run(data_dir, model_name, features, results_file_name, num_processes, args.run_parallel_data_experiment)


if __name__ == '__main__':
    main()
