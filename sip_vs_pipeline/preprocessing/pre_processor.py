import subprocess

from sip_vs_pipeline.preprocessing.ir_line_parser import generalize_ir_line
from sip_vs_pipeline.utils import read_blocks_df, write_blocks_df, write_relations_df, read_relations_df


class PreProcessor:
    def run(self, protected_bc_dir):
        raise NotImplementedError


class ComposePP(PreProcessor):
    def __init__(self, *pps: PreProcessor) -> None:
        super().__init__()
        self.pps = pps

    def run(self, protected_bc_dir):
        for pp in self.pps:
            pp.run(protected_bc_dir)


class Ir2VecInstructionGen(PreProcessor):
    def __init__(self, ir_delimiter='|.|') -> None:
        super().__init__()
        self._ir_delimiter = ir_delimiter

    def _get_generalized_ir_block(self, ir_block_str):
        cleaned_irs = [x.strip() for x in ir_block_str.strip().split(self._ir_delimiter) if x.strip() != '']
        gen_irs = [generalize_ir_line(ci) for ci in cleaned_irs]
        return self._ir_delimiter.join(gen_irs)

    def run(self, protected_bc_dir):
        blocks_file_path = protected_bc_dir / 'blocks.csv.gz'
        blocks_df = read_blocks_df(blocks_file_path)
        blocks_df['generalized_block'] = blocks_df['w_63'].map(self._get_generalized_ir_block)
        write_blocks_df(blocks_file_path, blocks_df)


def get_default_block_columns():
    feature_names = [f'w_{i}' for i in range(64)]
    return ['uid'] + feature_names + ['program', 'subject']


class CompressToZip(PreProcessor):
    def run(self, protected_bc_dir):
        blocks_file_path = protected_bc_dir / 'blocks.csv'
        if blocks_file_path.exists():
            blocks_df = read_blocks_df(
                blocks_file_path,
                header=None,
                lineterminator='\r',
                sep=';',
                names=get_default_block_columns()
            )
            write_blocks_df(blocks_file_path.with_suffix('.csv.gz'), blocks_df)

        relations_file_path = protected_bc_dir / 'relations.csv'
        if relations_file_path.exists():
            relations_df = read_relations_df(
                relations_file_path,
                header=None,
                sep=';',
                names=['source', 'target', 'label'],
            )
            write_relations_df(
                relations_file_path.with_suffix('.csv.gz'),
                relations_df
            )


class RemoveRawBinaries(PreProcessor):
    def run(self, protected_bc_dir):
        for file in protected_bc_dir.iterdir():
            if file.suffix == '.bc':
                file.unlink()


class RemoveCsvFiles(PreProcessor):
    def run(self, protected_bc_dir):
        for file in protected_bc_dir.iterdir():
            if file.suffix == '.csv':
                file.unlink()


class DisassembleBC(PreProcessor):
    def __init__(self, llvm_dis_version='10') -> None:
        super().__init__()
        self.llvm_dis_version = llvm_dis_version

    def run(self, protected_bc_dir):
        for file in protected_bc_dir.iterdir():
            if file.suffix == '.bc':
                subprocess.check_call([f'llvm-dis-{self.llvm_dis_version}', str(file)])
