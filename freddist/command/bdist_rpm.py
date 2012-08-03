import os
import sys

from tempfile import NamedTemporaryFile

from distutils.command.bdist_rpm import bdist_rpm as _bdist_rpm


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
    user_options = _bdist_rpm.user_options
    boolean_options = _bdist_rpm.boolean_options

    user_options.append(('build-extra-opts=', 'b',
        'extra option(s) passed to build command'))
    user_options.append(('install-extra-opts=', 'i',
        'extra option(s) passed to install command'))
    user_options.append(('dontpreservepath', None,
        'do not automatically append `--preservepath\'\
        option to `install-extra-opts\''))

    boolean_options.append('dontpreservepath')

    def initialize_options(self):
        self.build_extra_opts = None
        self.install_extra_opts = None
        self.dontpreservepath = None

        _bdist_rpm.initialize_options(self)

    def finalize_options(self):
        self.srcdir = self.distribution.srcdir
        self.set_undefined_options('bdist',
                ('dontpreservepath', 'dontpreservepath'),
                ('build_extra_opts', 'build_extra_opts'),
                ('install_extra_opts', 'install_extra_opts'),
        )

        # Prepend source directory to scripts if required
        #XXX: This stands on water as we have no idea if it should be prepended or not, so we only add it as last
        # attempt to make things work.
        for script in ('prep_script', 'build_script', 'install_script', 'clean_script', 'verify_script', 'pre_install',
                       'post_install', 'pre_uninstall', 'post_uninstall'):
            filename = getattr(self, script, None)
            if filename is None or os.path.isabs(filename):
                # We can not do anything
                continue
            abs_path = os.path.join(self.srcdir, filename)
            if not os.path.isfile(filename) and os.path.isfile(abs_path):
                setattr(self, script, abs_path)

        _bdist_rpm.finalize_options(self)

    def _make_spec_file(self):
        """
        Changes default build and install scripts.
        """
        #build_dir = os.path.join(self.rpm_base, 'BUILD')
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

            def_install = "%s install -cO2 --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES" % def_setup_call
            if self.install_extra_opts:
                def_install = '%s %s' % (def_install, self.install_extra_opts.strip())
            if '--preservepath' not in def_install:
                def_install += ' --preservepath'
            install_script_file.write(def_install)
            install_script_file.write('\n')
            # This is trick, so the file can be opened and read while we still have it opened.
            install_script_file.seek(0)

        return _bdist_rpm._make_spec_file(self)
