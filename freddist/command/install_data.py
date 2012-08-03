import filecmp
import os

from subprocess import check_call
from types import StringType

from distutils.command.install_data import install_data as _install_data
from distutils.util import subst_vars, change_root


class install_data(_install_data):
    """
    Data files can be inserted with replacement strings.

    data_files = [
        ('$sysconf', ('file.conf', )),
        ('$data/share', ('static.file', )),
    ]

    To change replacements, pass options to `install` command.
    """
    #TODO: Is it possible to use install_data on its own with all replacements?
    # Do not be confused, it is not easy to do so.
    user_options = _install_data.user_options + [
        ('sysconf_dir=', None,
         "installation directory for configuration files"),
    ]

    def initialize_options(self):
        _install_data.initialize_options(self)
        self.sysconf_dir = None

        # File path replacements
        self.config_dirs = None

    def finalize_options(self):
        _install_data.finalize_options(self)

        # Get file path replacements from `install` command
        self.set_undefined_options('install',
           ('config_dirs', 'config_dirs'),
           ('install_sysconf', 'sysconf_dir'),
        )

        # Convert data files
        self._expand_data_files()

    def _expand_data_files(self):
        """
        Expand variables in destination directories and joins source paths with source directory.
        """
        data_files = []
        for f in self.data_files:
            if type(f) is StringType:
                # Replace single file with tuple
                data_files.append(os.path.dirname(f), os.path.join(self.distribution.srcdir, f))
            else:
                dest, files = f
                data_files.append((self.expand_filename(dest),
                                   [os.path.join(self.distribution.srcdir, f) for f in files]))
        self.data_files = data_files

    def expand_filename(self, filename):
        new_filename = subst_vars(filename, self.config_dirs)
        # Make paths with replacements absolute
        if filename.startswith('$'):
            new_filename = change_root('/', new_filename)
        return new_filename

    def skip_sysconf_file(self, src, dest):
        """
        Requires confirmation to overwrite the file
        """
        # Force overwrite:
        if self.force or self.distribution.command_obj.get("bdist"):
            return False

        # Get full name of target
        destpath = os.path.join(dest, os.path.basename(src))

        # File does not exist or is the same
        if not os.path.isfile(destpath) or filecmp.cmp(src, destpath):
            return False

        while True:
            print "Configuration file '%s'\n" \
                  "==> Since the installation was changed (by you or the script).\n" \
                  "==> Distribution offers modified version.\n" \
                  "What do you do? Possible options are:\n" \
                  "Y or I : install the package version\n" \
                  "N or O : keep the current version\n" \
                  "D      : show the difference between the versions\n" \
                  "Ctrl+Z : switch this process in the background (return back: 'fg')\n" \
                  "The default action is to keep the current version.\n" \
                  "*** (Y/I/N/O/D/Z) [default=N] ?" % destpath,
            answer = raw_input()
            if answer == "" or answer in ("n", "N", "o", "O"):
                return True
            if answer in ("y", "Y", "i", "I"):
                return False
            if answer in ("d", "D"):
                # display difference
                check_call(["diff", src, destpath])

    def copy_file(self, infile, outfile, preserve_mode=1, preserve_times=1, link=None, level=1):
        """
        Prompt for action on configuration files.
        """
        if outfile.startswith(self.sysconf_dir) and self.skip_sysconf_file(infile, outfile):
            # Return proper result: target filename and 'copied' flag
            return os.path.join(outfile, os.path.basename(infile)), 0
        else:
            result = _install_data.copy_file(self, infile, outfile, preserve_mode=1, preserve_times=1, link=None,
                                             level=1)
            return result
