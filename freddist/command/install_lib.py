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

from distutils.command.install_lib import install_lib as _install_lib


class install_lib(_install_lib):
    def build(self):
        _install_lib.build(self)
        if not self.skip_build:
            if self.distribution.has_i18n_files():
                self.run_command('build_i18n')
            if self.distribution.has_scss_files():
                self.run_command('build_scss')

    def get_outputs(self):
        outputs = _install_lib.get_outputs(self)
        i18n_outputs = self._mutate_outputs(self.distribution.has_i18n_files(),
                                            'build_i18n', 'build_lib',
                                            self.install_dir)
        scss_outputs = self._mutate_outputs(self.distribution.has_scss_files(),
                                            'build_scss', 'build_lib',
                                            self.install_dir)
        return outputs + i18n_outputs + scss_outputs

    def get_inputs(self):
        inputs = _install_lib.get_inputs(self)
        if self.distribution.has_i18n_files():
            build_i18n = self.get_finalized_command('build_i18n')
            inputs.extend(build_i18n.get_outputs())
        if self.distribution.has_scss_files():
            build_scss = self.get_finalized_command('build_scss')
            inputs.extend(build_scss.get_outputs())
        return inputs
