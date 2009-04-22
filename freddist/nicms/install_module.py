#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import re
import shutil
from freddist import file_util
from freddist.command.install import install



class NicmsModuleInstall(install):
    """Install class for Fred NICMS modules. Provides all necessary options,
    check dependencies, update cron scripts, show individual help and
    run install process with necessary functions.
    """

    # must be set in descendant
    PROJECT_NAME = None # e.g. 'fred-nicms-payments'
    PACKAGE_NAME = None # e.g. 'fred-nicms-payments'
    PACKAGE_VERSION = None # '1.5.1'
    MODULE_NAME = None # 'payments'
    SCRIPT_CREATE_DB = None # 'fred-nicms-MODULENAME-create-tables'
    # subfolder where is script SCRIPT_CREATE_DB
    SCRIPTS_DIR = 'scripts'
    
    # name of the main settings file (in /etc/fred)
    BASE_CONFIG_NAME = 'nicms_cfg'
    # name of folder for settigns of the dynamic modules
    BASE_CONFIG_MODULE_NAME = 'nicms_cfg_modules'
    # name of base package
    BASE_CMS_NAME = 'fred-nicms'

    # os.path.join(BASE_CMS_NAME, 'apps', MODULE_NAME)
    BASE_APPS_MODULE_DIR = None
    log = None

    # folder where is hold settings file modified by setup
    # it must by same as path in doc/debian/postinst.install
    CONFIGURATION_DIR = 'configuration'
    
    
    user_options = install.user_options
    user_options.append(('fred-nicms=', None, 'fred-nicms path '\
                                                    '[PURELIBDIR/fred-nicms]'))
    user_options.append(('fred-nicms-conf-filepath=', None, 
        'fred-nicms settings file path [SYSCONFDIR/%s]' % BASE_CONFIG_NAME))
    user_options.append(('fred-nicms-conf-modules-dir=', None, 
        'fred-nicms settings file path [SYSCONFDIR/%s]' % 
                                                    BASE_CONFIG_MODULE_NAME))


    def initialize_options(self):
        install.initialize_options(self)
        self.fred_nicms = None
        self.fred_nicms_conf_filepath = None
        self.fred_nicms_conf_modules_dir = None


    def finalize_options(self):
        install.finalize_options(self)
        
        # path to fred-nicms base folder (/usr/share/fred-nicms)
        if self.fred_nicms is None:
            self.fred_nicms = os.path.join(
             os.path.split(self.getDir('PUREPYAPPDIR'))[0], self.BASE_CMS_NAME)

        # prepare conf_path
        base, folder_name = os.path.split(self.getDir('APPCONFDIR'))
        if folder_name == self.PACKAGE_NAME:
            conf_path = os.path.join(base, self.BASE_CMS_NAME)
        else:
            conf_path = os.path.join(base, folder_name)

        # path to fred-nicms base settings file (/etc/fred/nicms_cfg.py)
        if self.fred_nicms_conf_filepath is None:
            self.fred_nicms_conf_filepath = os.path.join(conf_path, 
                                                         self.BASE_CONFIG_NAME)

        # path to path to fred-nicms settings modules folder 
        # (/etc/fred/nicms_cfg_modules)
        if self.fred_nicms_conf_modules_dir is None:
            self.fred_nicms_conf_modules_dir = os.path.join(conf_path, 
                                                self.BASE_CONFIG_MODULE_NAME)
        
        # can be same as fred_nicms or different:
        # share_dir:  '/usr/share/fred-nicms'
        # fred_nicms: '/usr/share/fred-nicms' or 
        #             '/usr/local/lib/python2.5/site-packages/fred-nicms/'
        self.share_dir = os.path.join(self.getDir('DATADIR'),
                                      self.BASE_CMS_NAME)



    def check_dependencies(self):
        'Check some dependencies'
        # check base files
        for filepath in (
                os.path.join(self.fred_nicms, 'manage.py'), 
                self.fred_nicms_conf_filepath + '.py', 
            ):
            if not os.path.isfile(filepath):
                raise SystemExit, "Error: File %s missing." % filepath


    def update_settings(self):
        "Make any modifications in settings"


    def update_scritps(self):
        values = [('MODULE_ROOT', self.fred_nicms)]
        for src, dest in (
            (os.path.join('cron.d', 'run.install'), 
             os.path.join('cron.d', 'run.txt')), 
            ):
            if os.path.isfile(src):
                self.replace_pattern(src, dest, values)
                if self.log:
                    self.log.info('File %s was updated.' % dest)


    @staticmethod
    def show_after_help(commands):
        "Print individual text after default help"
        if len(commands) and issubclass(commands[0], install):
            print '   or: python setup.py install --localstatedir=/var '\
               '--prefix=/usr --purelibdir=/usr/share --sysconfdir=/etc/fred '\
               '--no-check-deps --prepare-debian-package --root=/tmp/package'



    def run(self):
        if self.no_check_deps is None:
            self.check_dependencies()

        # prepare files before move
        self.update_settings()
        self.update_scritps()

        # copy files
        install.run(self)

        # remove subsidiary file
        filepath = os.path.join(self.getDir_nop('DOCDIR'), 
                                    'cron.d', 'run.install')
        if os.path.isfile(filepath):
            os.unlink(filepath)

        if self.prepare_debian_package:
            self.make_preparation_for_debian_package(self.log, (
                ('MODULE_ROOT', self.fred_nicms),
                ('MODULES_CONF_DIR', self.fred_nicms_conf_modules_dir), 
                ('BINDIR', self.getDir('BINDIR')), 
                ('PACKAGE_VERSION', self.PACKAGE_VERSION), 
                ('INSTALLED_SIZE', file_util.get_folder_kb_size(
                                                            self.get_root())), 
                )
            )
            print "Next steps are:"
            print self.get_info_for_create_package(self.PROJECT_NAME, 
                                                   self.PACKAGE_VERSION)
            return

        # prepare command for create database
        command = "%s/%s %s" % (self.getDir_nop('BINDIR'), 
                                self.SCRIPT_CREATE_DB, self.fred_nicms)
        dest = os.path.join(self.fred_nicms_conf_modules_dir, '%s.py' % 
                            self.MODULE_NAME)
        # first try to open a settings modified by setup
        src = os.path.join(self.CONFIGURATION_DIR, 'settings.py')
        if not os.path.isfile(src):
            # if does not exists the modified copy use default
            src = 'settings.py'
        
        # create database
        if self.perform_all_install_steps:
            # copy settings into destination file
            print "Copy configuration file into", dest
            shutil.copy(src, dest)
            if self.SCRIPT_CREATE_DB:
                print "Run command", command
                os.system(command) # run create-database
        else:
            print "The remaining steps to complete the installation:"
            print "(Use --perform-all-install-steps for make all these "\
                    "command in one step)"
            print
            print "1. Copy settings file: cp source destination"
            print "cp %s %s" % (src, dest)
            print
            print "2. Run script: %s path-to-manage.py" % self.SCRIPT_CREATE_DB
            print command




class NicmsModuleInstallUpdateSettings(NicmsModuleInstall):
    """Extends NicmsModuleInstall for function what modify paths in
    settings file.
    """

    def update_settings(self):
        "Make path modifications in settings"
        configname, configname_install = ('settings.py', 'settings.py.install')
        
        if not os.path.isfile(configname_install):
            shutil.copy(configname, configname_install)
            if self.log:
                self.log.info('File %s was renamed to %s.' % (configname, 
                                                     configname_install))
        
        body = open(configname_install).read()
        
        body = re.sub('BASE_SHARE_DIR\s*=\s*(.+)', 
                      'BASE_SHARE_DIR = "%s"' % self.share_dir, body, 1)
        
        if not os.path.isdir(self.CONFIGURATION_DIR):
            os.mkdir(self.CONFIGURATION_DIR)

        settings = os.path.join(self.CONFIGURATION_DIR, configname)
        open(settings, 'w').write(body)
        if self.log:
            self.log.info('File %s was updated.' % settings)
