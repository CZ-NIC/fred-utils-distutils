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
    
    # name of folder for settigns of the dynamic modules
    BASE_CONFIG_MODULE_NAME = 'nicms_cfg_modules'
    # name of base package
    BASE_CMS_NAME = 'fred-nicms'

    # os.path.join(BASE_CMS_NAME, 'apps', MODULE_NAME)
    BASE_APPS_MODULE_DIR = None
    log = None
    
    user_options = install.user_options
    user_options.append(('fred-nicms=', None, 'fred-nicms path '\
                                                    '[PURELIBDIR/fred-nicms]'))
    user_options.append(('fred-nicms-confdir=', None, 
        'fred-nicms settings file path [SYSCONFDIR/%s]' % 
                                                    BASE_CONFIG_MODULE_NAME))

##    dirs = install.dirs + ['fredconfdir'] # FREDCONFDIR

    def initialize_options(self):
        install.initialize_options(self)
        self.fred_nicms = None
        self.fredconfdir = None


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
        
        # path to path to fred-nicms settings modules folder 
        # (/etc/fred/nicms_cfg_modules)
        if self.fredconfdir is None:
            self.fredconfdir = os.path.join(conf_path, 
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
        for filepath in (os.path.join(self.fred_nicms, 'manage.py'), ):
            if not os.path.isfile(filepath):
                raise SystemExit, "Error: File %s missing." % filepath


    def update_settings(self, src, dest):
        "Make any modifications in settings"


    def update_scripts(self, src, dest):
        "Update file by values"
        values = [('MODULE_ROOT', self.fred_nicms)]
        self.replace_pattern(src, dest, values)
        if self.log:
            self.log.info('File %s was updated.' % dest)


    def copy_settings(self, src, dest):
        "Create module settings MODULE_NAME from settings.py"
        self.update_scripts(src, os.path.join(os.path.dirname(src), "%s.py" % 
                                              self.MODULE_NAME))


    @staticmethod
    def show_after_help(commands):
        "Print individual text after default help"
        if len(commands) and issubclass(commands[0], install):
            print '   or: python setup.py install --localstatedir=/var '\
               '--prefix=/usr --purelibdir=/usr/share --sysconfdir=/etc/fred '\
               '--prepare-debian-package --root=/tmp/package'



    def run(self):
        if self.no_check_deps is None:
            self.check_dependencies()
        
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
                ('MODULES_CONF_DIR', self.fredconfdir), 
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
        dest = os.path.join(self.fredconfdir, '%s.py' % 
                            self.MODULE_NAME)
        
        # create database
        if self.after_install:
            # copy settings into destination file
            if self.SCRIPT_CREATE_DB:
                print "Run command", command
                os.system(command) # run create-database
        else:
            print "The remaining steps to complete the installation:"
            print "(Use --after-install for make all these "\
                    "command in one step)"
            print
            if self.SCRIPT_CREATE_DB:
                print
                print "Run script: %s path-to-manage.py" % \
                        self.SCRIPT_CREATE_DB
                print command




class NicmsModuleInstallUpdateSettings(NicmsModuleInstall):
    """Extends NicmsModuleInstall for function what modify paths in
    settings file.
    """

    def update_settings(self, src, dest):
        "Make path modifications in settings"
        body = open(src).read()
        body = re.sub('BASE_SHARE_DIR\s*=\s*(.+)', 
                      'BASE_SHARE_DIR = "%s"' % self.share_dir, body, 1)
        open(dest, 'w').write(body)
        if self.log:
            self.log.info('File %s was updated.' % settings)
