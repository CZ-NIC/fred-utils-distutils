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

from distutils.command.build import build as _build


class build(_build):
    """Has two more phases - i18n compilation and SCSS compilation."""

    def has_i18n_files(self):
        return self.distribution.has_i18n_files()

    def has_scss_files(self):
        return self.distribution.has_scss_files()

    sub_commands = _build.sub_commands
    sub_commands.append(('build_i18n', has_i18n_files))
    sub_commands.append(('build_scss', has_scss_files))
