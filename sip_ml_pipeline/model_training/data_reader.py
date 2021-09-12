import pandas as pd

from sip_ml_pipeline.utils import read_relations_df, blocks_for_fold


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

    def _get_sub_data_dir(self, fold_dir, combine_features):
        relations_file_path = self.data_dir / 'relations.csv.gz'
        lazy_blocks_df = LazyVariable(lambda: blocks_for_fold(fold_dir)[[self.target_feature_name]])
        lazy_relations_df = LazyVariable(lambda: read_relations_df(relations_file_path))
        lazy_features_df = LazyVariable(lambda: self._read_features(fold_dir, combine_features))

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
            elif feature_name == 'pdg':
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
        return self._read_features_csv_file(data_dir / 'pdg.features.csv.gz')

    def _read_tf_idf_features(self, data_dir):
        return self._read_features_csv_file(data_dir / 'tf_idf.features.csv.gz')

    def _read_code2vec_features(self, data_dir):
        return self._read_features_csv_file(data_dir / 'code2vec.features.csv.gz')

    def _read_features_csv_file(self, file_path):
        df = pd.read_csv(file_path, header=None, dtype={0: object}).set_index(0)
        df.index.rename('uid', inplace=True)
        return df

    def _combine_features(self, features_dict):
        df = pd.concat(features_dict.values(), axis=1)
        # some version of pandas seems to be dropping index name here
        df.index.rename('uid', inplace=True)
        return df


class SIPParallelDataset:
    def __init__(self, train_dataset, val_dataset) -> None:
        self.train_dataset = train_dataset
        self.val_dataset = val_dataset
        self.target_feature_name = train_dataset.target_feature_name
        self.features_to_use = train_dataset.features_to_use

    def iter_fold_data_dict(self):
        zipped_fold_data = zip(
            self.train_dataset.iter_fold_data_dict(),
            self.val_dataset.iter_fold_data_dict()
        )

        for train_fold_data, val_fold_data in zipped_fold_data:
            rel1 = train_fold_data['val']['relations_df']
            rel2 = val_fold_data['val']['relations_df']

            relation_df = LazyVariable(lambda: self.concat_lazy_dataframes(rel1, rel2))

            yield {
                'data_source': train_fold_data['data_source'],
                'data_dir': train_fold_data['data_dir'],
                'fold_dir': val_fold_data['fold_dir'],
                'train': {
                    'blocks_df': LazyVariable(lambda: self.concat_lazy_dataframes(
                        train_fold_data['train']['blocks_df'], val_fold_data['train']['blocks_df']
                    )),
                    'relations_df': relation_df,
                    'features': LazyVariable(lambda: self.concat_lazy_dataframes(
                        train_fold_data['train']['features'], val_fold_data['train']['features']
                    )),
                },
                'val': {
                    'blocks_df': val_fold_data['val']['blocks_df'],
                    'relations_df': relation_df,
                    'features': val_fold_data['val']['features']
                }
            }

    @staticmethod
    def concat_lazy_dataframes(df1, df2):
        return pd.concat([df1.get(), df2.get()], axis=0)

    def combine_train_and_val_features(self, fold_data, relations_df):
        return {
            'blocks_df': LazyVariable(lambda: self.concat_lazy_dataframes(
                fold_data['train']['blocks_df'], fold_data['val']['blocks_df']
            )),
            'relations_df': relations_df,
            'features': LazyVariable(lambda: self.concat_lazy_dataframes(
                fold_data['train']['features'], fold_data['val']['features']
            ))
        }
