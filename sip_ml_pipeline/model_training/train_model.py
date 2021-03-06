import argparse
import pathlib

from sip_ml_pipeline.model_training.data_reader import SIPSingleObfuscationDataset, SIPParallelDataset
from sip_ml_pipeline.model_training.graph_sage import GraphSageSIPLocalizer
from sip_ml_pipeline.utils import write_json


def parse_args():
    parser = argparse.ArgumentParser(description='Train ML model for attacking SIP')
    parser.add_argument('features_data_dir', help='Directory where feature files are stored')
    parser.add_argument(
        '--model', choices=['graph_sage'], help='Which model to use', default='graph_sage'
    )
    parser.add_argument(
        '--use_features', type=str, nargs='+', choices=['ir2vec', 'pdg', 'tf_idf', 'code2vec'],
        help='Names of the features to use', required=True
    )
    parser.add_argument(
        '--results_file_name', type=str, required=True,
        help='Names for the results file (graph_sage model creates one per obfuscation)'
    )
    parser.add_argument(
        '--val_features_data_dir', type=str, required=False,
        help='Separate dataset for validation, the results will be saved there. If this argument is passed, '
             'both <features_data_dir>/train and <features_data_dir>/val will be used for training.'
    )
    args = parser.parse_args()
    return args


def create_model(model_name):
    if model_name == 'graph_sage':
        return GraphSageSIPLocalizer()
    raise RuntimeError(f'Unknown model {model_name}')


def run_train(dataset, model_name, results_file_name, target_feature_name):
    for data_dict in dataset.iter_fold_data_dict():
        results_path = data_dict['fold_dir'] / results_file_name
        if results_path.exists():
            print(f'{results_path} already exists, moving on...')
            continue
        model = create_model(model_name)

        model_save_path = results_path.with_suffix('.model')
        results_data = model.train(data_dict, target_feature_name, model_save_path)
        results_data['features'] = dataset.features_to_use
        write_json(results_data, results_path)


def run(features_data_dir, val_features_data_dir, model_name, features, results_file_name):
    dataset = SIPSingleObfuscationDataset(features_data_dir, features)
    if val_features_data_dir is not None:
        dataset = SIPParallelDataset(
            dataset,
            SIPSingleObfuscationDataset(val_features_data_dir, features)
        )

    target_feature_name = dataset.target_feature_name
    run_train(dataset, model_name, results_file_name, target_feature_name)


def main():
    args = parse_args()
    data_dir = pathlib.Path(args.features_data_dir)
    model_name = args.model
    features = args.use_features
    results_file_name = args.results_file_name
    val_features_data_dir = None if args.val_features_data_dir is None else pathlib.Path(args.val_features_data_dir)
    run(data_dir, val_features_data_dir, model_name, features, results_file_name)


if __name__ == '__main__':
    main()
