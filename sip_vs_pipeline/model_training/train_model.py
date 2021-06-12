import argparse
import pathlib

from sip_vs_pipeline.model_training.data_reader import SIPSingleObfuscationDataset
from sip_vs_pipeline.model_training.graph_sage import GraphSageSIPLocalizer
from sip_vs_pipeline.utils import write_json


def parse_args():
    parser = argparse.ArgumentParser(description='Train ML model for attacking SIP')
    parser.add_argument('features_data_dir', help='Directory where feature files are stored')
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


def run_train(data_dict, model_name, results_file_name, target_feature_name):
    results_path = data_dict['data_dir'] / results_file_name
    if results_path.exists():
        print(f'{results_path} already exists, exiting...')
        return
    model = create_model(model_name)
    results_data = model.train(data_dict, target_feature_name)
    write_json(results_data, results_path)


def run(features_data_dir, model_name, features, results_file_name):
    dataset = SIPSingleObfuscationDataset(features_data_dir, features)
    target_feature_name = dataset.target_feature_name
    run_train(dataset.get_data_dict(), model_name, results_file_name, target_feature_name)


def main():
    args = parse_args()
    data_dir = pathlib.Path(args.features_data_dir)
    model_name = args.model
    features = args.use_features
    results_file_name = args.results_file_name
    run(data_dir, model_name, features, results_file_name)


if __name__ == '__main__':
    main()
