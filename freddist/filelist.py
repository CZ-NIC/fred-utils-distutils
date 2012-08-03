"""distutils.filelist

Provides the FileList class, used for poking about the filesystem
and building lists of files.
"""
import os

from distutils.filelist import findall as _findall, FileList as _FileList


def _strip_directory(filename, directory):
    """
    Strips directory from filename, if file is in directory or its subdirectories.
    """
    filename = os.path.normpath(filename)
    directory = os.path.normpath(directory)
    if filename.startswith(directory):
        return os.path.relpath(filename, directory)
    else:
        return filename


class FileList(_FileList):
    """
    A list of filenames relative to source directory.
    """
    def __init__(self,
                 warn=None,
                 debug_print=None,
                 srcdir=None):
        _FileList.__init__(self, warn, debug_print)
        self.srcdir = os.path.realpath(srcdir)

    def findall(self, dir=None):
        # Use source directory as default
        _FileList.findall(self, dir or self.srcdir)
        # And store paths relatively to source directory
        self.allfiles = [os.path.relpath(f, self.srcdir) for f in self.allfiles]

    # -- List-like methods ---------------------------------------------

    def append(self, item):
        # Store paths relatively to source directory
        _FileList.append(self, _strip_directory(item, self.srcdir))

    def extend(self, items):
        # Store paths relatively to source directory
        _FileList.extend(self, (_strip_directory(i, self.srcdir) for i in items))


def findall(dir=os.curdir):
    """
    Finds all files under 'dir' and returns the list of full filenames (relative to 'dir').

    Fix distutils version and really returns relative paths.
    """
    return [_strip_directory(f, dir) for f in _findall(dir)]
