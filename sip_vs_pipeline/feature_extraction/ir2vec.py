import json

import numpy as np
import pandas as pd

from sip_vs_pipeline.feature_extraction.extractor_base import FeatureExtractor


class IR2VecExtractor(FeatureExtractor):
    def __init__(self, name, vocab_path, rewrite=False, ir_delimiter='|.|', w0=1.0, wt=0.5, wa=0.25) -> None:
        super().__init__(name, rewrite)
        self.vocab_path = vocab_path
        self.ir_delimiter = ir_delimiter
        self.vocab = self._read_vocab()
        self.w0 = w0
        self.wt = wt
        self.wa = wa

    def _extract_features(self, blocks_df):
        generalized_blocks = blocks_df['generalized_block']
        embeddings = generalized_blocks.map(self._get_block_embedding)
        df = pd.DataFrame(embeddings.tolist(), index=embeddings.index)
        return df

    def _get_block_embedding(self, gen_block):
        irs = gen_block.split(self.ir_delimiter)
        embeddings = np.array([self._get_ir_embedding(ir) for ir in irs])
        return embeddings.sum(axis=0)

    def _get_ir_embedding(self, ir):
        words = ir.split('  ')
        cmd, tp, *args = map(lambda word: np.array(self.vocab[word]), words)
        return self.w0 * cmd + self.wt * tp + (np.array(args) * self.wa).sum(axis=0)

    def _read_vocab(self):
        with open(self.vocab_path) as inp:
            res = {}
            for line in map(str.strip, inp):
                if line != '':
                    key, val = line.split(':')
                    res[key] = np.array(json.loads(val.strip(',')))
            return res
