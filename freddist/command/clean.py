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
from distutils import log
from distutils.command.clean import clean as _clean


class clean(_clean):
    user_options = _clean.user_options + [
        ('manifest=', 'm',
         "manifest file [./MANIFEST]"),
    ]

    def initialize_options(self):
        _clean.initialize_options(self)
        self.manifest = None

    def finalize_options(self):
        _clean.finalize_options(self)
        if not self.manifest:
            self.manifest = 'MANIFEST'

    def run(self):
        _clean.run(self)

        # remove srcdir/MANIFEST file
        if os.path.exists(self.manifest):
            os.remove(self.manifest)
            log.info("%s removed" % self.manifest)
