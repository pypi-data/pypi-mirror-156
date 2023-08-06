#!/usr/bin/env python3
"""
Author : Xinyuan Chen <45612704+tddschn@users.noreply.github.com>
Date   : 2022-06-26
Purpose: Add directories to Spotlight exclusion list
"""

import argparse
from pathlib import Path
import os
from . import __version__
from .config import SPOTLIGHT_CONFIG_PLIST_FILE, SPOTLIGHT_INDEXING_LAUNCHD_SERVICE_NAME
from .utils import (
    concat_lines_from_files_stripped,
    read_spotlight_exclusions,
    add_dirs_to_spotlight_exclusions,
    remove_dirs_from_spotlight_exclusions,
    dedupe_spotlight_exclusions,
    restart_launchd_service,
)

__app_name__ = 'spotlight-exclude'


def show_dirs(args: argparse.Namespace) -> None:
    """Show Spotlight exclusion list"""
    print('\n'.join(read_spotlight_exclusions()))


def add_dirs(args: argparse.Namespace) -> None:
    """Add directories to Spotlight exclusion list"""
    add_dirs_to_spotlight_exclusions(args.dirs)


def add_dirs_from(args: argparse.Namespace) -> None:
    """Add directories from a file to Spotlight exclusion list"""
    dirs = concat_lines_from_files_stripped(args.files)
    add_dirs_to_spotlight_exclusions(dirs)  # type: ignore


def remove_dirs(args: argparse.Namespace) -> None:
    """Remove directories from Spotlight exclusion list"""
    remove_dirs_from_spotlight_exclusions(args.dirs)


def remove_dirs_from(args: argparse.Namespace) -> None:
    """Remove directories from Spotlight exclusion list"""
    dirs = concat_lines_from_files_stripped(args.files)
    remove_dirs_from_spotlight_exclusions(dirs)  # type: ignore


def dedupe_dirs(args: argparse.Namespace) -> None:
    """Remove duplicate directories from Spotlight exclusion list"""
    dedupe_spotlight_exclusions()


def get_args():
    """Get command-line arguments"""

    parser = argparse.ArgumentParser(
        prog=__app_name__,
        description='Add directories to Spotlight exclusion list',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        '-V',
        '--version',
        action='version',
        version=f'%(prog)s {__version__}',
    )

    sp = parser.add_subparsers()
    parser_show = sp.add_parser(
        'show',
        aliases=['s'],
        help='Show Spotlight exclusion list',
    )

    parser_show.set_defaults(func=show_dirs)
    parser_add = sp.add_parser(
        'add',
        aliases=['a'],
        help='Add one or more directories to Spotlight exclusion list',
    )
    parser_add.add_argument(
        'dirs',
        nargs='+',
        help='Directories to add to Spotlight exclusion list',
        type=Path,
    )
    parser_add.set_defaults(func=add_dirs)

    parser_add_from = sp.add_parser(
        'add-from',
        aliases=['af'],
        help='Read directories from a file and add them to Spotlight exclusion list',
    )

    parser_add_from.add_argument(
        'files', nargs='+', help='Files to read from', type=Path
    )

    parser_add_from.set_defaults(func=add_dirs_from)

    parser_remove = sp.add_parser(
        'remove',
        aliases=['r'],
        help='Remove one or more directories from Spotlight exclusion list',
    )
    parser_remove.add_argument(
        'dirs',
        nargs='+',
        help='Directories to remove from Spotlight exclusion list',
        type=Path,
    )
    parser_remove.set_defaults(func=remove_dirs)

    parser_remove_from = sp.add_parser(
        'remove-from',
        aliases=['rf'],
        help='Read directories from a file and remove them from Spotlight exclusion list',
    )

    parser_remove_from.add_argument(
        'files', nargs='+', help='Files to read from', type=Path
    )

    parser_remove_from.set_defaults(func=remove_dirs_from)

    parser_dedupe = sp.add_parser(
        'dedupe',
        aliases=['d'],
        help='Remove duplicate directories from Spotlight exclusion list',
    )
    parser_dedupe.set_defaults(func=dedupe_dirs)

    return parser, parser.parse_args()


def check_root():
    if os.getuid() != 0:
        print(f'{__app_name__} must be run as root')
        print(
            f'In order to read / write Spotlight exclusion list stored at {str(SPOTLIGHT_CONFIG_PLIST_FILE)}'
        )
        return 1


def main():
    """Make a jazz noise here"""

    check_root()
    parser, args = get_args()
    if hasattr(args, 'func'):
        args.func(args)
        if args.func in [
            add_dirs,
            add_dirs_from,
            remove_dirs,
            remove_dirs_from,
            dedupe_dirs,
        ]:
            restart_launchd_service(SPOTLIGHT_INDEXING_LAUNCHD_SERVICE_NAME)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
