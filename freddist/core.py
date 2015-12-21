"""
freddist.core
"""
import os
import sys
from distutils.core import setup as _setup

from freddist.dist import Distribution
from freddist.version import get_git_version


def setup(**attrs):
    """
    Replace default Distribution class.
    """
    srcdir = attrs.setdefault('srcdir', os.path.dirname(sys.argv[0]))
    # Get version from git, if available
    if 'version' not in attrs:
        try:
            attrs['version'] = get_git_version(srcdir)
        except ValueError:
            pass
    # Set default Distribution class
    attrs.setdefault('distclass', Distribution)
    # Set default script_name full
    attrs.setdefault('script_name', sys.argv[0])
    # Call original 'setup()'
    _setup(**attrs)
