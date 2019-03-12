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

from distutils.command.bdist import bdist as _bdist


def show_formats():
    """Print list of available formats (arguments to "--format" option)."""
    from distutils.fancy_getopt import FancyGetopt
    formats = []
    for fmt in bdist.format_commands:
        formats.append(("formats=" + fmt, None,
                        bdist.format_command[fmt][1]))
    pretty_printer = FancyGetopt(formats)
    pretty_printer.print_help("List of available distribution formats:")


class bdist(_bdist):
    user_options = _bdist.user_options + [
        ('build-extra-opts=', None,
         "extra option(s) passed to build command"),
        ('install-extra-opts=', None,
         "extra option(s) passed to install command")]

    format_commands = _bdist.format_commands + ['deb']
    format_command = _bdist.format_command
    format_command.update({'deb': ('bdist_deb', "Debian distribution")})

    # Copied so 'deb' is listed in formats
    help_options = [
        ('help-formats', None,
         "lists available distribution formats", show_formats),
        ]

    def initialize_options(self):
        self.build_extra_opts = None
        self.install_extra_opts = None

        _bdist.initialize_options(self)

    def finalize_options(self):
        if not self.build_extra_opts:
            self.build_extra_opts = ''

        if not self.install_extra_opts:
            self.install_extra_opts = ''

        _bdist.finalize_options(self)
