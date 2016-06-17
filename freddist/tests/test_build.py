import os
import unittest
from shutil import rmtree
from tempfile import mkdtemp

from freddist.command.build import build
from freddist.dist import Distribution


class TestBuild(unittest.TestCase):
    """
    Test `build` command.
    """
    def setUp(self):
        self.tmp_dir = mkdtemp()
        self.srcdir = os.path.join(self.tmp_dir, 'src')
        os.mkdir(self.srcdir)

    def tearDown(self):
        rmtree(self.tmp_dir)

    def test_has_scss_files(self):
        dist = Distribution({'srcdir': self.srcdir, 'scss_files': {'outfile': ['infile']}})
        cmd = build(dist)
        cmd.ensure_finalized()

        self.assertTrue(cmd.has_scss_files())

    def test_has_scss_files_empty(self):
        dist = Distribution({'srcdir': self.srcdir})
        cmd = build(dist)
        cmd.ensure_finalized()

        self.assertFalse(cmd.has_scss_files())
