import pandas as pd

from sip_vs_pipeline.utils import read_blocks_df, read_relations_df


def get_data_csv_files(labeled_bc_dir, csv_file_name):
    for sub_folder in labeled_bc_dir.iterdir():
        for data_dir in sub_folder.iterdir():
            yield data_dir / csv_file_name


class SIPDataSet:
    def __init__(self, features_to_use, labeled_bc_dir, target_feature_name='subject') -> None:
        super().__init__()
        self._features_to_use = features_to_use
        self._labeled_bc_dir = labeled_bc_dir
        self.target_feature_name = target_feature_name

    def iter_sub_datasets(self, combine_features=True):
        for sub_folder in self._labeled_bc_dir.iterdir():
            for data_dir in (self._labeled_bc_dir / sub_folder).iterdir():
                block_csv_file_path = data_dir / 'blocks.csv'
                relations_file_path = data_dir / 'relations.csv'
                blocks_df = read_blocks_df(block_csv_file_path)[[self.target_feature_name]]
                relations_df = read_relations_df(relations_file_path)
                yield {
                    'data_source': sub_folder,
                    'data_dir': data_dir,
                    'blocks_df': blocks_df,
                    'relations_df': relations_df,
                    'features': self._read_features(data_dir, combine_features)
                }

    def _read_features(self, data_dir, combine_features):
        res = {}
        for feature_name in self._features_to_use:
            if feature_name == 'ir2vec':
                res[feature_name] = self._read_ir2vec_features(data_dir)
            elif feature_name == 'seg':
                res[feature_name] = self._read_graph_features(data_dir)
            elif feature_name == 'tf_idf':
                res[feature_name] = self._read_tf_idf_features(data_dir)
            else:
                raise RuntimeError(f'Unknown features {feature_name}')
        if combine_features:
            return self._combine_features(res)
        return res

    def _read_ir2vec_features(self, data_dir):
        return self._read_features_csv_file(data_dir / 'ir2vec.features.csv')

    def _read_graph_features(self, data_dir):
        return self._read_features_csv_file(data_dir / 'seg.features.csv')

    def _read_tf_idf_features(self, data_dir):
        return self._read_features_csv_file(data_dir / 'tf_idf.features.csv')

    def _read_features_csv_file(self, file_path):
        df = pd.read_csv(file_path, header=None, dtype={0: object}).set_index(0)
        df.index.rename('uid', inplace=True)
        return df

    def _combine_features(self, features_dict):
        return pd.concat(features_dict.values(), axis=1)
