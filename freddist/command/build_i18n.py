"""distutils.command.build_i18n

Implements the Distutils 'build_i18n' command."""
import os
import sys

from distutils.core import Command
from distutils.util import convert_path

from freddist.util import i18n_compile as utils_i18n_compile


class build_i18n(Command):
    description = "\"build\" i18n files (compile and copy to build directory)"

    user_options = [
        ('build-lib=', 'd', "directory to \"build\" (copy) to"),
        ('compile-i18n', 'c', "compile .po to .mo [default]"),
        ('no-compile-i18n', None, "don't compile .po files"),
        ('force', 'f', "forcibly build everything (ignore file timestamps)"),
    ]
    boolean_options = ['compile-i18n', 'force']
    negative_opt = {'no-compile-i18n' : 'compile-i18n'}

    def initialize_options(self):
        self.build_lib = None
        self.i18n_files = None
        self.compile = 1
        self.force = None

    def finalize_options(self):
        self.set_undefined_options('build',
                                   ('build_lib', 'build_lib'),
                                   ('force', 'force'))

        # Get the distribution options that are aliases for build_i18n
        # options -- list of i18n files.
        self.i18n_files = self.distribution.i18n_files

    def get_source_files(self):
        """
        Returns list of source files under management of this command.
        """
        return self.i18n_files

    def run(self):
        if not self.i18n_files:
            return

        self.build_i18n_files()
        self.i18n_compile()

    def get_outputs(self, include_bytecode=True):
        """
        Returns list of files under build directory under management of this command.
        """
        outputs = []
        for filename in self.i18n_files:
            outfile = os.path.join(self.build_lib, filename)
            outputs.append(outfile)
            if include_bytecode:
                basename, dummy = os.path.splitext(outfile)
                outputs.append('%s.mo' % basename)
        return outputs

    def build_i18n_files(self):
        """
        Copy and compile gettext files to build directory.
        """
        for filename in self.i18n_files:
            filename = convert_path(filename)
            srcfile = os.path.join(self.distribution.srcdir, filename)
            outfile = os.path.join(self.build_lib, filename)
            self.mkpath(os.path.dirname(outfile))
            self.copy_file(srcfile, outfile, preserve_mode=0)

    def i18n_compile(self):
        """
        Compiles files inside of build directory.
        """
        if sys.dont_write_bytecode:
            self.warn('byte-compiling is disabled, skipping.')
            return
        utils_i18n_compile(self.get_outputs(include_bytecode=False), force=self.force, dry_run=self.dry_run)
