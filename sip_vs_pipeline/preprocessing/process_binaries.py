import argparse
import pathlib
from concurrent.futures import ProcessPoolExecutor

from tqdm import tqdm

from sip_vs_pipeline.preprocessing.pre_processor import ComposePP, Ir2VecInstructionGen, \
    CompressToZip, RemoveCsvFiles, RemoveRawBinaries, DisassembleBC, Code2VecPreProcessor, PDGPreProcessor, \
    KFoldSplit, LLVMPassLabels
from sip_vs_pipeline.utils import get_protected_bc_dirs


def parse_args():
    parser = argparse.ArgumentParser(description='Preprocess protected binary programs')
    parser.add_argument('labeled_bc_dir', help='Directory where labeled binaries are stored')
    parser.add_argument(
        '--preprocessors', choices=[
            'compress_csv', 'code2vec', 'general_ir', 'disassemble_bc', 'remove_raw_bc', 'remove_csv_files', 'pdg',
            'k_fold_split', 'llvm_sip_labels'
        ], nargs='+', help='Which preprocessors to run'
    )
    parser.add_argument(
        '--run_sequentially', default=False,
        type=bool, help='Run processing sequentially, in a single process'
    )
    args = parser.parse_args()
    return args


def create_preprocessor(preprocessors, labeled_bc_dir):
    pps = []
    for pp in preprocessors:
        if pp == 'compress_csv':
            pps.append(CompressToZip())
        elif pp == 'remove_raw_bc':
            pps.append(RemoveRawBinaries())
        elif pp == 'remove_csv_files':
            pps.append(RemoveCsvFiles())
        elif pp == 'general_ir':
            pps.append(Ir2VecInstructionGen())
        elif pp == 'disassemble_bc':
            pps.append(DisassembleBC())
        elif pp == 'code2vec':
            pps.append(Code2VecPreProcessor())
        elif pp == 'pdg':
            pps.append(PDGPreProcessor(labeled_bc_dir))
        elif pp == 'k_fold_split':
            pps.append(KFoldSplit())
        elif pp == 'llvm_sip_labels':
            pps.append(LLVMPassLabels())
        else:
            raise RuntimeError(f'Unknown pp {pp}')
    return ComposePP(*pps)


def main():
    args = parse_args()
    labeled_bc_dir = pathlib.Path(args.labeled_bc_dir)

    preprocessor = create_preprocessor(args.preprocessors, labeled_bc_dir)
    bc_dirs = list(get_protected_bc_dirs(labeled_bc_dir))

    if args.run_sequentially:
        for bc_dir in tqdm(bc_dirs, desc='preprocessing binaries'):
            preprocessor.run(bc_dir)
    else:
        with ProcessPoolExecutor() as process_pool:
            list(tqdm(
                process_pool.map(preprocessor.run, bc_dirs),
                total=len(bc_dirs),
                desc='preprocessing binaries'
            ))


if __name__ == '__main__':
    main()
