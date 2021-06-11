import pandas as pd

from sip_vs_pipeline.utils import read_blocks_df, read_relations_df


def get_data_csv_files(labeled_bc_dir, csv_file_name):
    for sub_folder in labeled_bc_dir.iterdir():
        for data_dir in sub_folder.iterdir():
            yield data_dir / csv_file_name


class LazyVariable:
    def __init__(self, get_fn) -> None:
        super().__init__()
        self._get_fn = get_fn
        self._val = None

    def get(self):
        if self._val is None:
            self._val = self._get_fn()
        return self._val

    def __repr__(self) -> str:
        return f'LazyVariable {id(self)}'


class SIPSingleObfuscationDataset:
    def __init__(self, features_dir, features_to_use, target_feature_name='subject') -> None:
        super().__init__()
        self._features_to_use = features_to_use
        self._data_dir = features_dir
        self.target_feature_name = target_feature_name

    def get_data_dict(self, combine_features=True):
        block_csv_file_path = self._data_dir / 'blocks.csv.gz'
        relations_file_path = self._data_dir / 'relations.csv.gz'
        lazy_blocks_df = LazyVariable(lambda: read_blocks_df(block_csv_file_path)[[self.target_feature_name]])
        lazy_relations_df = LazyVariable(lambda: read_relations_df(relations_file_path))
        lazy_features_df = LazyVariable(lambda: self._read_features(self._data_dir, combine_features))
        return {
            'data_source': self._data_dir,
            'data_dir': self._data_dir,
            'blocks_df': lazy_blocks_df,
            'relations_df': lazy_relations_df,
            'features': lazy_features_df
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
        return self._read_features_csv_file(data_dir / 'ir2vec.features.csv.gz')

    def _read_graph_features(self, data_dir):
        return self._read_features_csv_file(data_dir / 'seg.features.csv.gz')

    def _read_tf_idf_features(self, data_dir):
        return self._read_features_csv_file(data_dir / 'tf_idf.features.csv.gz')

    def _read_features_csv_file(self, file_path):
        df = pd.read_csv(file_path, header=None, dtype={0: object}).set_index(0)
        df.index.rename('uid', inplace=True)
        return df

    def _combine_features(self, features_dict):
        return pd.concat(features_dict.values(), axis=1)


class SIPDataSet:
    def __init__(self, features_to_use, labeled_bc_dir, target_feature_name='subject') -> None:
        super().__init__()
        self._features_to_use = features_to_use
        self._labeled_bc_dir = labeled_bc_dir
        self.target_feature_name = target_feature_name

    def iter_sub_datasets(self, combine_features=True):
        for sub_folder in self._labeled_bc_dir.iterdir():
            for data_dir in (self._labeled_bc_dir / sub_folder).iterdir():
                dt = SIPSingleObfuscationDataset(self._features_to_use, data_dir, self.target_feature_name)
                yield dt.get_data_dict(combine_features)
