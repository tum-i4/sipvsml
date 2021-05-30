import argparse
import json
import pathlib
from datetime import datetime

from sip_vs_pipeline.model_training.data_reader import SIPDataSet
from sip_vs_pipeline.model_training.graph_sage import GraphSageSIPLocalizer


def parse_args():
    parser = argparse.ArgumentParser(description='Train ML models for attacking SIP')
    parser.add_argument('labeled_bc_dir', help='Directory where labeled binaries are stored')
    parser.add_argument(
        '--model', choices=['graph_sage'], help='Which model to use', default='graph_sage'
    )
    parser.add_argument(
        '--use_features', type=str, nargs='+', choices=['ir2vec', 'seg', 'tf_idf'],
        help='Name of the features to use', required=True
    )
    parser.add_argument(
        '--save_results_path', type=str, required=True,
        help='Path to the file where training results will be stored'
    )
    args = parser.parse_args()
    return args


def create_model(model_name):
    if model_name == 'graph_sage':
        return GraphSageSIPLocalizer()
    raise RuntimeError(f'Unknown model {model_name}')


def write_json(training_res, training_results_path):
    with open(training_results_path, 'w', encoding='utf-8') as out:
        json.dump(training_res, out, ensure_ascii=False, indent=4)


def run(labeled_bc_dir, model_name, features, training_results_path):
    if training_results_path.exists():
        print(f'{training_results_path} already exists, exiting...')
        return

    model = create_model(model_name)
    dataset = SIPDataSet(features, labeled_bc_dir)
    start_time = datetime.now()
    training_res = model.train(dataset)
    elapsed = datetime.now() - start_time
    write_json({
        'datetime': datetime.now().isoformat(),
        'labeled_bc_dir': str(labeled_bc_dir),
        'model_name': model_name,
        'features': features,
        'training_time_seconds': elapsed.total_seconds(),
        'training_res': training_res
    }, training_results_path)


def main():
    args = parse_args()
    labeled_bc_dir = pathlib.Path(args.labeled_bc_dir)
    model_name = args.model
    features = args.use_features
    training_results_path = pathlib.Path(args.save_results_path)
    run(labeled_bc_dir, model_name, features, training_results_path)


if __name__ == '__main__':
    main()
