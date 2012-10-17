import os

from distutils.dist import Distribution as _Distribution


class Distribution(_Distribution):
    def __init__(self, attrs=None):
        self.srcdir = os.path.normpath(attrs['srcdir'])
        self.rundir = attrs.get('rundir', os.getcwd())
        self.requires = None

        # a structure for modification of files:
        # {"command": (("module.function", ("filename", ...)), ...), ...}
        self.modify_files = {}

        _Distribution.__init__(self, attrs)

    def get_command_packages(self):
        pkgs = _Distribution.get_command_packages(self)
        if "freddist.command" not in self.command_packages:
            pkgs.insert(0, "freddist.command")
            self.command_packages = pkgs
        return pkgs

    def find_config_files(self):
        """
        Searches for additional `setup.cfg` file in source directory.
        """
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
