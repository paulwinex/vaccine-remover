"""
Cleaning ma files from vaccine malware
"""
import logging
import re
import shutil
import traceback
from pathlib import Path
import tempfile

logging.basicConfig(level=logging.INFO)


def read_blocks(file):
    """
    Iterate through file blocks
    """
    pattern = re.compile(r'^\s+'.encode())
    block = []
    for line in file:
        line = line.rstrip()
        if not line:
            continue
        if not pattern.match(line):
            if block:
                yield b'\n'.join(block)
                block = []
        block.append(line)
    if block:
        yield b'\n'.join(block)


def clear_ma_file(file_path, tmp_dir=None):
    """
    Cleaning one ma file
    """
    is_cleared = False
    file_path = Path(file_path)
    tmp_file = Path(tmp_dir or tempfile.gettempdir(), file_path.name)
    if tmp_file.exists():
        tmp_file.unlink()
    with file_path.open('rb') as src, tmp_file.open('wb') as tmp:
        for block in read_blocks(src):
            if b"vaccine" in block:
                is_cleared = True
                continue
            tmp.write(f'{block}\n'.encode())
    if is_cleared:
        logging.info(f"File cleared: {file_path}")
        return tmp_file


def replace_file(old_file, new_file, backup=True):
    """
    Replacing an old file with backup option
    """
    if backup:
        bkp_file = old_file.with_name(old_file.name + '.bkp')
        logging.info(f'Backup {old_file} -> {bkp_file}')
        old_file.rename(bkp_file)
    else:
        logging.info(f'Delete {old_file}')
        old_file.unlink()
    logging.info(f'Move {old_file} -> {new_file}')
    shutil.copyfile(new_file, old_file)


def clear_ma_files(src_dir, tmp_dir=None, recursive=True, replace_old_file=False, make_backup=True):
    """
    Recursive search and removal of malware from ma files in the specified directory
    """
    total = 0
    failed = 0
    cleaned_files = []
    for orig_file in Path(src_dir).glob("**/*.ma" if recursive else "*.ma"):
        try:
            logging.info('Process file %s', orig_file)
            clean_file = clear_ma_file(orig_file, tmp_dir)
        except Exception as e:
            logging.error(f"Failed file {orig_file}: {e}")
            failed += 1
            traceback.print_exc()
            continue
        if clean_file:
            if replace_old_file:
                logging.info('Replace old file...')
                replace_file(orig_file, clean_file, backup=make_backup)
                cleaned_files.append(orig_file)
            else:
                new_name = orig_file.with_name(orig_file.name+'.clean')
                if new_name.exists():
                    new_name.unlink()
                shutil.move(clean_file, new_name)
                cleaned_files.append(new_name)
            total += 1
    logging.info('Total cleaned files: %s', total)
    if failed:
        logging.warning('Failed to clean %s files', failed)
    return cleaned_files


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('paths', nargs='+', default='.', help='Path to folder or file')
    parser.add_argument('-r', '--replace',  action='store_true', default=False, help='Replace old file')
    parser.add_argument('-b', '--backup',  action='store_true', default=False, help='Create backup for old file')
    args = parser.parse_args()
    if args.paths:
        for path in args.paths:
            path = Path(path).resolve()
            if path.exists():
                if path.is_dir():
                    cleared_files = clear_ma_files(
                        path,
                        recursive=True,
                        replace_old_file=args.replace,
                        make_backup=args.backup
                    )
                    for file in cleared_files:
                        print(file)
                elif path.is_file() and path.suffix == '.ma':
                    result = clear_ma_file(path)
                    if result:
                        replace_file(path, result)
