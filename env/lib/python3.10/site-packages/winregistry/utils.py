import winreg
from typing import Tuple
from winreg import KEY_WOW64_32KEY, KEY_WOW64_64KEY, HKEYType

from winregistry import ShortRootAlias


def expand_short_root(
    root: str,
) -> str:
    try:
        root = ShortRootAlias[root].value
    except KeyError:
        pass
    return root


def get_access_key(
    access: int,
    key_wow64_32key: bool = False,
) -> int:
    x64_key = KEY_WOW64_32KEY if key_wow64_32key else KEY_WOW64_64KEY
    return access | x64_key


def parse_path(
    path: str,
) -> Tuple[HKEYType, str]:
    _root, key_path = path.split("\\", maxsplit=1)
    _root = expand_short_root(_root.upper())
    reg_root = getattr(winreg, _root)
    if not key_path:
        raise ValueError('Not found key in "{}"'.format(path))
    return reg_root, key_path
