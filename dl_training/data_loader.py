import pathlib

import torch
from torch import tensor
from torch.utils.data import Dataset

TARGET_FLAGS = ['CFI', 'OH', 'SC']


class CompositeDataset(Dataset):
    def __init__(self, *datasets) -> None:
        super().__init__()
        self.datasets = datasets

    def __getitem__(self, index: int):
        for d in self.datasets:
            if index < len(d):
                return d[index]
            index -= len(d)

    def __len__(self) -> int:
        return sum(map(len, self.datasets))


class ProgramsDataset(Dataset):
    def __init__(self, program_path):
        super().__init__()
        self.flags = TARGET_FLAGS
        self.obfuscations = []
        self.program_path = pathlib.Path(program_path)
        self.program_paths = list(self._get_bc_program_paths())

    def _get_bc_program_paths(self):
        for file_path in self.program_path.iterdir():
            if str(file_path).endswith('.vec'):
                yield file_path

    def __getitem__(self, index: int):
        file_path = self.program_paths[index]
        features = tensor([float(n) for n in file_path.read_text().split()])
        assert features.shape[0] == 300
        targets = tensor([int(flag in file_path.name.split('.')[0].split('-')[1:]) for flag in self.flags]).float()
        obfuscations = '-'.join([x for x in file_path.name.split('.')[0].split('-')[1:] if x not in self.flags])
        return features, targets, obfuscations

    def __len__(self) -> int:
        return len(self.program_paths)


def get_loader(dataset, batch_size, shuffle, num_workers, drop_last=True):
    data_loader = torch.utils.data.DataLoader(
        dataset=dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=num_workers,
        drop_last=drop_last,
        pin_memory=True
    )
    return data_loader


def read_all_programs_dataset(data_dir='../data'):
    res = []
    data_dir = pathlib.Path(data_dir)
    for program_path in data_dir.iterdir():
        res.append(ProgramsDataset(program_path))
    return res


def main():
    all_programs_dataset = read_all_programs_dataset()
    dataset = CompositeDataset(*all_programs_dataset)
    loader = get_loader(dataset, batch_size=32, shuffle=True, num_workers=4, drop_last=False)
    for features, targets in loader:
        print(features.shape, targets.shape)


if __name__ == '__main__':
    main()
