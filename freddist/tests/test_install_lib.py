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

from freddist.command.install_lib import install_lib
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

    def test_get_outputs_empty(self):
        dist = Distribution({'srcdir': self.srcdir})
        cmd = install_lib(dist)
        cmd.ensure_finalized()

        self.assertEqual(cmd.get_outputs(), [])

    def test_get_outputs_scss(self):
        scss_files = {
            'out1': ['in1.1', 'in1.2'],
            'sub/out2': ['in2'],
        }
        dist = Distribution({'srcdir': self.srcdir, 'scss_files': scss_files})
        cmd = install_lib(dist)
        cmd.install_dir = 'target'
        cmd.ensure_finalized()

        self.assertEqual(cmd.get_outputs(), [os.path.join('target', 'out1'), os.path.join('target', 'sub', 'out2')])

    def test_get_inputs_empty(self):
        dist = Distribution({'srcdir': self.srcdir})
        cmd = install_lib(dist)
        cmd.ensure_finalized()

        self.assertEqual(cmd.get_inputs(), [])

    def test_get_inputs_scss(self):
        scss_files = {
            'out1': ['in1.1', 'in1.2'],
            'sub/out2': ['in2'],
        }
        dist = Distribution({'srcdir': self.srcdir, 'scss_files': scss_files})
        cmd = install_lib(dist)
        cmd.ensure_finalized()
        cmd.get_finalized_command('build_scss').build_lib = 'build'

        self.assertEqual(cmd.get_inputs(), [os.path.join('build', 'out1'), os.path.join('build', 'sub', 'out2')])
