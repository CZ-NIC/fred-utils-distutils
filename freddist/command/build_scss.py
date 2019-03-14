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

"""Implements the Distutils 'build_scss' command."""
import os
from distutils.core import Command
from distutils.util import convert_path

from freddist.util import scss_compile as utils_scss_compile


class build_scss(Command):
    description = "\"build\" SCSS files (compile to build directory)"

    user_options = [
        ('build-lib=', 'd', "directory to \"build\" to"),
        ('force', 'f', "forcibly build everything (ignore file timestamps)"),
    ]
    boolean_options = ['force']

    def initialize_options(self):
        self.build_lib = None
        self.scss_files = None
        self.force = None

    def finalize_options(self):
        self.set_undefined_options('build',
                                   ('build_lib', 'build_lib'),
                                   ('force', 'force'))

        # Get the distribution options that are aliases for build_scss
        # options -- list of SCSS files.
        self.scss_files = self.distribution.scss_files

    def get_source_files(self):
        """Return list of source files under management of this command."""
        if not self.scss_files:
            return []

        return [i for inputs in self.scss_files.values() for i in inputs]

    def run(self):
        if not self.scss_files:
            return

        self.scss_compile()

    def get_outputs(self):
        """Return list of files under build directory under management of this command."""
        if not self.scss_files:
            return []

        outputs = []
        for filename in self.scss_files.keys():
            outfile = os.path.join(self.build_lib, filename)
            outputs.append(outfile)
        return outputs

    def scss_compile(self):
        """Compile files to build directory."""
        scss_files = {}
        for output, inputs in self.scss_files.items():
            outfile = os.path.join(self.build_lib, convert_path(output))
            infiles = [os.path.join(self.distribution.srcdir, convert_path(i)) for i in inputs]
            scss_files[outfile] = infiles
        utils_scss_compile(scss_files, srcdir=self.distribution.srcdir, force=self.force, dry_run=self.dry_run)
