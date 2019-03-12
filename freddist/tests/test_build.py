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
from shutil import rmtree
from tempfile import mkdtemp

from freddist.command.build import build
from freddist.dist import Distribution


class TestBuild(unittest.TestCase):
    """
    Test `build` command.
    """
    def setUp(self):
        self.tmp_dir = mkdtemp()
        self.srcdir = os.path.join(self.tmp_dir, 'src')
        os.mkdir(self.srcdir)

    def tearDown(self):
        rmtree(self.tmp_dir)

    def test_has_scss_files(self):
        dist = Distribution({'srcdir': self.srcdir, 'scss_files': {'outfile': ['infile']}})
        cmd = build(dist)
        cmd.ensure_finalized()

        self.assertTrue(cmd.has_scss_files())

    def test_has_scss_files_empty(self):
        dist = Distribution({'srcdir': self.srcdir})
        cmd = build(dist)
        cmd.ensure_finalized()

        self.assertFalse(cmd.has_scss_files())
