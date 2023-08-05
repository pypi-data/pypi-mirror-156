"""This module provides a convenient context manager"""

import os

class cd:
    """
    Context manager for changing the current working directory.
    Author: Brian Hunt on Stack Overflow.
    https://stackoverflow.com/questions/431684/how-do-i-change-directory-cd-in-python/13197763#13197763

    >>> import os
    >>> from pathlib import Path
    >>> from pyfeasst import cd
    >>> with cd.cd("~/pyfeasst"): print(Path(os.getcwd()).name)
    pyfeasst
    """
    def __init__(self, newPath):
        self._new_path = os.path.expanduser(newPath)
        self._saved_path = None

    def __enter__(self):
        self._saved_path = os.getcwd()
        os.chdir(self._new_path)

    def __exit__(self, etype, value, traceback):
        os.chdir(self._saved_path)

if __name__ == "__main__":
    import doctest
    doctest.testmod()
