#
# Copyright (C) 2009-2019  CZ.NIC, z. s. p. o.
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

"""Module for freddist.core."""
import os
import sys
from distutils.core import setup as _setup

from freddist.dist import Distribution
from freddist.version import get_git_version


def setup(**attrs):
    """Replace default Distribution class."""
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
