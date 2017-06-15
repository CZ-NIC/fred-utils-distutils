import os
from distutils.dist import Distribution as _Distribution
from distutils.errors import DistutilsModuleError


class Distribution(_Distribution):
    """
    Add extra arguments for setup() function.

     * modify_files
     * i18n_files - list of gettext text files to be compiled and distributed (like included in package_data).
     * scss_files - a dictionary of SCSS files - keys are CSS output files, values are lists of SCSS input files
    """

    def __init__(self, attrs=None):
        self.srcdir = os.path.normpath(attrs['srcdir'])
        self.rundir = attrs.get('rundir', os.getcwd())
        self.requires = None

        # a structure for modification of files:
        # {filename: callback, ...}
        self.modify_files = {}

        self.i18n_files = None
        self.scss_files = None

        _Distribution.__init__(self, attrs)

    def print_commands(self):
        """Fill register with commands before help is printed."""
        import freddist.command
        # try to load all commands from freddist
        for cmd_name in freddist.command.__all__:
            try:
                self.get_command_class(cmd_name)
            except DistutilsModuleError:
                continue

        _Distribution.print_commands(self)

    def get_command_packages(self):
        pkgs = _Distribution.get_command_packages(self)
        if "freddist.command" not in self.command_packages:
            pkgs.insert(0, "freddist.command")
            self.command_packages = pkgs
        return pkgs

    def find_config_files(self):
        """Search for additional `setup.cfg` file in source directory."""
        files = _Distribution.find_config_files(self)
        # Handle source-directory setup.cfg
        local_file = "setup.cfg"
        filename = os.path.join(self.srcdir, local_file)
        if os.path.isfile(filename):
            if local_file in files:
                files.insert(-1, filename)
            else:
                files.append(filename)
        return files

    # -- Distribution query methods ------------------------------------

    def has_i18n_files(self):
        return self.i18n_files and len(self.i18n_files) > 0

    def has_scss_files(self):
        return self.scss_files and len(self.scss_files) > 0
