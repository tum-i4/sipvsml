import argparse
import itertools
import pathlib
import subprocess
from collections import defaultdict
from dataclasses import dataclass
from typing import List

from tqdm import tqdm


@dataclass
class Node:
    node_type: str
    start_pos: int
    end_pos: int
    txt: str
    children: List
    parent = None


class AstTree:
    def __init__(self, root, file_content) -> None:
        super().__init__()
        self.root = root
        self.file_content = file_content

    def get_basic_blocks(self):
        yield from self._get_nodes_with_type(self.root, 'BasicBlock')

    def get_leaf_pairs_with_paths(self, max_path_length, max_path_width, root=None):
        all_leaves = list(self._get_all_leaves(root))
        paths_dict = []
        for leaf in all_leaves:
            paths_dict.append(self._get_path_to_leaf(leaf))

        for (i1, leaf1), (i2, leaf2) in itertools.combinations(enumerate(all_leaves), 2):
            if i2 - i1 > max_path_width:
                continue

            path1 = paths_dict[i1]
            path2 = paths_dict[i2]
            up, parent, down = self._get_full_path(path1, path2)
            if len(up) + 1 + len(down) < max_path_length:
                yield (up, i1), parent, (down, i2)

    @staticmethod
    def _get_full_path(path1, path2):
        i = 0
        while i < len(path1) and i < len(path2) and path1[i] == path2[i]:
            i += 1

        up, parent, down = path1[i:][::-1], path1[i-1], path2[i:]
        return up, parent, down

    def _get_path_to_leaf(self, leaf):
        res = []
        while True:
            res.append(leaf)
            if leaf == self.root:
                break
            leaf = leaf.parent
        return res[::-1]  # reverse path to get root -> ... -> leaf

    def _get_all_leaves(self, root=None):
        if root is None:
            root = self.root

        if len(root.children) == 0:
            yield root

        for child in root.children:
            yield from self._get_all_leaves(child)

    def _get_nodes_with_type(self, node, target_type):
        if node.node_type == target_type:
            yield node

        for child in node.children:
            yield from self._get_nodes_with_type(child, target_type)


class BasicBlock:
    def __init__(self, uid, sip_label, ast_node) -> None:
        super().__init__()
        self.uid = uid
        self.label = sip_label
        self.ast_node = ast_node


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-maxlen', '--max_path_length', dest='max_path_length', required=False, default=8)
    parser.add_argument('-maxwidth', '--max_path_width', dest='max_path_width', required=False, default=2)
    parser.add_argument('-file', '--file', dest='file', required=False)
    parser.add_argument('-dir', '--dir', dest='dir', required=False)
    args = parser.parse_args()

    if sum([args.file is None, args.dir is None]) != 1:
        parser.error('Exactly One of -file or -dir must be given')

    return args


def find_all_sub_ll_files(path):
    if path.is_file():
        if path.suffix == '.ll':
            yield path.absolute()
    else:
        for child in path.iterdir():
            yield from find_all_sub_ll_files(child)


def get_all_ll_files(args):
    if args.file is not None:
        yield pathlib.Path(args.file)
    elif args.dir is not None:
        dir_path = pathlib.Path(args.dir)
        yield from find_all_sub_ll_files(dir_path)


def parse_tree_lines(lines, depth, i):
    line = lines[i]
    node_type, start_pos, end_pos, txt = map(str.strip, line.strip('-').split('\t'))
    start_pos, end_pos = int(start_pos), int(end_pos)

    children = []
    i += 1
    while i < len(lines):
        next_line = lines[i]
        if next_line.startswith('-' * (depth + 1)):
            child, i = parse_tree_lines(lines, depth + 1, i)
            children.append(child)
        else:
            break

    node = Node(node_type, start_pos, end_pos, txt, children)
    for child in node.children:
        child.parent = node
    return node, i


def parse_ast_text(ast_text):
    lines = ast_text.decode().splitlines(keepends=False)
    root, _ = parse_tree_lines(lines, 0, 0)
    return root


def get_raw_text(file_content, node):
    return file_content[node.start_pos: node.end_pos]


def get_ast(ll_file_path):
    cmd = ['go', 'run', 'main/main.go', '-ll-file-path', str(ll_file_path)]
    ast_text = subprocess.check_output(cmd, cwd='llvm_ir_parser')
    root = parse_ast_text(ast_text)
    file_content = read_file(ll_file_path)
    return AstTree(root, file_content)


def get_block_labels(ll_file_path):
    # TODO
    return defaultdict(lambda: 'none')


def get_basic_blocks(root, block_labels):
    for basic_block_node in root.get_basic_blocks():
        uid = " LABELED-BCs/simple-cov/BCF30/anagram-BCF.bccheck_anagram%originalBB28alteredBB "
        yield BasicBlock(uid, block_labels[uid], basic_block_node)


def hash_code(text):
    # default java string hash code implementation
    h = 0
    for b in text.encode():
        h = 31 * h + (b & 255)
    return h


def print_training_data(basic_block, paths):
    paths = list(paths)
    label = basic_block.label
    path_strings = []
    for (up, i1), parent, (down, i2) in paths:
        up_str = [x.node_type for x in up]
        up_str[0] = f'{up_str[0]}{i1}'

        down_str = [x.node_type for x in down]
        down_str[-1] = f'{down_str[-1]}{i2}'

        path_up = '^'.join(map(lambda x: f'({x})', up_str))
        path_down = '_'.join(map(lambda x: f'({x})', down_str))
        path_str = path_up + '^' + f'({parent.node_type})' + '_' + path_down
        path_strings.append(path_str)

    print(path_strings)


def extract_from_ll_file(ll_file_path, max_path_length, max_path_width):
    ast = get_ast(ll_file_path)
    block_labels = get_block_labels(ll_file_path)
    basic_blocks = get_basic_blocks(ast, block_labels)
    for basic_block in basic_blocks:
        block_paths = ast.get_leaf_pairs_with_paths(max_path_length, max_path_width, basic_block.ast_node)
        print_training_data(basic_block, block_paths)


def read_file(ll_file_path):
    with open(ll_file_path) as inp:
        file_content = inp.read()
    return file_content


def extract_from_all_files(all_ll_files, max_path_length, max_path_width):
    for ll_file_path in tqdm(list(all_ll_files)):
        extract_from_ll_file(ll_file_path, max_path_length, max_path_width)


def main():
    args = parse_args()
    max_path_length = args.max_path_length
    max_path_width = args.max_path_width
    all_ll_files = get_all_ll_files(args)
    extract_from_all_files(all_ll_files, max_path_length, max_path_width)


if __name__ == '__main__':
    main()
