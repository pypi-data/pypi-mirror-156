from os import PathLike
from pathlib import Path
from typing import Iterable
from .config import SPOTLIGHT_CONFIG_PLIST_FILE


def concat_lines_from_files_stripped(files: Iterable[Path]) -> list[str]:
    lines = []
    for f in files:
        lines += [line.strip() for line in f.read_text().splitlines()]
    return lines


def read_spotlight_exclusions() -> list[str]:
    """Read Spotlight exclusion list"""
    import plistlib

    plist = plistlib.loads(SPOTLIGHT_CONFIG_PLIST_FILE.read_bytes())
    return plist['Exclusions']


def add_dirs_to_spotlight_exclusions(dirs: list[PathLike]) -> None:
    """Add directories to Spotlight exclusion list"""
    import plistlib

    plist = plistlib.loads(SPOTLIGHT_CONFIG_PLIST_FILE.read_bytes())
    exclusion_set = set(plist['Exclusions'])
    exclusion_set.update(str(d.resolve()) if isinstance(d, Path) else d for d in dirs)
    plist['Exclusions'] = list(exclusion_set)
    SPOTLIGHT_CONFIG_PLIST_FILE.write_bytes(plistlib.dumps(plist))


def remove_dirs_from_spotlight_exclusions(dirs: list[PathLike]) -> None:
    """Remove directories from Spotlight exclusion list"""
    import plistlib

    plist = plistlib.loads(SPOTLIGHT_CONFIG_PLIST_FILE.read_bytes())
    exclusion_set = set(plist['Exclusions'])
    exclusion_set.difference_update(
        str(d.resolve()) if isinstance(d, Path) else d for d in dirs
    )
    plist['Exclusions'] = list(exclusion_set)
    SPOTLIGHT_CONFIG_PLIST_FILE.write_bytes(plistlib.dumps(plist))


def dedupe_spotlight_exclusions() -> None:
    """Remove duplicate directories from Spotlight exclusion list"""
    import plistlib

    plist = plistlib.loads(SPOTLIGHT_CONFIG_PLIST_FILE.read_bytes())
    exclusion_set = set(plist['Exclusions'])
    exclusion_list = list(exclusion_set)
    exclusion_list.sort()
    plist['Exclusions'] = exclusion_list
    SPOTLIGHT_CONFIG_PLIST_FILE.write_bytes(plistlib.dumps(plist))


def restart_launchd_service(service_name: str) -> None:
    """Restart launchd service"""
    import subprocess

    subprocess.run(['launchctl', 'stop', service_name])
    subprocess.run(['launchctl', 'start', service_name])
