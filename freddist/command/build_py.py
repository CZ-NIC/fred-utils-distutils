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

import os
from distutils.command.build_py import build_py as _build_py


class build_py(_build_py):
    def get_package_dir(self, package):
        """Return full path to source package directory."""
        return os.path.join(self.distribution.srcdir, _build_py.get_package_dir(self, package))

    def build_package_data(self):
        """Copy data files into build directory."""
        # Rewritten to join source directory to package_data locations.
        for dummy_package, src_dir, build_dir, filenames in self.data_files:
            for filename in filenames:
                source = os.path.join(src_dir, filename)
                target = os.path.join(build_dir, filename)
                self.mkpath(os.path.dirname(target))
                self.copy_file(source, target, preserve_mode=False)
