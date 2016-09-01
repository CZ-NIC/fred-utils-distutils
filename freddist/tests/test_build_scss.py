import os
import unittest
from shutil import rmtree
from tempfile import mkdtemp

from freddist.command.build_scss import build_scss
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

    def test_build_scss(self):
        infile = os.path.join(self.srcdir, 'infile.scss')
        with open(infile, 'w') as scss:
            scss.write('$color: #fff;\nbody: {color: $color;}\n')

        dist = Distribution({'srcdir': self.srcdir, 'scss_files': {'outfile.css': ['infile.scss']}})
        cmd = build_scss(dist)
        cmd.build_lib = self.tmp_dir
        cmd.ensure_finalized()
        cmd.run()

        outfile = os.path.join(self.tmp_dir, 'outfile.css')
        self.assertIn('body-color:#fff', open(outfile).read())

    def test_build_scss_srcdir(self):
        os.mkdir(os.path.join(self.srcdir, 'sources'))
        infile = os.path.join(self.srcdir, 'sources', 'infile.scss')
        with open(infile, 'w') as scss:
            scss.write('@import "sources/included"\n')
        included = os.path.join(self.srcdir, 'sources', 'included.scss')
        with open(included, 'w') as included_scss:
            included_scss.write('$color: #fff;\nbody: {color: $color;}\n')

        dist = Distribution({'srcdir': self.srcdir, 'scss_files': {'outfile.css': ['sources/infile.scss']}})
        cmd = build_scss(dist)
        cmd.build_lib = self.tmp_dir
        cmd.ensure_finalized()
        cmd.run()

        outfile = os.path.join(self.tmp_dir, 'outfile.css')
        self.assertIn('body-color:#fff', open(outfile).read())

    def test_build_scss_no_files(self):
        dist = Distribution({'srcdir': self.srcdir})
        cmd = build_scss(dist)
        cmd.ensure_finalized()
        cmd.run()

    def test_get_source_files_empty(self):
        dist = Distribution({'srcdir': self.srcdir})
        cmd = build_scss(dist)
        cmd.ensure_finalized()

        self.assertEqual(cmd.get_source_files(), [])

    def test_get_source_files(self):
        scss_files = {
            'out1': ['in1.1', 'in1.2'],
            'out2': ['in2'],
        }
        dist = Distribution({'srcdir': self.srcdir, 'scss_files': scss_files})
        cmd = build_scss(dist)
        cmd.ensure_finalized()

        self.assertEqual(cmd.get_source_files(), ['in1.1', 'in1.2', 'in2'])

    def test_get_outputs_empty(self):
        dist = Distribution({'srcdir': self.srcdir})
        cmd = build_scss(dist)
        cmd.ensure_finalized()

        self.assertEqual(cmd.get_outputs(), [])

    def test_get_outputs(self):
        scss_files = {
            'out1': ['in1.1', 'in1.2'],
            'out2': ['in2'],
        }
        dist = Distribution({'srcdir': self.srcdir, 'scss_files': scss_files})
        cmd = build_scss(dist)
        cmd.build_lib = self.tmp_dir
        cmd.ensure_finalized()

        self.assertEqual(cmd.get_outputs(), [os.path.join(self.tmp_dir, 'out1'), os.path.join(self.tmp_dir, 'out2')])
