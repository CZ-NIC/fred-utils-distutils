"""distutils.filelist

Provides the FileList class, used for poking about the filesystem
and building lists of files.
"""


__revision__ = "$Id: filelist.py 37828 2004-11-10 22:23:15Z loewis $"


import os
from distutils.filelist import FileList as _FileList


class FileList(_FileList):
    def __init__(self,
                 warn=None,
                 debug_print=None,
                 srcdir=None):
        _FileList.__init__(self, warn, debug_print)
        self.srcdir = srcdir

    # -- Filtering/selection methods -----------------------------------

    def include_pattern (self, pattern,
                         anchor=1, prefix=None, is_regex=0):
        if prefix:
            prefix = os.path.join(self.srcdir, prefix)
        return _FileList.include_pattern(self, pattern, anchor, prefix, is_regex)
