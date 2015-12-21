"""distutils.util

Miscellaneous utility functions -- anything that doesn't fit into
one of the other *util.py modules.
"""
import os
import sys
from distutils import log
from distutils.dep_util import newer
from distutils.util import convert_path
from subprocess import CalledProcessError, check_call as _check_call

from freddist.filelist import findall

try:
    # distutils version 2.6.5
    from distutils.errors import DistutilsByteCompileError
except ImportError:
    # distutils version 2.5.1
    from distutils.errors import CompileError as DistutilsByteCompileError


def check_call(*args, **kwargs):
    """
    Returns whether call was successful.
    """
    try:
        _check_call(*args, **kwargs)
    except CalledProcessError, error:
        log.warn(error)
        return False
    else:
        return True


def i18n_compile(i18n_files, force=0, dry_run=0):
    """
    Byte-compile i18n files.
    """
    # nothing is done if sys.dont_write_bytecode is True
    if sys.dont_write_bytecode:
        raise DistutilsByteCompileError('byte-compiling is disabled.')

    for filename in i18n_files:
        if not filename.endswith('.po'):
            continue

        outfile = '%s.mo' % os.path.splitext(filename)[0]
        cmd = ('msgfmt', '--check-format', '-o', outfile, filename)

        if force or newer(filename, outfile):
            log.info("byte-compiling %s to %s", filename, outfile)
            if not dry_run:
                if not check_call(cmd):
                    log.warn("error in compilation of %s to %s", filename, outfile)
        else:
            log.debug("skipping byte-compilation of %s to %s", filename, outfile)


# Copied from setuptools
def find_packages(where='.', exclude=()):
    """
    Return a list all Python packages found within directory 'where'

    'where' should be supplied as a "cross-platform" (i.e. URL-style) path; it
    will be converted to the appropriate local path syntax.  'exclude' is a
    sequence of package names to exclude; '*' can be used as a wildcard in the
    names, such that 'foo.*' will exclude all subpackages of 'foo' (but not
    'foo' itself).
    """
    out = []
    stack=[(convert_path(where), '')]
    while stack:
        where,prefix = stack.pop(0)
        for name in os.listdir(where):
            fn = os.path.join(where,name)
            if ('.' not in name and os.path.isdir(fn) and
                os.path.isfile(os.path.join(fn,'__init__.py'))
            ):
                out.append(prefix+name); stack.append((fn,prefix+name+'.'))
    for pat in list(exclude)+['ez_setup', 'distribute_setup']:
        from fnmatch import fnmatchcase
        out = [item for item in out if not fnmatchcase(item,pat)]
    return out


def find_data_files(srcdir, path='.'):
    """
    Finds all files at given location and returns data-files style list.

    Target directories are relative to path, source files are relative to source directory.
    """
    data_files = {}
    for filename in findall(os.path.join(srcdir, path)):
        dirname = os.path.dirname(filename)
        files = data_files.setdefault(dirname, [])
        files.append(os.path.join(path, filename))
    return data_files.items()
