import argparse
import pathlib

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
    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    labeled_bc_dir = pathlib.Path(args.labeled_bc_dir)
    model_name = args.model
    features = args.use_features
    print(labeled_bc_dir, model_name, features)

    model = GraphSageSIPLocalizer()
    dataset = SIPDataSet(features, labeled_bc_dir)
    res = model.train(dataset)
    print(res)


if __name__ == '__main__':
    main()
