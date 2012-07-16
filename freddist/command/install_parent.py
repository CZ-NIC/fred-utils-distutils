"""
Parent class for all install* classes
"""
import os
import re
import sys

from distutils.cmd import Command


class install_parent(Command):

    user_options = []
    boolean_options = []
    
    PRESERVEPATH = True # constant for get_root(): self.get_root(self.PRESERVEPATH)

    # Names of variables what will be copied into other classes 
    # (install_data, install_lib, install_script) by function finalize_options()
    UNDEFINED_OPTIONS = ('root', 'prefix', 'record', 'bindir', 'sbindir', 
        'sysconfdir', 'appconfdir', 'libexecdir', 'localstatedir', 'libdir',
        'pythondir', 'purelibdir', 'datarootdir', 'datadir', 'infodir', 
        'mandir', 'docdir', 'preservepath', 'no_record', 'no_pycpyo', 'no_mo',
        'no_check_deps', 'replace_path_rel', 'after_install',
        'include_scripts')

    user_options.append(('bindir=', None,
        'user executables [PREFIX/bin]'))
    user_options.append(('sbindir=', None,
        'system admin executables [PREFIX/sbin]'))
    user_options.append(('sysconfdir=', None, 
        'System configuration directory [PREFIX/etc]'))
    user_options.append(('appconfdir=', None, 
        'System configuration directory [fred] (sysconfdir/fred)'))
    user_options.append(('libexecdir=', None,
        'Program executables [PREFIX/libexec]'))
    user_options.append(('localstatedir=', None,
        'Modifiable single machine data [PREFIX/var]'))
    user_options.append(('libdir=', None,
        'object code libraries [PREFIX/lib]'))
    user_options.append(('pythondir=', None,
        'python directory [LIBDIR/python%d.%d]' %
        (sys.version_info[0], sys.version_info[1])))
    user_options.append(('purelibdir=', None,
        'python pure libraries [LIBDIR/python%d.%d/(site-packages or dist-packages)]' %
        (sys.version_info[0], sys.version_info[1])))
    user_options.append(('datarootdir=', None,
        'read only architecture-independent data root [PREFIX/share]'))
    user_options.append(('datadir=', None,
        'read only architecture-independent data [DATAROOTDIR]'))
    user_options.append(('infodir=', None,
        'info documentation [DATAROOTDIR/info]'))
    user_options.append(('mandir=', None,
        'man documentation [DATAROOTDIR/man]'))
    user_options.append(('docdir=', None,
        'documentation root [DATAROOTDIR/doc/APPNAME]'))

    user_options.append(('preservepath', None, 
        'Preserve path(s) in configuration file(s).'))
    user_options.append(('no-record', None,
        'do not record list of installed files'))
    user_options.append(('no-pycpyo', None,
        'do not create compiled pyc and optimized pyo files'))
    user_options.append(('no-mo', None,
        'do not create .mo compiled translations from gettext .po files'))
    user_options.append(('no-check-deps', None,
        'do not check dependencies'))

    user_options.append(('replace-path-rel', None,
        'When setup.py replace some path, replace it with relative path'))
    user_options.append(('after-install', None,
        'Do everything required after install (syncdb, loaddata)'))
    user_options.append(('include-scripts', None,
        'Include scripts folder.'))

    boolean_options.append('preservepath')
    boolean_options.append('no_record')
    boolean_options.append('no_pycpyo')
    boolean_options.append('no_mo')
    boolean_options.append('no_check_deps')
    boolean_options.append('replace_path_rel')
    boolean_options.append('after_install')
    boolean_options.append('include_scripts')

    dirs = ['prefix', 'bindir', 'sbindir', 'sysconfdir', 'appconfdir', 'libexecdir',
            'localstatedir', 'libdir', 'pythondir', 'purelibdir', 'datarootdir',
            'datadir', 'infodir', 'mandir', 'docdir', 'appdir', 'srcdir']

    def __init__(self, *attrs):
        self.is_bdist_mode = None
        self.is_wininst = False
        self.install_purelib = None     # for pure module distributions

        for dist in attrs:
            for name in dist.commands:
                if re.match('bdist', name): #'bdist' or 'bdist_rpm' or 'bdist_deb'
                    self.is_bdist_mode = 1 #it is bdist mode - creating a package
                    break
            if self.is_bdist_mode:
                break

    def get_actual_root(self):
        '''
        Return actual root only in case if the process is not in creation of
        the package
        '''
        return "" if self.root is None \
                        or self.preservepath \
                        or self.is_bdist_mode \
                  else \
                        self.root

    def get_root(self, apply_preservepath=None):
        "Return aways root except if the parameter apply_preservepath is set."
        root = ''
        if self.root is not None:
            root = self.root
        if apply_preservepath and (self.is_bdist_mode or self.preservepath):
            root = '' # reset root
        return root

    def initialize_options(self):
        self.prefix         = None
        self.root           = None
        
        self.bindir         = None
        self.sbindir        = None
        self.sysconfdir     = None
        self.appconfdir     = None
        self.libexecdir     = None
        self.localstatedir  = None
        self.libdir         = None
        self.pythondir      = None
        self.purelibdir     = None
        self.datarootdir    = None
        self.datadir        = None
        self.appdir         = None
        self.infodir        = None
        self.mandir         = None
        self.docdir         = None

        self.preservepath   = None
        self.no_record      = None
        self.no_pycpyo      = None
        self.no_mo          = None
        self.no_check_deps  = None

        self.replace_path_rel   = None
        self.after_install = None
        self.include_scripts = None

    def set_option_values(self):
        "Set values options"
        
        if self.root and self.prefix and self.prefix[0] != '/':
            # prefix must start with slash if the root is set
            # otherwise the prefix is duplicated
            self.prefix = '/' + self.prefix
        
        if not self.bindir:
            self.bindir = os.path.join(self.prefix, 'bin')
        if not self.sbindir:
            self.sbindir = os.path.join(self.prefix, 'sbin')
        if not self.sysconfdir:
            self.sysconfdir = os.path.join(self.prefix, 'etc')
        
        if not self.appconfdir:
            # 'fred' or self.distribution.metadata.name
            self.appconfdir = os.path.join(self.sysconfdir, 'nicms_cfg')
        else:
            if self.appconfdir[0] != "/":
                self.appconfdir = os.path.join(self.sysconfdir, self.appconfdir)
        
        if not self.libexecdir:
            self.libexecdir = os.path.join(self.prefix, 'libexec')
        if not self.localstatedir:
            self.localstatedir = os.path.join(self.prefix, 'var')
        if not self.libdir:
            self.libdir = os.path.join(self.prefix, 'lib')
        if not self.pythondir:
            self.pythondir = os.path.join(self.libdir, 'python%d.%d' % 
                    (sys.version_info[0], sys.version_info[1]))
        if not self.purelibdir:
            if 'install_lib' in self.distribution.command_options.get('install', {}):
                path = self.distribution.command_options['install']['install_lib'][1] # ('command line', 'path/path')
                self.purelibdir = path if path[:1] == '/' else os.path.join(self.prefix, path)
            else:
                self.purelibdir = os.path.join(self.pythondir, self.get_site_packages_name())

        if not self.datarootdir:
            self.datarootdir = os.path.join(self.prefix, 'share')
        if not self.datadir:
            self.datadir = self.datarootdir
        if not self.appdir:
            self.appdir = os.path.join(self.datadir, self.distribution.metadata.name)
        if not self.infodir:
            self.infodir = os.path.join(self.datarootdir, 'info')
        if not self.mandir:
            self.mandir = os.path.join(self.datarootdir, 'man')
        if not self.docdir:
            self.docdir = os.path.join(
                    self.datarootdir, 'doc', self.distribution.metadata.name)

        if self.after_install:
            # scripts must be included if you want run them after installation
            self.include_scripts = True

    def get_site_packages_name(self):
        "Returns actual name 'site_packages' (Can be also 'dist-packages')"
        if self.install_purelib is None:
            return ''
        return self.install_purelib.split('/')[-1]

    def finalize_options(self):
        self.srcdir = self.distribution.srcdir
        if not self.prefix:
            # prefix is empty - set it to the default value
            self.prefix = os.path.join('/', 'usr', 'local')
        self.set_option_values()

    def set_directories(self, prefix=None):
        if prefix:
            self.prefix = prefix
        self.set_option_values()

    def replace_pattern(self, fileOpen, fileSave=None, values = None):
        """
        Replace given patterns with new values, for example in config files.
        Patterns and new values can contain regular expressions.
        Structure of values parameter looks like:
        [(pattern_1, new_val_1), (pattern_2, new_val_2), ...]
        If targer directory does not exists, method will create it.
        """
        if not fileSave:
            fileSave = fileOpen
        body = open(fileOpen).read()

        for value in values or []:
            body = re.sub(value[0], value[1], body)
        try:
            if not os.path.isdir(os.path.dirname(fileSave)):
                os.makedirs(os.path.dirname(fileSave))
        except Exception:
            pass
        open(fileSave, 'w').write(body)

    def getDir(self, directory, no_add_root=None):
        """
        Method returs actual value of some system directory and if needed it
        prepend self.root path (depend on preservepath option).
        """
        if self.is_wininst:
            return self.install_dir
        try:
            dir_name = getattr(self, directory.lower())
        except AttributeError:
            return ''
        if no_add_root is not None:
            return dir_name
        if self.get_actual_root():
            return os.path.join(self.root, dir_name.lstrip(os.path.sep))
        return dir_name

    def getDir_nop(self, directory):
        """
        Variant of `getDir' method. Only difference is that `getDir' return
        path sometimes without self.root (if preserve path is set). `getDir_nop'
        return path always with root (but only if root is set). This method is
        used almost only inside freddist (but can be used everywhere as well).
        (rem: nop means NoPreservepath ;)
        """
        if self.is_wininst:
            return self.install_dir
        try:
            dir_name = getattr(self, directory.lower())
        except AttributeError:
            return ''
        if self.root:
            return os.path.join(self.root, dir_name.lstrip(os.path.sep))
        else:
            return dir_name

    def getDir_noprefix(self, directory):
        """
        Another ``getDir'' variant. This one return directory without prefix
        part, as well as without optional root part.
        """
        try:
            dir_name = getattr(self, directory.lower())
        except AttributeError:
            return ''
        return dir_name.replace(os.path.commonprefix(
            [self.prefix, dir_name]), '').strip(os.path.sep)

    def getDir_std(self, directory):
        """
        This version of ``getDir'' is affected by value of ``replace_path_rel''
        variable. So it can return result from standard getDir (i.e with prefix
        and maybe with root) or result from ``getDir_noprefix'' (without prefix).
        """
        if self.is_wininst:
            return self.install_dir
        if self.replace_path_rel:
            return self.getDir_noprefix(directory)
        else:
            return self.getDir(directory)

    def normalize_record(self):
        """
        Method normalize content of record file, prepend slashes (/) if needed
        and remove double slashes (//) from paths.
        """
        if self.record:
            oldRecord = open(self.record).readlines()
            newRecord = []
            for line in oldRecord:
                if not line.startswith(os.path.sep):
                    line = os.path.sep + line
                newRecord.append(os.path.normpath(line))
            open(self.record, 'w').writelines(newRecord)

    def update_record(self):
        """
        If needed prepend self.root to each path
        """
        if self.get_actual_root() and self.record:
            record = open(self.record).readlines()
            for i in range(len(record)):
                if os.path.normpath(record[i]).find(
                        os.path.normpath(self.root)) == -1:
                    record[i] = os.path.join(
                        self.root, record[i].lstrip(os.path.sep))
            open(self.record, 'w').writelines(record)

    def add_to_record(self, files):
        """
        This method take as parameter list of files, which are added
        into record file (if exists)
        """
        #proceed only if i record
        if self.record:
            record = open(self.record).readlines()
            for filename in files:
                # i must ensure, that every file from files has new line
                # character at end
                filename = filename.strip() + '\n'
                if not filename in record:
                    # file is not in record, so add it
                    record.append(filename)
            open(self.record, 'w').writelines(record)
            print "record file has been updated"

    def modify_file(self, command, filename, targetpath):
        "Modify file if any function is defined."
        if not hasattr(self.distribution, "modify_files"):
            return
        
        # modify_files: {"command": 
        #                 (("module.function", ("filename", ...)), ...), ...}
        for mfncname, files in self.distribution.modify_files.get(command, []):
            modulename, fncname = mfncname.split(".")
            fnc = getattr(self.distribution.command_obj[modulename], fncname)
            for name in files:
                if re.search("%s$" % name, filename):
                    # modify file by fnc(SRC, DEST) from SRC to DEST
                    fnc(filename, os.path.join(targetpath, name))
