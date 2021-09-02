from sip_ml_pipeline.utils import blocks_for_fold


class FeatureExtractor:
    def __init__(self, name, rewrite=False) -> None:
        super().__init__()
        self.name = name
        self.rewrite = rewrite

    def __repr__(self) -> str:
        return f'{self.name}_extractor'

    def extract(self, train_dir, val_dir):
        raise NotImplementedError


class CompositeExtractor(FeatureExtractor):
    def __init__(self, name: str, *extractors: FeatureExtractor, rewrite=False) -> None:
        super().__init__(name, rewrite)
        self._extractors = extractors

    def extract(self, *args, **kwargs):
        for extractor in self._extractors:
            extractor.extract(*args, **kwargs)


class BlockFeatureExtractor(FeatureExtractor):
    def extract(self, train_dir, val_dir):
        self._extract(train_dir)
        self._extract(val_dir)

    def _extract(self, bc_dir):
        features_csv_path = bc_dir / f'{self.name}.features.csv.gz'
        if features_csv_path.exists() and not self.rewrite:
            return

        blocks_df = blocks_for_fold(bc_dir)
        features_df = self.extract_using_blocks_df(blocks_df)
        features_df.reset_index().to_csv(
            features_csv_path,
            index=False,
            header=False
        )

    def extract_using_blocks_df(self, blocks_df):
        raise NotImplementedError
