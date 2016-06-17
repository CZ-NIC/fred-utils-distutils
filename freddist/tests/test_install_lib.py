import os
import unittest
from shutil import rmtree
from tempfile import mkdtemp

from freddist.command.install_lib import install_lib
from freddist.dist import Distribution


class TestBuildScss(unittest.TestCase):
    """
    Test `build_scss` command.
    """
    def setUp(self):
        self.tmp_dir = mkdtemp()
        self.srcdir = os.path.join(self.tmp_dir, 'src')
        os.mkdir(self.srcdir)

    def tearDown(self):
        rmtree(self.tmp_dir)

    def test_get_outputs_empty(self):
        dist = Distribution({'srcdir': self.srcdir})
        cmd = install_lib(dist)
        cmd.ensure_finalized()

        self.assertEqual(cmd.get_outputs(), [])

    def test_get_outputs_scss(self):
        scss_files = {
            'out1': ['in1.1', 'in1.2'],
            'sub/out2': ['in2'],
        }
        dist = Distribution({'srcdir': self.srcdir, 'scss_files': scss_files})
        cmd = install_lib(dist)
        cmd.install_dir = 'target'
        cmd.ensure_finalized()

        self.assertEqual(cmd.get_outputs(), [os.path.join('target', 'out1'), os.path.join('target', 'sub', 'out2')])

    def test_get_inputs_empty(self):
        dist = Distribution({'srcdir': self.srcdir})
        cmd = install_lib(dist)
        cmd.ensure_finalized()

        self.assertEqual(cmd.get_inputs(), [])

    def test_get_inputs_scss(self):
        scss_files = {
            'out1': ['in1.1', 'in1.2'],
            'sub/out2': ['in2'],
        }
        dist = Distribution({'srcdir': self.srcdir, 'scss_files': scss_files})
        cmd = install_lib(dist)
        cmd.ensure_finalized()
        cmd.get_finalized_command('build_scss').build_lib = 'build'

        self.assertEqual(cmd.get_inputs(), [os.path.join('build', 'out1'), os.path.join('build', 'sub', 'out2')])
