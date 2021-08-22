import os
import pathlib
import subprocess

from sip_vs_pipeline.datagen.generate_dataset import __file__ as __datagen_file__
from sip_vs_pipeline.datagen.generate_dataset import parse_args
from sip_vs_pipeline.feature_extraction.extract_features import __file__ as __feature_extraction_file__
from sip_vs_pipeline.model_training.train_all_models import __file__ as __train_all_models_file__
from sip_vs_pipeline.preprocessing.process_binaries import __file__ as __preprocessing_file__


def run_bash_command(cmd):
    subprocess.run(
        f'bash -c "{" ".join(cmd)}"', check=True, shell=True
    )


def generate_dataset(dataset_dir):
    cmd = [
        'python3',
        str(pathlib.Path(__datagen_file__).absolute()),
        str(dataset_dir)
    ]
    print(' '.join(cmd))
    run_bash_command(cmd)


def run_preprocessing(labeled_bc_dir):
    preprocessors = [
        'pdg',
        'disassemble_bc',
        'remove_ll_metadata',
        'llvm_sip_labels',
        'general_ir',
        'code2vec',
        'k_fold_split',
    ]
    # can be run together, but easier to debug this way
    for preprocessor in preprocessors:
        cmd = [
            'python3',
            str(pathlib.Path(__preprocessing_file__).absolute()),
            str(labeled_bc_dir),
            '--preprocessors', preprocessor
        ]
        print(' '.join(cmd))
        run_bash_command(cmd)


def run_feature_extraction(labeled_bc_dir):
    features = [
        'code2vec',
        'tf_idf',
        'ir2vec',
        'pdg'
    ]

    # Progressively reduce max_workers to compensate for possible OOM crashes
    max_workers = os.cpu_count()
    while max_workers > 1:
        for feature in features:
            cmd = [
                'python3',
                str(pathlib.Path(__feature_extraction_file__).absolute()),
                str(labeled_bc_dir),
                '--feature_extractor', feature,
                '--max_workers', str(max_workers)
            ]
            print(' '.join(cmd))
            run_bash_command(cmd)
        max_workers //= 2


def run_experiments(labeled_bc_dir):
    features = [
        ('pdg',),
        ('code2vec',),
        ('tf_idf',),
        ('ir2vec',),

        ('pdg', 'tf_idf'),
        ('pdg', 'code2vec'),
        ('pdg', 'ir2vec'),

        ('pdg', 'tf_idf', 'ir2vec', 'code2vec'),
    ]
    # Progressively reduce max_workers to compensate for possible OOM crashes
    num_processes = os.cpu_count()
    while num_processes > 1:
        for feature_set in features:
            cmd = [
                'python3',
                str(pathlib.Path(__train_all_models_file__).absolute()),
                '--model', 'graph_sage',
                '--use_features', ' '.join(feature_set),
                '--num_processes', str(num_processes),
                str(labeled_bc_dir)
            ]
            print(' '.join(cmd))
            run_bash_command(cmd)
        num_processes //= 2


def main():
    args = parse_args()
    dataset_dir = pathlib.Path(args.output_dir)

    generate_dataset(dataset_dir)

    labeled_bc_dir = dataset_dir / 'LABELED-BCs'
    run_preprocessing(labeled_bc_dir)
    run_feature_extraction(labeled_bc_dir)
    run_experiments(labeled_bc_dir)


if __name__ == '__main__':
    main()
