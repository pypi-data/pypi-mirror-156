#!/usr/bin/env python3
import argparse
import ftplib
import os
import re
import sys
from typing import Iterable, List, NamedTuple


HOSTNAME = 'modland.com'
MODULE_PATH = 'pub/modules'


class PathPair(NamedTuple):
    remote_path: str
    destination: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-d', '--create-database', action='store_true', help='create modland database')
    parser.add_argument('-a', '--artist', type=str, help='artist name')
    return parser.parse_args()


def connect() -> ftplib.FTP:
    ftp = ftplib.FTP(HOSTNAME)
    ftp.login()
    return ftp


def search_dir(ftp: ftplib.FTP, path: str=MODULE_PATH) -> List[str]:
    result = []
    for directory in sorted(filter(lambda x: x[1]['type'] == 'dir', ftp.mlsd(path)), key=lambda x: x[0]):
        print('\r', end='\x1b[2K', flush=True)
        record = os.path.join(path, directory[0])
        print('READ:', os.path.join(HOSTNAME, record), end='', flush=True)
        result.append(record)
        result += search_dir(ftp, record)
    return sorted(result)


def download_base(path: str='~/.cache/modland.txt'):
    directory_list = search_dir(connect())
    with open(path, 'wt') as f:
        for item in directory_list:
            f.write(f'{item}\n')
            print('\r', end='\x1b[2K', flush=True)
            print('SAVE:', item, end='', flush=True)
    print('\r\x1b[2KLocal database complete.')


def search_artist(datafile: str, artist: str) -> List[str]:
    result = []
    with open(datafile, 'rt') as f:
        while True:
            line = f.readline()
            if not line:
                break
            if re.match(f'.+/?{artist.lower()}(/|$)', line.lower()):
                result.append(line.strip())
    return result


def make_destination_path(path_collection: Iterable[str], artist: str) -> List[PathPair]:
    result = []
    for path in path_collection:
        splitted_path = list(filter(lambda x: x, os.path.normpath(path).split(os.path.sep)))
        if path.lower().endswith(f'coop-{artist}'):
            result.append(PathPair(path, os.path.join(artist, f'coop-{splitted_path[-2]}')))
            continue
        elif path.lower().endswith(artist):
            result.append(PathPair(path, artist))
            continue
        result.append(PathPair(path, os.path.join(artist, splitted_path[-1])))
    return result


def download_artist(ftp: ftplib.FTP, path_pair: List[PathPair]):
    for pair in path_pair:
        if not os.path.exists(pair.destination):
            os.makedirs(pair.destination)
        files = filter(lambda x: x[1]['type'] == 'file', ftp.mlsd(pair.remote_path))
        for f in files:
            file_path = os.path.join(pair.remote_path, f[0])
            print('\r', end='\x1b[2K')
            print('DOWNLOAD:', os.path.join(pair.destination, f[0]), end=' ', flush=True)
            try:
                with open(os.path.join(pair.destination, f[0]), 'wb') as handler:
                    ftp.retrbinary(f'RETR {file_path}', handler.write)
            except ftplib.all_errors:
                print('ERROR')
                continue
    print()


if __name__ == '__main__':
    args = parse_args()
    if args.create_database:
        download_base()
        sys.exit(0)
    datafile_path = os.path.join(os.path.expanduser('~'), '.cache/modland.txt')
    if not os.path.exists(datafile_path):
        print('Modland datafile does not exists. Run with flag -d for download.')
        sys.exit(1)
    download_artist(connect(), make_destination_path(search_artist(datafile_path, args.artist), args.artist))

