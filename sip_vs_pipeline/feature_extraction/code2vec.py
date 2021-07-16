import gzip
import os
import shutil
import subprocess

import pandas as pd

from sip_vs_pipeline.feature_extraction.extractor_base import FeatureExtractor
from sip_vs_pipeline.utils import read_json, get_program_name_from_filename, blocks_for_fold


def move_file(src_path, dst_path, block_size=1024*1024*8):
    with open(src_path, 'rb') as inp, open(dst_path, 'wb') as out:
        while True:
            block = inp.read(block_size)
            if len(block) == 0:
                break
            out.write(block)


class Code2VecExtractor(FeatureExtractor):
    def __init__(self, name, code2vec_path, rewrite=False) -> None:
        super().__init__(name, rewrite)
        self.code2vec_path = code2vec_path
        self._model_path = None

    def extract(self, train_dir, val_dir):
        train_features_path = train_dir / f'{self.name}.features.csv.gz'
        val_features_path = val_dir / f'{self.name}.features.csv.gz'
        if not self.rewrite and train_features_path.exists() and val_features_path.exists():
            return

        fold_dir = train_dir.parent
        model_dir = fold_dir / 'code2vec_llir_model'
        os.makedirs(model_dir, exist_ok=True)
        train_vectors_path, val_vectors_path = self._train_code2vec_model(fold_dir, model_dir)

        self._compress_and_write_features(
            train_dir, train_vectors_path, train_features_path
        )

        self._compress_and_write_features(
            val_dir, val_vectors_path, val_features_path
        )

        # cleanup
        shutil.rmtree(model_dir)
        for child in fold_dir.iterdir():
            if any([child.name.endswith(suffix) for suffix in ['.c2v', '.c2v.vectors', '.num_examples']]):
                child.unlink()

    def _generate_histogram_files(self, fold_dir):
        train_data_file = fold_dir / 'code2vec_llir.train.raw.txt'
        self._collect_raw_c2v_files(fold_dir / 'train', train_data_file)

        val_data_file = fold_dir / 'code2vec_llir.val.raw.txt'
        self._collect_raw_c2v_files(fold_dir / 'val', val_data_file)

        cmd = [str(self.code2vec_path / 'preprocess_llir_sip_vs_ml.sh'), str(fold_dir)]
        subprocess.check_call(cmd, cwd=str(self.code2vec_path.absolute()))
        return fold_dir / 'code2vec_llir.train.c2v', fold_dir / 'code2vec_llir.val.c2v'

    def _train_code2vec_model(self, fold_dir, model_dir):
        self._generate_histogram_files(fold_dir)

        cmd = [
            'python', str(self.code2vec_path / 'code2vec.py'),
            '--data', str(fold_dir / 'code2vec_llir'),
            '--test', str(fold_dir / 'code2vec_llir.val.c2v'),
            '--save', f'{model_dir}/',
            '--framework', 'tensorflow',
            '--export_code_vectors'
        ]
        output = subprocess.check_output(cmd, cwd=str(self.code2vec_path))
        with open(fold_dir / 'code2vec_training_log.txt', 'wb') as out:
            out.write(output)

        cmd = [
            'python', str(self.code2vec_path / 'code2vec.py'),
            '--load', f'{model_dir}/',
            '--test', str(fold_dir / 'code2vec_llir.train.c2v'),
            '--framework', 'tensorflow',
            '--export_code_vectors'
        ]
        subprocess.check_call(cmd)

        return fold_dir / 'code2vec_llir.train.c2v.vectors', fold_dir / 'code2vec_llir.val.c2v.vectors'

    @staticmethod
    def _collect_raw_c2v_files(data_dir, train_data_file):
        program_names = read_json(data_dir / 'programs.json')
        input_files = [
            file for file in data_dir.parent.parent.parent.iterdir()
            if file.name.endswith('.raw_c2v.gz') and get_program_name_from_filename(file.name) in program_names
        ]
        with open(train_data_file, 'w') as out:
            for file in input_files:
                with gzip.open(file, mode='rt') as inp:
                    assert out.write(inp.read()) > 0
                    out.write('\n')

    @staticmethod
    def _compress_and_write_features(bc_dir, vectors_path, out_path):
        code2vec_vectors = []
        with open(vectors_path) as inp:
            for line in inp:
                code2vec_vectors.append([float(x) for x in line.split()])

        blocks_df = blocks_for_fold(bc_dir)
        llvm_pass_labels = []
        for program_name in list(blocks_df['program'].unique()):
            with open((bc_dir.parent.parent.parent / program_name).with_suffix('.sip_labels')) as inp:
                for line in inp:
                    llvm_pass_labels.append(line)

        assert len(code2vec_vectors) == len(llvm_pass_labels)

        features = []
        for feature_vector, llvm_pass_line in zip(code2vec_vectors, llvm_pass_labels):
            block_name, block_uid, *_ = llvm_pass_line.split('\t')
            features.append([block_uid] + feature_vector)

        pd.DataFrame(features).to_csv(
            out_path,
            index=False,
            header=False
        )
