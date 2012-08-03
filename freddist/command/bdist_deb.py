#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import re

from distutils.core import Command

from freddist.util import check_call


# name of package release
UBUNTU_NAME = 'jaunty'


class bdist_deb(Command):
    description = "create a Debian distribution"

    user_options = [
        ('bdist-base=', None, "base directory for creating build"),
        ('epoch=', None, "Program epoch [0]"),
        ('package-version=', None, "Package version [1]"),
        ('release=', None, "Debian release [%s]" % UBUNTU_NAME),
        ('build-int=', None, "Package build int [1]"),
        ('platform=', None, "OS platform [all]"),
        ('install-extra-opts=', 'i', 'extra option(s) passed to install command'),
    ]

    def initialize_options (self):
        self.bdist_base = None
        self.epoch = None
        self.package_version = None
        self.release = None
        self.build_int = None
        self.platform = None
        self.install_extra_opts = None

    def finalize_options (self):
        if not self.bdist_base:
            self.bdist_base = 'deb'
        elif self.bdist_base == "build":
            raise SystemExit("Error --bdist-base: Folder name 'build' is " \
                             "reserved for building process.")

        # epoch zero is shown empty string "" otherwice "NUMBER:"
        if not self.epoch:
            self.epoch = ''
        else:
            self.epoch = '%s:' % self.epoch
        if not self.package_version:
            self.package_version = '1'
        if not self.release:
            self.release = UBUNTU_NAME
        if not self.build_int:
            self.build_int = '1'
        if not self.platform:
            self.platform = 'all' # architecture

        # it is necessary overwrite extra-opts if the command 'bdist' is set
        if self.distribution.command_options.has_key('bdist'):
            bdist_val = self.distribution.command_options['bdist']
            if bdist_val.has_key('install_extra_opts'):
                self.install_extra_opts = bdist_val['install_extra_opts'][1]

    def run (self):
        # check if exists tool for create deb package
        if os.popen("which dpkg-deb").read() == "":
            raise SystemExit, "Error: dpkg-deb missing. "\
                              "It is required for create deb."

        # check debian/control
        controlpath = os.path.join(self.distribution.srcdir, "doc", "debian", "control")
        if not os.path.isfile(controlpath):
            raise SystemExit, "Error: %s missing." % controlpath

        # other options must be set in setup.cfg
        command = ['python', os.path.join(self.distribution.srcdir, 'setup.py'), 'install',
                   self.install_extra_opts or '', '--no-compile', '--no-check-deps', '--root', self.bdist_base]
        if not check_call(command):
            return

        # prepare package name and find paths
        version = "%s%s-%s~%s+%s" % (self.epoch, self.distribution.get_version(), self.package_version, self.release,
                                     self.build_int)
        deb_name = "%s_%s_%s" % (self.distribution.get_name(), version, self.platform)
        build_dir = os.path.abspath(self.bdist_base)

        # modify control file
        controlpath = os.path.join(build_dir, "DEBIAN", "control")
        control_data = open(controlpath, 'r').read()
        control_data = re.sub('PACKAGE_VERSION', version, control_data)
        control_data = re.sub('PLATFORM', self.platform, control_data)
        open(controlpath, 'w').write(control_data)

        command = 'find %s -type f ! -regex "^DEBIAN/" -exec md5sum {} >> %s/DEBIAN/md5sums \;' % (build_dir, build_dir)
        if not check_call(command):
            return
        if not check_call(['dpkg-deb', '-b', build_dir, '%s.deb' % deb_name]):
            return
