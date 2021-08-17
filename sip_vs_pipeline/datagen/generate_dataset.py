import argparse
import pathlib
import subprocess

IMAGE_NAME = 'smwyg'
GEN_PROTECTED_BINARIES_SH_PATH = pathlib.Path(__file__).absolute().parent / 'generate-protected-binaries.sh'
SMWYG_GIT_REPOSITORY = 'https://github.com/mr-ma/smwyg-artifact.git'


def parse_args():
    parser = argparse.ArgumentParser(description='Generates the dataset of protected binaries')
    parser.add_argument('output_dir', help='Directory where output should be stored')
    parser.add_argument(
        '--force', dest='force', action='store_true',
        help='Force data creation even if the output_dir is not empty', default=False
    )
    args = parser.parse_args()
    return args


def validate_output_dir(out_dir, force):
    if out_dir.exists():
        if out_dir.is_file():
            raise ValueError(f'{out_dir} must be a directory')
        if len(list(out_dir.iterdir())) > 0 and not force:
            raise ValueError(f'{out_dir} must be an empty directory')
    else:
        out_dir.mkdir(parents=True)


def build_docker_image():
    print(f'Building the docker image - {IMAGE_NAME}...')
    subprocess.run(['docker', 'build', '-t', IMAGE_NAME, SMWYG_GIT_REPOSITORY], check=True)
    print(f'Building the docker image - {IMAGE_NAME}...DONE')


def run_data_generation_script(out_dir):
    print('Running data generation in docker container...')
    docker_run = f'docker run --rm ' \
                 f'-v "{out_dir}":/home/sip/paperback:rw ' \
                 f'-v "{GEN_PROTECTED_BINARIES_SH_PATH}":/home/sip/eval/{GEN_PROTECTED_BINARIES_SH_PATH.name} ' \
                 f'--security-opt seccomp=unconfined {IMAGE_NAME}'
    data_script = 'mkdir -p /home/sip/paperback/LABELED-BCs && ' \
                  'ln -s /home/sip/paperback/LABELED-BCs /home/sip/eval/LABELED-BCs && ' \
                  f'bash {GEN_PROTECTED_BINARIES_SH_PATH.name}'
    subprocess.run(f'{docker_run} bash -c "{data_script}"', shell=True, check=True)
    print('Running data generation in docker container...DONE')


def main():
    args = parse_args()
    out_dir = pathlib.Path(args.output_dir)
    validate_output_dir(out_dir, args.force)
    build_docker_image()
    run_data_generation_script(out_dir)


if __name__ == '__main__':
    main()
