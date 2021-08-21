import argparse
import pathlib
from concurrent.futures import ProcessPoolExecutor

from tqdm import tqdm

from sip_vs_pipeline.preprocessing.pre_processor import ComposePP, Ir2VecInstructionGen, \
    DisassembleBC, Code2VecPreProcessor, PDGPreProcessor, \
    KFoldSplit, LLVMPassLabels, RemoveLLMetadata
from sip_vs_pipeline.utils import get_protected_bc_dirs


def parse_args():
    parser = argparse.ArgumentParser(description='Preprocess protected binary programs')
    parser.add_argument('labeled_bc_dir', help='Directory where labeled datasets stored')
    parser.add_argument(
        '--preprocessors', choices=[
            'code2vec', 'general_ir', 'disassemble_bc', 'pdg',
            'k_fold_split', 'llvm_sip_labels', 'remove_ll_metadata'
        ], nargs='+', help='Which preprocessors to run'
    )
    parser.add_argument(
        '--run_sequentially', default=False, action='store_true',
        help='Run processing sequentially, in a single process'
    )
    parser.add_argument(
        '--dataset', help='Dataset name to process', required=False
    )
    args = parser.parse_args()
    return args


def create_preprocessor(preprocessors, labeled_bc_dir):
    pps = []
    for pp in preprocessors:
        if pp == 'general_ir':
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
        elif pp == 'remove_ll_metadata':
            pps.append(RemoveLLMetadata())
        else:
            raise RuntimeError(f'Unknown pp {pp}')
    return ComposePP(*pps)


def main():
    args = parse_args()
    labeled_bc_dir = pathlib.Path(args.labeled_bc_dir)

    preprocessor = create_preprocessor(args.preprocessors, labeled_bc_dir)
    bc_dirs = list(get_protected_bc_dirs(labeled_bc_dir, args.dataset))

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
