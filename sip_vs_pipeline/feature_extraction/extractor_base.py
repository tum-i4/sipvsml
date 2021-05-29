class FeatureExtractor:
    def __init__(self, name, rewrite=False) -> None:
        super().__init__()
        self.name = name
        self.rewrite = rewrite

    def __repr__(self) -> str:
        return f'{self.name}_extractor'

    def extract(self, binaries_dir, blocks_df):
        features_csv_path = binaries_dir / f'{self.name}.features.csv'
        if features_csv_path.exists() and not self.rewrite:
            return blocks_df
        features_df = self._extract_features(blocks_df, features_csv_path)
        features_df.reset_index().to_csv(
            features_csv_path,
            index=False,
            header=False
        )
        return blocks_df

    def _extract_features(self, blocks_df, features_output_csv_path):
        raise NotImplementedError


class CompositeExtractor(FeatureExtractor):
    def __init__(self, name: str, *extractors: FeatureExtractor, rewrite=False) -> None:
        super().__init__(name, rewrite)
        self._extractors = extractors

    def _extract_features(self, blocks_df, features_output_csv_path):
        for extractor in self._extractors:
            blocks_df = extractor.extract(blocks_df, features_output_csv_path.parent)
        return blocks_df
