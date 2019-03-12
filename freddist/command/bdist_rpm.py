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
import sys
from distutils.command.bdist_rpm import bdist_rpm as _bdist_rpm
from tempfile import NamedTemporaryFile


# bdist_rpm notes:
#
# new command line options:
# `--install-extra-opts'
# `--build-extra-opts'
#   both of this command are used to pass options to install (as well
#   as install_*) and build commands. For example to add prefix option,
#   and so on.
#
class bdist_rpm(_bdist_rpm):
    user_options = _bdist_rpm.user_options + [
        ('build-extra-opts=', 'b',
         "extra option(s) passed to build command"),
        ('install-extra-opts=', 'i',
         "extra option(s) passed to install command"),
    ]

    def initialize_options(self):
        self.build_extra_opts = None
        self.install_extra_opts = None

        _bdist_rpm.initialize_options(self)

    def finalize_options(self):
        self.set_undefined_options(
            'bdist',
            ('build_extra_opts', 'build_extra_opts'),
            ('install_extra_opts', 'install_extra_opts'),
        )

        # Prepend source directory to scripts if required
        # XXX: This stands on water as we have no idea if it should be prepended or not, so we only add it as last
        # attempt to make things work.
        for script in ('prep_script', 'build_script', 'install_script', 'clean_script', 'verify_script', 'pre_install',
                       'post_install', 'pre_uninstall', 'post_uninstall'):
            filename = getattr(self, script, None)
            if filename is None or os.path.isabs(filename):
                # We can not do anything
                continue
            abs_path = os.path.join(self.distribution.srcdir, filename)
            if not os.path.isfile(filename) and os.path.isfile(abs_path):
                setattr(self, script, abs_path)

        _bdist_rpm.finalize_options(self)

    def _make_spec_file(self):
        """Change default build and install scripts."""
        def_setup_call = "%s %s" % (self.python, os.path.basename(sys.argv[0]))

        if not self.build_script:
            # create build script
            build_script_file = NamedTemporaryFile(prefix='build_script')
            self.build_script = build_script_file.name

            def_build = "%s build" % def_setup_call
            if self.use_rpm_opt_flags:
                def_build = 'env CFLAGS="$RPM_OPT_FLAGS" ' + def_build
            if self.build_extra_opts:
                def_build = '%s %s' % (def_build, self.build_extra_opts.strip())
            build_script_file.write(def_build)
            build_script_file.write('\n')
            # This is trick, so the file can be opened and read while we still have it opened.
            build_script_file.seek(0)

        if not self.install_script:
            # create install script
            install_script_file = NamedTemporaryFile(prefix='install_script')
            self.install_script = install_script_file.name

            def_install = "%s install -cO2 --force --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES" % def_setup_call
            if self.install_extra_opts:
                def_install = '%s %s' % (def_install, self.install_extra_opts.strip())
            install_script_file.write(def_install)
            install_script_file.write('\n')
            # This is trick, so the file can be opened and read while we still have it opened.
            install_script_file.seek(0)

        return _bdist_rpm._make_spec_file(self)
