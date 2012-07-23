# -*- coding: utf-8 -*-
# Author: Douglas Creager <dcreager@dcreager.net>
# Changed by CZ.NIC to suit the need
# This file is placed into the public domain.

# Calculates the current version number. If possible, this is the
# output of “git describe”, modified to conform to the versioning
# scheme that setuptools uses. If “git describe” returns an error
# (most likely because we're in an unpacked copy of a release tarball,
# rather than in a git working copy), then we fall back on reading the
# contents of the RELEASE-VERSION file.
#
# To use this script, simply import it your setup.py file, and use the
# results of get_git_version() as your package version:
#
# from version import *
#
# setup(
# version=get_git_version(),
# .
# .
# .
# )
#
# This will automatically update the RELEASE-VERSION file, if
# necessary. Note that the RELEASE-VERSION file should *not* be
# checked into git; please add it to your top-level .gitignore file.
#
# You'll probably want to distribute the RELEASE-VERSION file in your
# sdist tarballs; to do this, just create a MANIFEST.in file that
# contains the following line:
#
# include RELEASE-VERSION

__all__ = ("get_git_version")

import os

from subprocess import Popen, PIPE


def call_git_describe(srcdir=None, abbrev=4):
    ''' Calls git describe returns last tag on branch where we are.
        If no tags found, git describe is run again
        with --always argument and returns 'g$revision' instead.
    '''
    try:
        command = ['git', 'describe', '--abbrev=%d' % abbrev, '--tags']
        if srcdir: # set git options for where is git repository and working tree (must be before describe command)
            command.insert(1, '--git-dir=%s' % os.path.join(srcdir, '.git'))
            command.insert(1, '--work-tree=%s' % srcdir)
        popen = Popen(command, stdout=PIPE, stderr=PIPE)
        if popen.wait():
            # non-zero returncode -> no tags found, run again with --always
            command.append('--always')
            popen = Popen(command, stdout=PIPE, stderr=PIPE)
            # return git revision with 'g' prefix similar to what --long does for tags
            line = 'g' + popen.stdout.readlines()[0]
        else:
            line = popen.stdout.readlines()[0]
        return line.strip()
    except:
        return None


def read_release_version(srcdir=None):
    try:
        filename = "RELEASE-VERSION"
        if srcdir:
            filename = os.path.join(srcdir, filename)
        file_obj = open(filename, "r")

        try:
            version = file_obj.readlines()[0]
            return version.strip()

        finally:
            file_obj.close()

    except:
        return None


def write_release_version(version, srcdir=None):
    filename = "RELEASE-VERSION"
    if srcdir:
        filename = os.path.join(srcdir, filename)
    file_obj = open(filename, "w")
    file_obj.write("%s\n" % version)
    file_obj.close()


def get_git_version(srcdir=None, abbrev=4):
    # Read in the version that's currently in RELEASE-VERSION.

    release_version = read_release_version(srcdir)

    # First try to get the current version using “git describe”.

    version = call_git_describe(srcdir, abbrev)

    # If that doesn't work, fall back on the value that's in
    # RELEASE-VERSION.

    if version is None:
        version = release_version

    # If we still don't have anything, that's an error.

    if version is None:
        raise ValueError("Cannot find the version number!")

    # If the current version is different from what's in the
    # RELEASE-VERSION file, update the file to be current.

    if version != release_version:
        write_release_version(version, srcdir)

    # Finally, return the current version.

    return version


if __name__ == "__main__":
    print get_git_version()
