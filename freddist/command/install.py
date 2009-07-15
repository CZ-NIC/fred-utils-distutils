"""
This module extends distutils.install by new functrions and features .
"""
import os, re, sys, stat
from install_parent import install_parent
from distutils.command.install import install as _install


# Difference between freddist.install and distutils.install class isn't wide.
# Only new options were added. Most of them are output directory related.
# These are used so far by freddist.install_data class.
# Others are `--preservepath' and `--dont-record'. Preservepath command is used
# to cut root part of installation path (of course if `--root' is used) when
# this installation path is e.g. used in config files.
#
# Default distutils bahaviour is not to create file with installed files list.
# Freddist change it. Default is to create that file (due to uninstall class)
# and `--dont-record' option prevent this.

class install(_install, install_parent):

    user_options = _install.user_options + install_parent.user_options
    boolean_options = _install.boolean_options + install_parent.boolean_options

    DEPENDENCIES = None


    def __init__(self, *attrs):
        "Initialize install object"
        _install.__init__(self, *attrs)
        install_parent.__init__(self, *attrs)

    def initialize_options(self):
        "Initialize object attributes"
        _install.initialize_options(self)
        install_parent.initialize_options(self)


    def finalize_options(self):
        "Set defaults of attributes"
        install_parent.finalize_options(self)
        _install.finalize_options(self)
        if not self.record and not self.no_record:
            self.record = 'install.log'


    def make_preparation_for_debian_package(self, log, values):
        "Prepare folder for debian package."
        src_root = os.path.join(self.srcdir, 'doc', 'debian')
        dest_root = os.path.join(self.get_root(), 'DEBIAN')
        for name in ('control', 'conffiles', 'postinst', 'postrm'):
            filename = os.path.join(src_root, name)
            if os.path.isfile(filename):
                dest = os.path.join(dest_root, name)
                self.replace_pattern(filename, dest, values)
                if log:
                    log.info('creating %s' % dest)
                # set privileges to run
                if name in ('postinst', 'postrm'):
                    set_file_executable(dest)


    def check_dependencies(self):
        'Check some dependencies'
        if self.DEPENDENCIES is None:
            return # no any dependencies
        
        is_ok = True
        modules = {}
        missing_modules = []
        missing_packages = []
        # check modules or commands
        for module, package in self.DEPENDENCIES:
            if package is None:
                error = os.popen3("%s --version" % module, 't')[2].read()
                if error:
                    missing_modules.append(module)
                    missing_packages.append(module)
                    is_ok = False
            else:
                try:
                    modules[module] = __import__(module)
                except ImportError:
                    missing_modules.append(module)
                    missing_packages.append(package)
                    is_ok = False
        
        # check versions
        if hasattr(modules, 'django') and modules['django'].VERSION[0] < 1:
            print >> sys.stderr, 'Module django must be in version >= 1.0'
            is_ok = False

        if not is_ok:
            if len(missing_modules):
                print >> sys.stderr, "Some required modules are missing:"
                print >> sys.stderr, " ", "\n  ".join(missing_modules)
                # message only for Ubuntu
                if re.search('Ubuntu', sys.version):
                    print >> sys.stderr, "To install missing requirements "\
                            "log in as root and process following command:"
                    print >> sys.stderr, "apt-get install %s" % \
                            " ".join(missing_packages)
            raise SystemExit


    def run(self):
        "Run install process"

        if self.no_check_deps is None:
            self.check_dependencies()
    
        _install.run(self)
        self.normalize_record()




def set_file_executable(filepath):
    "Set file mode to executable"
    os.chmod(filepath, os.stat(filepath)[stat.ST_MODE] | stat.S_IEXEC | 
             stat.S_IXGRP | stat.S_IXOTH)


