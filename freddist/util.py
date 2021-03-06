#
# Copyright (C) 2011-2019  CZ.NIC, z. s. p. o.
#
# This file is part of FRED.
#
# FRED is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# FRED is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with FRED.  If not, see <https://www.gnu.org/licenses/>.

"""
Module for distutils.util.

Miscellaneous utility functions -- anything that doesn't fit into
one of the other *util.py modules.
"""
import os
import sys
from distutils import log
from distutils.dep_util import newer, newer_group
from distutils.dir_util import mkpath
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
    """Return whether call was successful."""
    try:
        _check_call(*args, **kwargs)
    except CalledProcessError, error:
        log.warn(error)
        return False
    else:
        return True


def i18n_compile(i18n_files, force=0, dry_run=0):
    """Byte-compile i18n files."""
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


def scss_compile(scss_files, srcdir=None, force=0, dry_run=0):
    """Compile SCSS files."""
    for output, inputs in scss_files.items():
        cmd = ['pyscss', '--output', output]
        if srcdir:
            cmd += ['--load-path', srcdir]
        cmd += list(inputs)

        if force or newer_group(inputs, output):
            log.info("SCSS compiling %s to %s", inputs, output)
            if not dry_run:
                # Create directory if it doesn't exist
                mkpath(os.path.dirname(output))
                if not check_call(cmd):
                    log.warn("error in SCSS compilation of %s to %s", inputs, output)
        else:
            log.debug("skipping SCSS compilation of %s to %s", inputs, output)


# Copied from setuptools
def find_packages(where='.', exclude=()):
    """
    Return a list all Python packages found within directory 'where'.

    'where' should be supplied as a "cross-platform" (i.e. URL-style) path; it
    will be converted to the appropriate local path syntax.  'exclude' is a
    sequence of package names to exclude; '*' can be used as a wildcard in the
    names, such that 'foo.*' will exclude all subpackages of 'foo' (but not
    'foo' itself).
    """
    out = []
    stack = [(convert_path(where), '')]
    while stack:
        where, prefix = stack.pop(0)
        for name in os.listdir(where):
            fn = os.path.join(where, name)
            if ('.' not in name and os.path.isdir(fn) and os.path.isfile(os.path.join(fn, '__init__.py'))):
                out.append(prefix + name)
                stack.append((fn, prefix + name + '.'))
    for pat in list(exclude)+['ez_setup', 'distribute_setup']:
        from fnmatch import fnmatchcase
        out = [item for item in out if not fnmatchcase(item, pat)]
    return out


def find_data_files(srcdir, path='.'):
    """
    Find all files at given location and return data-files style list.

    Target directories are relative to path, source files are relative to source directory.
    """
    data_files = {}
    for filename in findall(os.path.join(srcdir, path)):
        dirname = os.path.dirname(filename)
        files = data_files.setdefault(dirname, [])
        files.append(os.path.join(path, filename))
    return data_files.items()
