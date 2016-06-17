import os
import unittest
from shutil import rmtree
from tempfile import mkdtemp

from freddist.util import scss_compile


class TestScssCompile(unittest.TestCase):
    """
    Test `scss_compile` function.
    """
    def setUp(self):
        self.tmp_dir = mkdtemp()

    def tearDown(self):
        rmtree(self.tmp_dir)

    def assertScssOutputEqual(self, result, expected):
        # pyscss >= 1.3 appends newline at the end of file
        self.assertEqual(result.strip('\n'), expected.strip('\n'))

    def test_no_files(self):
        scss_compile({})

    def test_compile(self):
        outfile = os.path.join(self.tmp_dir, 'outfile.css')
        infile = os.path.join(self.tmp_dir, 'infile.scss')
        with open(infile, 'w') as scss:
            scss.write('$color: #fff;\nbody: {color: $color;}\n')

        scss_compile({outfile: [infile]})

        self.assertScssOutputEqual(open(outfile).read(), 'body-color:#fff\n')

    def test_compile_mkdir(self):
        outfile = os.path.join(self.tmp_dir, 'sub/outfile.css')
        infile = os.path.join(self.tmp_dir, 'infile.scss')
        with open(infile, 'w') as scss:
            scss.write('$color: #fff;\nbody: {color: $color;}\n')

        scss_compile({outfile: [infile]})

        self.assertScssOutputEqual(open(outfile).read(), 'body-color:#fff\n')

    def test_newer_outfile(self):
        outfile = os.path.join(self.tmp_dir, 'outfile.css')
        infile = os.path.join(self.tmp_dir, 'infile.scss')
        with open(infile, 'w') as scss:
            scss.write('$color: #fff;\nbody: {color: $color;}\n')
        with open(outfile, 'w') as scss:
            scss.write('NEWER OUTPUT\n')

        scss_compile({outfile: [infile]})

        self.assertScssOutputEqual(open(outfile).read(), 'NEWER OUTPUT\n')

    def test_force(self):
        outfile = os.path.join(self.tmp_dir, 'outfile.css')
        infile = os.path.join(self.tmp_dir, 'infile.scss')
        with open(infile, 'w') as scss:
            scss.write('$color: #fff;\nbody: {color: $color;}\n')
        with open(outfile, 'w') as scss:
            scss.write('NEWER OUTPUT\n')

        scss_compile({outfile: [infile]}, force=True)

        self.assertScssOutputEqual(open(outfile).read(), 'body-color:#fff\n')

    def test_dry_run(self):
        outfile = os.path.join(self.tmp_dir, 'outfile.css')
        infile = os.path.join(self.tmp_dir, 'infile.scss')
        open(infile, 'w')

        scss_compile({outfile: [infile]}, dry_run=True)

        self.assertFalse(os.path.exists(outfile))

    def test_compile_multiple_inputs(self):
        outfile = os.path.join(self.tmp_dir, 'outfile.css')
        infile = os.path.join(self.tmp_dir, 'infile.scss')
        infile2 = os.path.join(self.tmp_dir, 'infile2.scss')
        with open(infile, 'w') as scss:
            scss.write('$color: #fff;\nbody: {color: $color;}\n')
        with open(infile2, 'w') as scss:
            scss.write('div: {color: 555;}\n')

        scss_compile({outfile: [infile, infile2]})

        self.assertIn('body-color:#fff', open(outfile).read())
        self.assertIn('div-color:555', open(outfile).read())

    def test_compile_multiple_outputs(self):
        outfile = os.path.join(self.tmp_dir, 'outfile.css')
        outfile2 = os.path.join(self.tmp_dir, 'outfile2.css')
        infile = os.path.join(self.tmp_dir, 'infile.scss')
        infile2 = os.path.join(self.tmp_dir, 'infile2.scss')
        with open(infile, 'w') as scss:
            scss.write('$color: #fff;\nbody: {color: $color;}\n')
        with open(infile2, 'w') as scss:
            scss.write('div: {}\n')

        scss_compile({outfile: [infile], outfile2: [infile2]})

        self.assertScssOutputEqual(open(outfile).read(), 'body-color:#fff\n')
        self.assertScssOutputEqual(open(outfile2).read(), '\n')

    def test_compile_nonexisting(self):
        outfile = os.path.join(self.tmp_dir, 'outfile.css')
        infile = os.path.join(self.tmp_dir, 'infile.scss')

        scss_compile({outfile: [infile]})

        # pyscss create the outfile even if it fails
        self.assertTrue(os.path.exists(outfile))
        self.assertEqual(open(outfile).read(), '')
