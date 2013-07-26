import os
import string

from glob import glob
from types import TupleType

from distutils import dir_util, file_util, log
from distutils.command.sdist import sdist as _sdist
from distutils.util import convert_path

from freddist.filelist import FileList


class sdist(_sdist):
    user_options = _sdist.user_options + [
        ('create-manifest-in', None,
         "Create file MANIFEST.in"),
    ]

    boolean_options = _sdist.boolean_options + ['create-manifest-in']

    def initialize_options(self):
        _sdist.initialize_options(self)
        self.create_manifest_in = False

    def finalize_options(self):
        _sdist.finalize_options(self)
        self.template = os.path.join(self.distribution.srcdir, self.template)

    def run(self):
        #FREDDIST: Use different FileList
        # 'filelist' contains the list of files that will make up the
        # manifest
        self.filelist = FileList(srcdir=self.distribution.srcdir)

        # Ensure that all required meta-data is given; warn if not (but
        # don't die, it's not *that* serious!)
        self.check_metadata()

        # Do whatever it takes to get the list of files to process
        # (process the manifest template, read an existing manifest,
        # whatever).  File list is accumulated in 'self.filelist'.
        self.get_file_list()

        #FREDDIST: Just create 'MANIFEST.in'
        if self.create_manifest_in:
            self.generate_manifest_in()
            return

        # If user just wanted us to regenerate the manifest, stop now.
        if self.manifest_only:
            return

        # Otherwise, go ahead and create the source distribution tarball,
        # or zipfile, or whatever.
        self.make_distribution()

    def add_defaults (self):
        """Add all the default files to self.filelist:
          - README or README.txt
          - setup.py
          - test/test*.py
          - all pure Python modules mentioned in setup script
          - all files pointed by package_data (build_py)
          - all files defined in data_files.
          - all files defined as scripts.
          - all C sources listed as part of extensions or C libraries
            in the setup script (doesn't catch C headers!)
        Warns if (README or README.txt) or setup.py are missing; everything
        else is optional.
        """
        # This method is copied from version 2.7

        standards = [('README', 'README.txt'), self.distribution.script_name]
        for fn in standards:
            if type(fn) is TupleType:
                alts = fn
                got_it = 0
                for fn in alts:
                    #FREDDIST: create full path
                    fn = os.path.join(self.distribution.srcdir, fn)
                    if os.path.exists(fn):
                        got_it = 1
                        self.filelist.append(fn)
                        break

                if not got_it:
                    self.warn("standard file not found: should have one of " +
                              string.join(alts, ', '))
            else:
                #FREDDIST: create full path
                fn = os.path.join(self.distribution.srcdir, fn)
                if os.path.exists(fn):
                    self.filelist.append(fn)
                else:
                    self.warn("standard file '%s' not found" % fn)

        #FREDDIST: add release version file
        optional = ['test/test*.py', 'setup.cfg', 'RELEASE-VERSION']
        for pattern in optional:
            #FREDDIST: create full path
            pattern = os.path.join(self.distribution.srcdir, pattern)
            files = filter(os.path.isfile, glob(pattern))
            if files:
                self.filelist.extend(files)

        # build_py is used to get:
        #  - python modules
        #  - files defined in package_data
        build_py = self.get_finalized_command('build_py')

        # getting python files
        if self.distribution.has_pure_modules():
            self.filelist.extend(build_py.get_source_files())

        # getting package_data files
        # (computed in build_py.data_files by build_py.finalize_options)
        for pkg, src_dir, build_dir, filenames in build_py.data_files:
            for filename in filenames:
                self.filelist.append(os.path.join(src_dir, filename))

        # getting distribution.data_files
        if self.distribution.has_data_files():
            for item in self.distribution.data_files:
                if isinstance(item, str): # plain file
                    item = convert_path(item)
                    #FREDDIST: create full path
                    item = os.path.join(self.distribution.srcdir, item)
                    if os.path.isfile(item):
                        self.filelist.append(item)
                else:    # a (dirname, filenames) tuple
                    dirname, filenames = item
                    for f in filenames:
                        f = convert_path(f)
                        #FREDDIST: create full path
                        f = os.path.join(self.distribution.srcdir, f)
                        if os.path.isfile(f):
                            self.filelist.append(f)

        if self.distribution.has_ext_modules():
            build_ext = self.get_finalized_command('build_ext')
            self.filelist.extend(build_ext.get_source_files())

        if self.distribution.has_c_libraries():
            build_clib = self.get_finalized_command('build_clib')
            self.filelist.extend(build_clib.get_source_files())

        if self.distribution.has_scripts():
            build_scripts = self.get_finalized_command('build_scripts')
            self.filelist.extend(build_scripts.get_source_files())

        #FREDDIST: add i18n files
        if self.distribution.has_i18n_files():
            build_i18n = self.get_finalized_command('build_i18n')
            self.filelist.extend(build_i18n.get_source_files())

    def make_release_tree (self, base_dir, files):
        """Create the directory tree that will become the source
        distribution archive.  All directories implied by the filenames in
        'files' are created under 'base_dir', and then we hard link or copy
        (if hard linking is unavailable) those files into place.
        Essentially, this duplicates the developer's source tree, but in a
        directory named after the distribution, containing only the files
        to be distributed.
        """
        # Create all the directories under 'base_dir' necessary to
        # put 'files' there; the 'mkpath()' is just so we don't die
        # if the manifest happens to be empty.
        self.mkpath(base_dir)
        dir_util.create_tree(base_dir, files, dry_run=self.dry_run)

        # And walk over the list of files, either making a hard link (if
        # os.link exists) to each one that doesn't already exist in its
        # corresponding location under 'base_dir', or copying each file
        # that's out-of-date in 'base_dir'.  (Usually, all files will be
        # out-of-date, because by default we blow away 'base_dir' when
        # we're done making the distribution archives.)

        if hasattr(os, 'link'):        # can make hard links on this system
            link = 'hard'
            msg = "making hard links in %s..." % base_dir
        else:                           # nope, have to copy
            link = None
            msg = "copying files to %s..." % base_dir

        if not files:
            log.warn("no files to distribute -- empty manifest?")
        else:
            log.info(msg)
        for file in files:
            #FREDDIST: create full filename
            src = os.path.join(self.distribution.srcdir, file)
            if not os.path.isfile(src):
                log.warn("'%s' not a regular file -- skipping" % file)
            else:
                dest = os.path.join(base_dir, file)
                self.copy_file(src, dest, link=link)

        self.distribution.metadata.write_pkg_info(base_dir)

    #FREDDIST: new method
    def generate_manifest_in(self, initial=None):
        """
        This function generage file MANIFEST.in from distribution.data_files array.
        """
        manifest = ['# created by:$ python setup.py sdist --create-manifest-in']

        # include individual variables
        if isinstance(initial, list) or isinstance(initial, tuple):
            manifest.extend(initial)
        elif isinstance(initial, str):
            manifest.append(initial)

        # include folders from distribution.data_files
        for line in self.distribution.data_files:
            if len(line[1]):
                path = os.path.dirname(line[1][0])
                if path:
                    manifest.append('include %s/*' % path)
                else:
                    manifest.append('include %s' % ' '.join(line[1]))

        self.execute(file_util.write_file,
                     (self.manifest, self.filelist.files),
                     "writing manifest template file '%s'" % self.manifest)
