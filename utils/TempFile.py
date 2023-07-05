import atexit
import os
import sys
from tempfile import NamedTemporaryFile
from typing import IO, List, Literal


_tempfile_pool: List[IO[any]] = []
_FileMode = Literal['r', 'w', 'a', 'x', 'r+', 'w+', 'a+', 'x+', 'rt', 'wt', 'at', 'xt', 'r+t', 'w+t', 'a+t', 'x+t']


def make_tempfile(mode: _FileMode, suffix: str):
    fp = NamedTemporaryFile(mode, delete=False, suffix=suffix)
    _tempfile_pool.append(fp)
    return fp


@atexit.register
def _cleanup_tempfile():
    for fp in _tempfile_pool:
        try:
            if not fp.closed: fp.close()
            os.unlink(fp.name)
        except:
            pass
