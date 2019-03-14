#!/usr/bin/python
# -*- coding: utf-8 -*-
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

from freddist.core import setup


setup(name='fred-distutils',
      description='Fred Distutils',
      author='Aleš Doležal, CZ.NIC',
      author_email='ales.dolezal@nic.cz',
      url='http://www.nic.cz/',
      license='GPLv3+',
      platforms=['posix'],
      long_description='Fred Distutils, utilities for easier way to build packages.',
      packages=('freddist', 'freddist.command'),
      package_data={'freddist': ['README']})
