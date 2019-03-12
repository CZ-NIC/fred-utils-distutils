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

import unittest

from freddist.dist import Distribution


class TestDistribution(unittest.TestCase):
    """
    Test `Distribution` class.
    """
    def test_scss_files(self):
        dist = Distribution({'srcdir': '.', 'scss_files': {'outfile': ['infile']}})
        self.assertEqual(dist.scss_files, {'outfile': ['infile']})

    def test_has_scss_files_none(self):
        dist = Distribution({'srcdir': '.'})
        self.assertFalse(dist.has_scss_files())

    def test_has_scss_files_empty(self):
        dist = Distribution({'srcdir': '.', 'scss_files': {}})
        self.assertFalse(dist.has_scss_files())

    def test_has_scss_files(self):
        dist = Distribution({'srcdir': '.', 'scss_files': {'outfile': ['infile']}})
        self.assertTrue(dist.has_scss_files())
