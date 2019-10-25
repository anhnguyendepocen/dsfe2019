#!/usr/bin/env python
""" Build exercise
"""

import os
import os.path as op
from argparse import ArgumentParser
import shutil
from glob import glob
from zipfile import ZipFile

import jupytext
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor


def read_nb(fname):
    return jupytext.readf(fname)


def clear_directory(fname):
    path = path_of(fname)
    for basename in ('.ok_storage',):
        pth = op.join(path, basename)
        if op.exists(pth):
            os.unlink(pth)
    pycache = op.join(path, 'tests', '__pycache__')
    if op.isdir(pycache):
        shutil.rmtree(pycache)


def path_of(fname):
    return op.split(op.abspath(fname))[0]


def ipynb_fname(fname):
    froot, ext = op.splitext(fname)
    return froot + '.ipynb'


def execute_nb(nb, path, nbargs=None):
    nbargs = {} if nbargs is None else nbargs
    ep = ExecutePreprocessor(**nbargs)
    ep.preprocess(nb, {'metadata': {'path': path}})
    return nb


def clear_outputs(nb):
    for cell in nb['cells']:
        if cell['cell_type'] == 'code':
            cell['outputs'] = []
    return nb


def write_nb(nb, fname):
    with open(fname, 'w', encoding='utf-8') as f:
        nbformat.write(nb, f)


def good_fname(fname):
    fn = op.basename(fname)
    if fn.startswith('.'):
        return False
    if fn.endswith('.Rmd'):
        return False
    if fn.startswith('test_'):
        return False
    if 'solution' in fn:
        return False
    if fn == ('__pycache__'):
        return False
    if fn.endswith('.pyc'):
        return False
    return True


def pack_exercise(fname, out_path=None):
    path = op.relpath(path_of(fname), '.')
    if out_path is None:
        out_path = os.getcwd()
    froot = op.splitext(op.basename(fname))[0]
    zip_fname = op.join(out_path, froot + '.zip')
    listing = glob(op.join(path, '**'), recursive=True)
    files = [f for f in listing if good_fname(f)]
    with ZipFile(zip_fname, 'w') as zip_obj:
        for fn in files:
            zip_obj.write(fn)


def get_parser():
    parser = ArgumentParser()
    parser.add_argument('notebook', nargs='+',
                        help='Notebook(s) to clean')
    parser.add_argument('--execute', action='store_true',
                        help='If specified, execute notebooks before cleaning')
    parser.add_argument('--out-path', default=os.getcwd(),
                        help='Output path for zipped exercise (default pwd)')
    return parser


def process_nb(fname, execute=False, out_path=None):
    clear_directory(fname)
    nb = read_nb(fname)
    if execute:
        nb = execute_nb(nb, path_of(fname))
    nb = clear_outputs(nb)
    write_nb(nb, ipynb_fname(fname))
    pack_exercise(fname, out_path)


def main():
    args = get_parser().parse_args()
    for fname in args.notebook:
        process_nb(fname, execute=args.execute, out_path=args.out_path)


if __name__ == '__main__':
    main()
