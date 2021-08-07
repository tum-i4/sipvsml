import pathlib
import subprocess

from sip_vs_pipeline.datagen.generate_dataset import IMAGE_NAME, GEN_PROTECTED_BINARIES_SH_PATH, parse_args, \
    build_docker_image


def run_data_generation_script(out_dir):
    print('Running data generation in docker container...')
    docker_run = f'docker run --rm ' \
                 f'-v "{out_dir}":/home/sip/paperback:rw ' \
                 f'-v "{GEN_PROTECTED_BINARIES_SH_PATH}":/home/sip/eval/generate-protected-binaries.sh ' \
                 f'--security-opt seccomp=unconfined {IMAGE_NAME}'
    data_script = 'mkdir -p /home/sip/paperback/LABELED-BCs && ' \
                  'ln -s /home/sip/paperback/LABELED-BCs /home/sip/eval/LABELED-BCs && ' \
                  'bash generate-protected-binaries.sh'
    subprocess.run(f'{docker_run} bash -c "{data_script}"', shell=True, check=True)
    print('Running data generation in docker container...DONE')


def main():
    args = parse_args()
    out_dir = pathlib.Path(args.output_dir)
    build_docker_image()
    run_data_generation_script(out_dir)


if __name__ == '__main__':
    main()
