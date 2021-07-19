import pandas as pd

from sip_vs_pipeline.utils import read_blocks_df, read_relations_df, blocks_for_fold


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
        self.data_dir = features_dir
        self.features_to_use = features_to_use
        self.target_feature_name = target_feature_name

    def iter_fold_data_dict(self):
        for fold_dir in (self.data_dir / 'folds').iterdir():
            if fold_dir.is_file():
                continue
            yield self._get_data_dict(fold_dir)

    def _get_data_dict(self, fold_dir, combine_features=True):
        return {
            'data_source': self.data_dir.parent,
            'data_dir':  self.data_dir,
            'fold_dir':  fold_dir,
            'train': self._get_sub_data_dir(fold_dir / 'train', combine_features),
            'val': self._get_sub_data_dir(fold_dir / 'val', combine_features),
        }

    def _get_sub_data_dir(self, features_dir, combine_features):
        relations_file_path = self.data_dir / 'relations.csv.gz'
        lazy_blocks_df = LazyVariable(lambda: blocks_for_fold(features_dir)[[self.target_feature_name]])
        lazy_relations_df = LazyVariable(lambda: read_relations_df(relations_file_path))
        lazy_features_df = LazyVariable(lambda: self._read_features(features_dir, combine_features))

        return {
            'blocks_df': lazy_blocks_df,
            'relations_df': lazy_relations_df,
            'features': lazy_features_df
        }

    def _read_features(self, data_dir, combine_features):
        res = {}
        for feature_name in self.features_to_use:
            if feature_name == 'ir2vec':
                res[feature_name] = self._read_ir2vec_features(data_dir)
            elif feature_name == 'seg':
                res[feature_name] = self._read_graph_features(data_dir)
            elif feature_name == 'tf_idf':
                res[feature_name] = self._read_tf_idf_features(data_dir)
            elif feature_name == 'code2vec':
                res[feature_name] = self._read_code2vec_features(data_dir)
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

    def _read_code2vec_features(self, data_dir):
        return self._read_features_csv_file(data_dir / 'code2vec.features.csv.gz')


class SIPDataSet:
    def __init__(self, labeled_bc_dir, features_to_use, target_feature_name='subject') -> None:
        super().__init__()
        self._labeled_bc_dir = labeled_bc_dir
        self._features_to_use = features_to_use
        self.target_feature_name = target_feature_name

    def iter_sub_datasets(self):
        for sub_folder in self._labeled_bc_dir.iterdir():
            for data_dir in (self._labeled_bc_dir / sub_folder).iterdir():
                dt = SIPSingleObfuscationDataset(
                    data_dir,
                    self._features_to_use,
                    self.target_feature_name,
                )
                yield dt
