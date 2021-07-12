import subprocess

import pandas as pd

from sip_vs_pipeline.feature_extraction.extractor_base import FeatureExtractor
from sip_vs_pipeline.utils import read_blocks_df, read_json, get_program_name_from_filename


class Code2VecExtractor(FeatureExtractor):
    def __init__(self, name, code2vec_path, rewrite=False) -> None:
        super().__init__(name, rewrite)
        self.code2vec_path = code2vec_path
        self._model_path = None

    def extract(self, train_dir, val_dir):
        fold_dir = train_dir.parent
        model_dir = fold_dir / 'code2vec_llir_model'
        if not model_dir.exists():
            self._train_code2vec_model(fold_dir, train_dir, val_dir, model_dir)
        cmd = [
            'python', str(self.code2vec_path / 'code2vec.py'),
            '--load', model_dir / 'saved_model_iter1',
            '--framework', 'tensorflow',
            '--export_code_vectors',
            '--test', str(fold_dir / 'code2vec_llir.val.c2v')
        ]
        # TODO compress and return features dataframe
        print(' '.join(cmd))

    def _generate_histogram_files(self, fold_dir, train_dir, val_dir):
        train_data_file = fold_dir / 'code2vec_llir.train.raw.txt'
        self._collect_raw_c2v_files(train_dir, train_data_file)

        val_data_file = fold_dir / 'code2vec_llir.val.raw.txt'
        self._collect_raw_c2v_files(val_dir, val_data_file)

        cmd = [str(self.code2vec_path / 'preprocess_llir_sip_vs_ml.sh'), str(fold_dir)]
        subprocess.check_call(cmd, cwd=str(self.code2vec_path.absolute()))
        return fold_dir / 'code2vec_llir.train.c2v', fold_dir / 'code2vec_llir.val.c2v'

    def _extract_features(self, binaries_dir):
        blocks_df = read_blocks_df(binaries_dir / 'blocks.csv.gz')
        bc_paths = [x for x in binaries_dir.iterdir() if x.suffix == '.bc']

        features = []
        all_block_uids = set(blocks_df.index)
        for bc_path in bc_paths:
            code2vec_vectors_path = self._extract_code2vec_vectors(bc_path)
            df = self._read_feature_vectors(bc_path, code2vec_vectors_path)
            assert len(set(df[0]) & all_block_uids) > 0
            features.append(df)
        return pd.concat(features)

    def _extract_code2vec_vectors(self, bc_path):
        code2vec_vectors = bc_path.parent / f'{bc_path.name.split(".")[0]}.c2v_vec'
        if not code2vec_vectors.exists() or self.rewrite:
            c2v_file_path = self._generate_c2v_file(bc_path)
            cmd = [
                'python',
                str(self.code2vec_path / 'code2vec.py'),
                '--load',
                str(self._model_path),
                '--framework',
                'tensorflow',
                '--export_code_vectors',
                '--test',
                str(c2v_file_path)
            ]
            subprocess.check_call(cmd)
        return code2vec_vectors

    def _read_feature_vectors(self, bc_file_path, code2vec_vectors_path):
        code2vec_vectors = []
        with open(code2vec_vectors_path) as inp:
            for line in inp:
                code2vec_vectors.append([float(x) for x in line.split()])

        with open(bc_file_path.with_suffix('.sip_labels')) as inp:
            llvm_pass_labels = inp.readlines()

        assert len(code2vec_vectors) == len(llvm_pass_labels)

        features = []
        for feature_vector, llvm_pass_line in zip(code2vec_vectors, llvm_pass_labels):
            block_name, block_uid, *_ = llvm_pass_line.split('\t')
            features.append([block_uid] + feature_vector)
        return pd.DataFrame(features)

    def _train_code2vec_model(self, fold_dir, train_dir, val_dir, model_dir):
        self._generate_histogram_files(fold_dir, train_dir, val_dir)

        cmd = [
            'python', str(self.code2vec_path / 'code2vec.py'),
            '--data', str(fold_dir / 'code2vec_llir'),
            '--save', str(model_dir),
            '--framework', 'tensorflow'
        ]
        output = subprocess.check_output(cmd)
        # return model_dir

    @staticmethod
    def _collect_raw_c2v_files(data_dir, train_data_file):
        program_names = read_json(data_dir / 'programs.json')
        input_files = [
            file for file in data_dir.parent.parent.parent.iterdir()
            if file.name.endswith('raw_c2v') and get_program_name_from_filename(file.name) in program_names
        ]
        with open(train_data_file, 'w') as out:
            for file in input_files:
                with open(file) as inp:
                    assert out.write(inp.read()) > 0
                    out.write('\n')
