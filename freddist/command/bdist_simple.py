import os
import shutil
import sys
import tempfile

from distutils.core import Command
from distutils.errors import DistutilsPlatformError


class bdist_simple(Command):
    rand_dir = None
    boolean_options = []

    description = 'Create "simple" built distribution'

    user_options = [('format=', 'f',
                     "archive format to create (tar, ztar, gztar, bz2tar, zip)"),
                    ('dist-dir=', 'd',
                     "directory to put final built distributions in"),
                   ]

    user_options.append(('output-file-name=', None,
        'output file archive name'))
    user_options.append(('build-extra-opts=', 'b',
        'extra option(s) passed to build command'))
    user_options.append(('install-extra-opts=', 'i',
        'extra option(s) passed to install command'))
    user_options.append(('dontpreservepath', None,
        'do not automatically append `--preservepath\'\
        option to `install-extra-opts\''))

    boolean_options = ['keep-temp', 'dontpreservepath']

    default_format = {
            'posix': 'gztar',
            'nt': 'zip',
            'os2': 'zip' }

    def initialize_options(self):
        # exampleeeeeeeee
        # self.relative = 0
        self.bdist_dir = None
        self.format = None
        self.dist_dir = None

        self.output_file_name = None
        self.build_extra_opts = None
        self.install_extra_opts = None
        self.dontpreservepath = None

    def finalize_options(self):
        if self.bdist_dir is None:
            bdist_base = self.get_finalized_command('bdist').bdist_base
            self.bdist_dir = os.path.join(bdist_base, 'dumb')

        if self.format is None:
            try:
                self.format = self.default_format[os.name]
            except KeyError:
                raise DistutilsPlatformError, \
                      ("don't know how to create dumb built distributions " +
                       "on platform %s") % os.name

        self.set_undefined_options('bdist',
                ('dist_dir', 'dist_dir'),
                ('dontpreservepath', 'dontpreservepath'),
                ('build_extra_opts', 'build_extra_opts'),
                ('install_extra_opts', 'install_extra_opts'),
                )
        if not self.output_file_name:
            self.output_file_name = self.distribution.metadata.name \
                    + "-" \
                    + self.distribution.metadata.version
        self.srcdir = self.distribution.srcdir

    def getRandTempDir(self):
        if self.rand_dir != None:
            return self.rand_dir
        else:
            self.rand_dir = os.path.join(tempfile.mkdtemp(
                prefix=self.output_file_name + "_"),
                self.output_file_name)
            # self.rand_dir = os.path.join(tempfile.mkdtemp(
                # prefix=self.distribution.get_name() + "_"),
                # self.distribution.get_name() + "_" + self.distribution.get_version())
            return self.rand_dir
        #return os.path.join('/tmp', self.distribution.get_name())

    def run(self):
        cmd = "python %s install %s --prefix=%s --sysconfdir=%s --bindir=%s --sbindir=%s \
                --libdir=%s --datarootdir=%s --replace-path-rel" % (
                sys.argv[0],
                self.install_extra_opts,
                self.getRandTempDir(),
                os.path.join(self.getRandTempDir(), 'data_files', 'conf'),
                self.getRandTempDir(),
                self.getRandTempDir(),
                os.path.join(self.getRandTempDir(), 'data_files', 'lib'),
                os.path.join(self.getRandTempDir(), 'data_files'))

        os.popen(cmd, "w")

        cwd = os.getcwd()

        if not os.path.exists(self.dist_dir):
            os.makedirs(self.dist_dir)

        if self.format == 'tar':
            cmd = 'tar cf %s.tar %s' % (os.path.join(
                cwd,
                self.dist_dir,
                self.output_file_name),
                os.path.basename(self.getRandTempDir()))
        elif self.format == 'bz2tar':
            cmd = 'tar cjf %s.tar.bz2 %s' % (os.path.join(
                cwd,
                self.dist_dir,
                self.output_file_name),
                os.path.basename(self.getRandTempDir()))
        elif self.format == 'gztar':
            cmd = 'tar czf %s.tar.gz %s' % (os.path.join(
                cwd,
                self.dist_dir,
                self.output_file_name),
                os.path.basename(self.getRandTempDir()))
        elif self.format == 'ztar':
            cmd = 'tar cZf %s.tar.Z %s' % (os.path.join(
                cwd,
                self.dist_dir,
                self.output_file_name),
                os.path.basename(self.getRandTempDir()))
        elif self.format == 'zip':
            cmd = 'zip -r %s.zip %s' % (os.path.join(
                cwd,
                self.dist_dir,
                self.output_file_name),
                os.path.basename(self.getRandTempDir()))

        os.chdir(os.path.dirname(self.getRandTempDir()))

        os.popen(cmd)
        os.chdir(cwd)

        shutil.rmtree(os.path.dirname(self.getRandTempDir()))
