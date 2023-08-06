# This file is part of nvitop, the interactive NVIDIA-GPU process viewer.
# License: GNU GPL version 3.

# pylint: disable=missing-module-docstring,missing-function-docstring

import os as _os
from collections import defaultdict as _defaultdict

import psutil as _psutil
from cachetools.func import ttl_cache as _ttl_cache
from psutil import *  # pylint: disable=wildcard-import,unused-wildcard-import,redefined-builtin


__all__ = _psutil.__all__.copy()
__all__.extend([
    'load_average', 'memory_percent', 'swap_percent',
    'ppid_map', 'reverse_ppid_map',
    'WSL', 'WINDOWS_SUBSYSTEM_FOR_LINUX'
])
__all__[__all__.index('Error')] = 'PsutilError'


PsutilError = Error  # make alias
del Error  # pylint: disable=undefined-variable


cpu_percent = _ttl_cache(ttl=0.25)(_psutil.cpu_percent)
virtual_memory = _ttl_cache(ttl=0.25)(_psutil.virtual_memory)
swap_memory = _ttl_cache(ttl=0.25)(_psutil.swap_memory)


try:
    load_average = _ttl_cache(ttl=2.0)(_psutil.getloadavg)
except AttributeError:
    def load_average(): return None  # pylint: disable=multiple-statements


def memory_percent():
    return virtual_memory().percent


def swap_percent():
    return swap_memory().percent


ppid_map = _psutil._ppid_map  # pylint: disable=protected-access


def reverse_ppid_map():  # pylint: disable=function-redefined
    tree = _defaultdict(list)
    for pid, ppid in ppid_map().items():
        tree[ppid].append(pid)

    return tree


if LINUX:
    WSL = _os.getenv('WSL_DISTRO_NAME', default=None)
    if WSL is not None and WSL == '':
        WSL = 'WSL'
else:
    WSL = None
WINDOWS_SUBSYSTEM_FOR_LINUX = WSL
