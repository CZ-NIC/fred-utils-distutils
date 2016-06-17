import unittest

from freddist.dist import Distribution


class TestDistribution(unittest.TestCase):
    """
    Test `Distribution` class.
    """
    def test_scss_files(self):
        dist = Distribution({'srcdir': '.', 'scss_files': {'outfile': ['infile']}})
        self.assertEqual(dist.scss_files, {'outfile': ['infile']})

    def test_has_scss_files_none(self):
        dist = Distribution({'srcdir': '.'})
        self.assertFalse(dist.has_scss_files())

    def test_has_scss_files_empty(self):
        dist = Distribution({'srcdir': '.', 'scss_files': {}})
        self.assertFalse(dist.has_scss_files())

    def test_has_scss_files(self):
        dist = Distribution({'srcdir': '.', 'scss_files': {'outfile': ['infile']}})
        self.assertTrue(dist.has_scss_files())
