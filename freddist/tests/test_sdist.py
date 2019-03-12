#
# Copyright (C) 2016-2019  CZ.NIC, z. s. p. o.
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

import os
import unittest
from distutils.filelist import FileList
from shutil import rmtree
from tempfile import mkdtemp

from freddist.command.sdist import sdist
from freddist.dist import Distribution


class TestBuildScss(unittest.TestCase):
    """
    Test `build_scss` command.
    """
    def setUp(self):
        self.tmp_dir = mkdtemp()
        self.srcdir = os.path.join(self.tmp_dir, 'src')
        os.mkdir(self.srcdir)

    def tearDown(self):
        rmtree(self.tmp_dir)

    def test_add_defaults_empty(self):
        readme = os.path.join(self.srcdir, 'README')
        setup_py = os.path.join(self.srcdir, 'setup.py')
        open(readme, 'w')
        open(setup_py, 'w')
        dist = Distribution({'srcdir': self.srcdir, 'script_name': 'setup.py'})
        cmd = sdist(dist)
        cmd.ensure_finalized()

        cmd.filelist = FileList()
        cmd.add_defaults()

        self.assertEqual(cmd.filelist.files, [readme, setup_py])

    def test_add_defaults_scss(self):
        readme = os.path.join(self.srcdir, 'README')
        setup_py = os.path.join(self.srcdir, 'setup.py')
        open(readme, 'w')
        open(setup_py, 'w')
        open(os.path.join(self.srcdir, 'in.scss'), 'w')
        dist = Distribution({'srcdir': self.srcdir, 'scss_files': {'out.css': ['in.scss']}, 'script_name': 'setup.py'})
        cmd = sdist(dist)
        cmd.ensure_finalized()

        cmd.filelist = FileList()
        cmd.add_defaults()

        self.assertEqual(cmd.filelist.files, [readme, setup_py, 'in.scss'])
