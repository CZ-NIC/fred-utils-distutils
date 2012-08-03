"""
This module extends distutils.install by new functrions and features .
"""
import os
import re
import sys

from distutils.command.install import install as _install
from distutils.util import change_root, convert_path, subst_vars
from distutils.version import LooseVersion


# Difference between freddist.install and distutils.install class isn't wide.
# Only new options were added. Most of them are output directory related.
# These are used so far by freddist.install_data class.
# The others is `--dont-record'.
#
# Default distutils bahaviour is not to create file with installed files list.
# Freddist change it. Default is to create that file (due to uninstall class)
# and `--dont-record' option prevent this.


class install(_install):
    user_options = _install.user_options + [
        ('install-doc=', None,
         "installation directory for documentation"),
        ('install-libexec=', None,
         "installation directory for executables called by other programs"),
        ('install-localstate=', None,
         "installation directory for modifiable files"),
        ('install-sysconf=', None,
         "installation directory for configuration files"),
        ('no-record', None,
         "do not record list of installed files"),
        ('no-check-deps', None,
         "do not check dependencies"),
    ]

    boolean_options = _install.boolean_options + ['no_record', 'no_check_deps']

    DEPS_PYMODULE = None
    # Format: ('module_name[ [attr/function](compare number)]', ...)
    # Example:
    # DEPS_PYMODULE = ('django', 'django (>= 1.0)', 'django VERSION(>= 1.0)')
    # Explanation:
    #   compare: can be only >, >=, =, ==, <=, <
    #   attr/function: is module attribute or function returns the version
    #   value. This value is converted to string and than to LooseVersion obj.

    DEPS_COMMAND = None
    # Format: (module_name, ...)
    # Example: ('xsltproc', 'xmllint')

    DEPS_HELP = None
    # Format: {dist: {'module_name': 'package-name', ...}, ...}
    # Example:
    # DEPS_HELP = {
    #    'rpm': {'django':    'Django',
    #            'PIL':       'PIL', },
    #    'deb': {'django':    'python-django',
    #            'PIL':       'python-imaging', }}

    DEPS_COMMAND_VERSION = None
    # Format: {module_name: ('compare number', 'shell command'), ...}
    # Example:
    # DEPS_COMMAND_VERSION = {
    #    'xsltproc': (">= 10122",
    #                 "xsltproc --version | head -n 1 | awk '{print $5}'"),
    #    'xmllint': (">= 20631",
    #                "xmllint 2>&1 --version | head -n 1 | awk '{print $NF}'"),
    #}

    DEPS_HELP_COMMAND = {
        'rpm': 'yum install',
        'deb': 'apt-get install',
    }

    def initialize_options(self):
        _install.initialize_options(self)

        # Another installation directories
        self.install_doc = None
        self.install_libexec = None
        self.install_localstate = None
        self.install_sysconf = None

        self.no_record = None
        self.no_check_deps = None

        # File path replacements
        self.config_dirs = None

    def finalize_options(self):
        # Set defaults of freddist directories
        if not self.install_doc:
            self.install_doc = '$data/share/doc/$dist_name'
        if not self.install_libexec:
            self.install_libexec = '$platbase/libexec'
        if not self.install_localstate:
            self.install_localstate = '$base/var'
        if not self.install_sysconf:
            self.install_sysconf = '$base/etc'

        # Call parent
        _install.finalize_options(self)

        # Finalize freddist dirs
        self.convert_paths('doc', 'libexec', 'localstate', 'sysconf')
        if self.root is not None:
            self.change_roots('doc', 'libexec', 'localstate', 'sysconf')

        self.dump_dirs("after freddist directories")

        if not self.no_record and not self.record:
            self.record = 'install.log'

    def expand_dirs(self):
        _install.expand_dirs(self)

        # Add data directory to config vars
        self.config_vars['data'] = self.install_data

        # Expand freddist directories
        self._expand_attrs(['install_doc',
                            'install_libexec',
                            'install_localstate',
                            'install_sysconf'])

        #XXX: Store configuration directories
        # This is hack, but it is easier than removing root from final paths.
        self.config_dirs = {'doc': self.install_doc,
                            'data': self.install_data,
                            'headers': self.install_headers,
                            'localstate': self.install_localstate,
                            'libexec': self.install_libexec,
                            'platlib': self.install_platlib,
                            'purelib': self.install_purelib,
                            'scripts': self.install_scripts,
                            'sysconf': self.install_sysconf}

    def run(self):
        """
        Run install process
        """
        if self.no_check_deps is None:
            self.check_dependencies()
        _install.run(self)

        # Run file modifications
        for filename, callback in self.distribution.modify_files.iteritems():
            fullname = convert_path(self.expand_filename(filename))
            if self.root is not None:
                fullname = change_root(self.root, fullname)
            if fullname in self.get_outputs():
                getattr(self, callback)(fullname)
            else:
                self.warn("Modified file '%s' not found." % filename)

    def expand_filename(self, filename):
        """
        Expands parametrized filename.
        """
        return subst_vars(filename, self.config_dirs)

    #===== Dependency checks ===========================================================================================
    def get_help4dist(self):
        "Get help depends on distribution"
        # set the distribution depended help
        dist, help_text = None, {}
        if self.DEPS_HELP is None:
            return dist, help_text
        if re.search('Ubuntu', sys.version):
            dist = 'deb'
        elif re.search('Fedora', sys.version):
            dist = 'rpm'
        if dist and self.DEPS_HELP.has_key(dist):
            help_text = self.DEPS_HELP[dist]
        return dist, help_text

    def __check_import_module(self, module_name):
        "Check module by import"
        try:
            module = __import__(module_name)
        except ImportError:
            module = None
            self.__missing_modules.append(module_name)
        return module

    def __grab_module_version(self, module, attr_name):
        "Grab version of module using attr_name or some common names"
        module_version = None
        # load version from user defined attribute/function name or try some
        # common names of function/attribute holding version number
        for key in (attr_name, 'version', 'VERSION', '__version__'):
            if key is None:
                continue # user did not defined version attr.
            if hasattr(module, key):
                attr = getattr(module, key)
                module_version = attr() if callable(attr) else attr
                break
        if hasattr(module_version, '__iter__'):
            module_version = '.'.join([str(item) for item in module_version])
        return str(module_version)

    def __parse_compare_version(self, compare_version):
        "Parse compare signs and version number from text"
        # compare_version: '>= 1.2' or '1.2.0'
        compare, version = "=", compare_version
        # compare_version: '>= 1.2' -> ('>=', '1.2')
        match = re.match('\s*([><=]+)\s*(.+)', compare_version)
        if match:
            compare, version = match.groups()
        return compare, version

    def __check_command_version(self, module_name, compare_version, command):
        "Check command version"
        module_version = os.popen(command).read().strip()
        self.__do_version_comparation(module_name,
                                      module_version, compare_version)

    def __check_module_version(self, module, module_name, version_func,
                               compare_version):
        "Check module version"
        # Actual installed module version
        module_version = self.__grab_module_version(module, version_func)
        if module_version is None:
            self.__missing_modules.append('Version Error: Version value was '
                    'not found in module %s.' % module_name)
        else:
            self.__do_version_comparation(module_name, module_version,
                                          compare_version)

    def __do_version_comparation(self, module_name, module_version,
                                 compare_version):
        "Do version comparation"
        # parse version
        compare, version = self.__parse_compare_version(compare_version)

        vers1 = LooseVersion(module_version)
        vers2 = LooseVersion(version)

        if compare == '<':
            result = vers1 < vers2
        elif compare == '<=':
            result = vers1 <= vers2
        elif compare == '==' or compare == '=':
            result = vers1 == vers2
        elif compare == '>=':
            result = vers1 >= vers2
        elif compare == '>':
            result = vers1 > vers2
        else:
            result = None
            self.__missing_modules.append('Invalid comparation %s' % compare)

        if not result:
            self.__missing_modules.append('Module %s %s is not in required '
                    'version %s.' % (module_name, vers1, vers2))

    def check_mymodules(self):
        "Check mypthon modules. Save missing names into self.__missing_modules"
        if self.DEPS_PYMODULE is None:
            return # no any python modules dependencies
        for item in self.DEPS_PYMODULE:
            # item: "django"
            module_name, version_func, compare_version = item, None, None
            # item: "django VERSION(>= 1.2)" -> 'django', 'VERSION', '>= 1.2')
            match = re.match('(\w+)\s+(\w+)\((.+?)\)', item)
            if match:
                module_name, version_func, compare_version = match.groups()
            else:
                # item: "django (>= 1.2)" -> ('django', '>= 1.2')
                match = re.match('(\w+)\s+\((.+?)\)', item)
                if match:
                    module_name, compare_version = match.groups()

            module = self.__check_import_module(module_name)
            if module and compare_version:
                self.__check_module_version(module, module_name, version_func,
                                            compare_version)

    def check_commands(self):
        """Check shell commands. Use 'which command'.
        Save missing names into self.__missing_modules.
        """
        if self.DEPS_COMMAND is None:
            return # no any command dependencies
        for command in  self.DEPS_COMMAND:
            if os.popen("which %s" % command).read() == "":
                self.__missing_modules.append(command)
            elif self.DEPS_COMMAND_VERSION is not None and \
                                    self.DEPS_COMMAND_VERSION.has_key(command):
                compare_version, cmd = self.DEPS_COMMAND_VERSION[command]
                self.__check_command_version(command, compare_version, cmd)

    def check_dependencies(self):
        'Check application dependencies'
        self.__missing_modules = []

        # check python modules
        self.check_mymodules()
        # check shell commands
        self.check_commands()

        if len(self.__missing_modules):
            print >> sys.stderr, "Some required modules are missing or are "\
                        "not required version:"
            print >> sys.stderr, " ", "\n  ".join(self.__missing_modules)
            # get dict with help text for particular distribution
            dist, help = self.get_help4dist()
            helptext = [name for name in self.__missing_modules
                        if help.has_key(name)]
            if len(helptext):
                print >> sys.stderr, "To install missing requirements " \
                        "log in as root and process following command:"
                print >> sys.stderr, "%s %s" % (
                        self.DEPS_HELP_COMMAND.get(dist, ''),
                        " ".join(helptext))
            raise SystemExit
