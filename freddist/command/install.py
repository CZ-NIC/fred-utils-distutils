import os, re, sys, stat
from install_parent import install_parent
from distutils.command.install import install as _install
from distutils.debug import DEBUG
from distutils.util import convert_path, subst_vars, change_root


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

    def __init__(self, *attrs):
        _install.__init__(self, *attrs)
        install_parent.__init__(self, *attrs)

    def initialize_options(self):
        _install.initialize_options(self)
        install_parent.initialize_options(self)


    def finalize_options(self):
        install_parent.finalize_options(self)
        _install.finalize_options(self)
        if not self.record and not self.no_record:
            self.record = 'install.log'


    def make_preparation_for_debian_package(self, log, values):
        "Prepare folder for debian package. Parameter values is in format (('FROM_PATTERN', 'to-value'), ...)"
        
        src_root = os.path.join('doc', 'debian')
        dest_root = os.path.join(self.get_root(), 'DEBIAN')
        
        for src, dest in (
            (os.path.join(src_root, 'postinst.install'), 
             os.path.join(dest_root, 'postinst')), 
            
            (os.path.join(src_root, 'postrm.install'), 
             os.path.join(dest_root, 'postrm')), 

            (os.path.join(src_root, 'control.install'), 
             os.path.join(dest_root, 'control')), 
            
            ):
            self.replace_pattern(os.path.join(self.srcdir, src), 
                                 os.path.join(self.srcdir, dest), values)
            if log:
                log.info('creating %s' % dest)
        
        # set privileges to run
        for name in ('postinst', 'postrm'):
            set_file_executable(os.path.join(dest_root, name))


    def get_info_for_create_package(self, project_name, package_version):
        body = []
        body.append("cd %s" % self.get_root())
        body.append('find * -type f|grep -v "^DEBIAN/"|while read x;do md5sum "${x}";done > DEBIAN/md5sums')
        body.append("cd ..")
        body.append("dpkg-deb -b %s %s_%s-1~hardy+1_all.deb" % (self.get_root(), project_name, package_version))
        return '\n'.join(body)
    


    def run(self):
        _install.run(self)
        self.normalize_record()




def set_file_executable(filepath):
    "Set file mode to executable"
    os.chmod(filepath, os.stat(filepath)[stat.ST_MODE] | stat.S_IEXEC | 
             stat.S_IXGRP | stat.S_IXOTH)


