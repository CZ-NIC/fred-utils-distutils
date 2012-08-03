import os

from distutils import log
from distutils.command.clean import clean as _clean


class clean(_clean):
    user_options = _clean.user_options + [
        ('manifest=', 'm',
         "manifest file [./MANIFEST]"),
    ]

    def initialize_options(self):
        _clean.initialize_options(self)
        self.manifest = None

    def finalize_options(self):
        _clean.finalize_options(self)
        if not self.manifest:
            self.manifest = 'MANIFEST'

    def run(self):
        _clean.run(self)

        # remove srcdir/MANIFEST file
        if os.path.exists(self.manifest):
            os.remove(self.manifest)
            log.info("%s removed" % self.manifest)
