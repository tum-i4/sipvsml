import argparse
import pathlib
from datetime import datetime

from sip_vs_pipeline.model_training.data_reader import SIPDataSet
from sip_vs_pipeline.model_training.graph_sage import GraphSageSIPLocalizer
from sip_vs_pipeline.utils import write_json


def parse_args():
    parser = argparse.ArgumentParser(description='Train ML models for attacking SIP')
    parser.add_argument('labeled_bc_dir', help='Directory where labeled binaries are stored')
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
    args = parser.parse_args()
    return args


def create_model(model_name):
    if model_name == 'graph_sage':
        return GraphSageSIPLocalizer()
    raise RuntimeError(f'Unknown model {model_name}')


def run(labeled_bc_dir, model_name, features, results_file_name):
    dataset = SIPDataSet(features, labeled_bc_dir)
    start_time = datetime.now()

    target_feature_name = dataset.target_feature_name
    for data_dict in dataset.iter_sub_datasets():
        results_path = data_dict['data_dir'] / results_file_name
        if results_path.exists():
            print(f'{results_path} already exists, exiting...')

        model = create_model(model_name)
        results_data = model.train(data_dict, target_feature_name)
        write_json(results_data, results_path)

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
    labeled_bc_dir = pathlib.Path(args.labeled_bc_dir)
    model_name = args.model
    features = args.use_features
    results_file_name = args.results_file_name
    run(labeled_bc_dir, model_name, features, results_file_name)


if __name__ == '__main__':
    main()
