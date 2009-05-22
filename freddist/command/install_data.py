import types, os, re, sys
from distutils import util
from distutils.command.install_data import install_data as _install_data
from install_parent import install_parent

# freddist install_data came with one enhancement. It regards system directories.
# And first simple example. This is part of core.setup function:
#
# 01     setup(name='some_name',
# 02             author='your name',
# 03             #important part goes now
# 04             data_files = [
# 05                 ('SYSCONFDIR/some_name',
# 06                     [
# 07                         'file_no1.conf',
# 08                         'file_no2.conf'
# 09                     ]
# 10                 ),
# 11                 ('DOCDIR',
# 12                     [
# 13                         'document_no1.html'
# 14                     ]
# 15                 ),
# 16                 ('LOCALSTATEDIR/whatever', ),
# 17             ],
# 18             another setup stuff....,
#
# As you can see, in data_files is used some strange `SYSCONFDIR' and `DOCDIR'
# option. These are during install phase replaced by fully expanded directory
# names. For example `file_no1.conf' and `file_no2.conf' will be installed into
# `PREFIX/etc/some_name' directory. And since `PREFIX' is normally `/usr/local'
# then full path to first file will be `/usr/local/etc/some_name/file_no1.conf'.
# All these setting can be overriden by proper options.
# On line 16 is example of creating empty directory.

class install_data(_install_data, install_parent):

    user_options = _install_data.user_options + install_parent.user_options
    boolean_options = _install_data.boolean_options + install_parent.boolean_options

    user_options.append(('root=', None,
        'install everything relative to this alternate root directory'))
    user_options.append(('prefix=', None,
        'installation prefix'))

    NOT_ADD_ROOT = 1

    # directory patterns which install_data recognize
    dir_patts = ['PREFIX', 'SYSCONFDIR', 'APPCONFDIR', 'LOCALSTATEDIR', 'LIBEXECDIR',
            'LIBDIR', 'DATAROOTDIR', 'DATADIR', 'MANDIR', 'DOCDIR',
            'INFODIR', 'SBINDIR', 'BINDIR', 'LOCALEDIR', 'PYTHONDIR',
            'PURELIBDIR', 'APPDIR', 'PUREPYAPPDIR', 'SRCDIR', 'FREDCONFDIR']

    def __init__(self, *attrs):
        self.compile = 1
        self.optimize = 1
        _install_data.__init__(self, *attrs)
        install_parent.__init__(self, *attrs)

    def replaceSpecialDir(self, dir):
        """
        Method purpose is to replace `special directory' pattern passed to
        freddist.core.setup function in its data_files list. For example
        data_files could look like this:
            data_files = [('SYSCONFDIR/some_dir', ['file_no1', 'file_no2'])]
        In this example `file_no1' and `file_no2' will be copied into
        `SYSCONFDIR/some_dir' directory where `SYSCONFDIR' will be replaced
        with actual setting (by default it is `prefix/etc' where prefix is
        `/usr/local'. So whole path will be `/usr/local/etc/some_dir').
        Valid patterns are emplaced in self.`dir_patts' variable.
        """
        for str in self.dir_patts:
            s = re.search("^"+str, dir)
            if s:
                if self.is_wininst:
                    self.is_wininst = False
                    ret = os.path.join(self.getDir_noprefix(str.lower()), dir[s.end():].lstrip(os.path.sep))
                    if str in ('SYSCONFDIR', 'APPCONFDIR'):
                        ret = "+" + ret
                    self.is_wininst = True
                    return ret
                dir = self.getDir(str.lower(), install_data.NOT_ADD_ROOT) + dir[s.end():]
        return dir

    def initialize_options(self):
        _install_data.initialize_options(self)
        install_parent.initialize_options(self)
        self.prefix = None
        self.root = None
        self.record = None

    def finalize_options(self):
        _install_data.finalize_options(self)
        if 'install' in sys.argv:
            self.set_undefined_options('install', *[(k, k) for k in self.UNDEFINED_OPTIONS])
        else:
            install_parent.finalize_options(self)
        self.set_directories(self.prefix)
        if not self.record and not self.no_record:
            self.record = 'install.log'
        self.srcdir = self.distribution.srcdir
        self.rundir = self.distribution.rundir

    def run(self):
        #FREDDIST line added
        self.mkpath(self.install_dir)

        if self.no_pycpyo:
            self.compile = 0
            self.optimize = 0
        
        for f in self.data_files:
            if type(f) is types.StringType:
                #FREDDIST next line changed
                if not os.path.exists(f):
                    f = util.convert_path(os.path.join(self.srcdir, f))
                if self.warn_dir:
                    self.warn("setup script did not provide a directory for "
                              "'%s' -- installing right in '%s'" %
                              (f, self.install_dir))
                # it's a simple file, so copy it
                (out, _) = self.copy_file(f, self.install_dir)
                self.outfiles.append(out)
                self.modify_file("install_data", f, self.install_dir)

                if out.endswith('.py') and self.compile == 1:
                    os.system('python -c "import py_compile; \
                            py_compile.compile(\'%s\')"' % out)
                    self.outfiles.append(out)
                    print "creating compiled %s" % out + 'c'
                if out.endswith('.py') and self.optimize == 1:
                    os.system('python -O -c "import py_compile; \
                            py_compile.compile(\'%s\')"' % out)
                    self.outfiles.append(out)
                    print "creating optimized %s" % out + 'o'
            else:
                # it's a tuple with path to install to and a list of files
                dir = util.convert_path(self.replaceSpecialDir(f[0]))
                if not os.path.isabs(dir):
                    if self.is_wininst and dir[0] == '+':
                        dir = os.path.join(self.install_dir[:self.install_dir.rfind(os.path.sep)], dir[1:])
                    else:
                        dir = os.path.join(self.install_dir, dir)
                elif self.root:
                    dir = util.change_root(self.root, dir)
                self.mkpath(dir)

                if len(f) == 1 or f[1] == []:
                    # If there are no files listed, the user must be
                    # trying to create an empty directory, so add the
                    # directory to the list of output files.
                    self.outfiles.append(dir)
                    print "creating directory %s" % dir
                else:
                    # Copy files, adding them to the list of output files.
                    for data in f[1]:
                        #FREDDIST next line changed
                        if not os.path.exists(data):
                            data = util.convert_path(
                                    os.path.join(self.srcdir, data))
                        (out, _) = self.copy_file(data, dir)
                        self.outfiles.append(out)
                        self.modify_file("install_data", data, dir)
                        if 'bin' in out.split(os.path.sep) or\
                                'sbin' in out.split(os.path.sep) or\
                                'init.d' in out.split(os.path.sep):
                            os.chmod(out, 0755)

                        if out.endswith('.py') and self.compile == 1:
                            os.system('python -c "import py_compile; \
                                    py_compile.compile(\'%s\')"' % out)
                            self.outfiles.append(out + 'c')
                            print "creating compiled %s" % out + 'c'

                        if out.endswith('.py') and self.optimize == 1:
                            os.system('python -O -c "import py_compile; \
                                    py_compile.compile(\'%s\')"' % out)
                            self.outfiles.append(out + 'o')
                            print "creating optimized %s" % out + 'o'

