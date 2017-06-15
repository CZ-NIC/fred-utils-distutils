import os
from distutils.command.build_py import build_py as _build_py


class build_py(_build_py):
    def get_package_dir(self, package):
        """Return full path to source package directory."""
        return os.path.join(self.distribution.srcdir, _build_py.get_package_dir(self, package))

    def build_package_data(self):
        """Copy data files into build directory."""
        # Rewritten to join source directory to package_data locations.
        for dummy_package, src_dir, build_dir, filenames in self.data_files:
            for filename in filenames:
                source = os.path.join(src_dir, filename)
                target = os.path.join(build_dir, filename)
                self.mkpath(os.path.dirname(target))
                self.copy_file(source, target, preserve_mode=False)
