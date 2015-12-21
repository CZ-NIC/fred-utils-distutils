import os
from distutils.command.build_scripts import build_scripts as _build_scripts


class build_scripts(_build_scripts):
    def run(self):
        # Join source directory to scripts locations
        self.scripts = [os.path.join(self.distribution.srcdir, s) for s in self.scripts]
        _build_scripts.run(self)
