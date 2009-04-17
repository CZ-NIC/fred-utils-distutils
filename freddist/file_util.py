"""
freddist.file_util
Utility function for operating on files
"""

import os, sys, fnmatch, sets, re, stat
from distutils.file_util import *

# by default exclude hidden files/directories
EXCLUDE_PATTERN = ['.*']
# and include all other
INCLUDE_PATTERN = ['*']

#def curdir(path):
#    """Return directory where setup.py file is situated."""
#    return os.path.join(os.path.dirname(sys.argv[0]), path)

def fit_pattern(filename, excludePattern):
    """Return True if filename fit `excludePattern', otherwise False"""
    for patt in excludePattern:
        if fnmatch.fnmatch(filename, patt):
            return True
    return False

def all_files_in_3(dst_directory, directory, excludePattern=None,
        includePattern=None, recursive=True):
    if not excludePattern:
        try:
            excludePattern = EXCLUDE_PATTERN
        except NameError:
            excludePattern = ['.*']
    if not includePattern:
        try:
            includePattern = INCLUDE_PATTERN
        except NameError:
            includePattern = ['*']
    paths = [] # list of couples (directory, directory/file) for all files
    dirr = os.listdir(directory)

    for filename in dirr:
        if fit_pattern(filename, excludePattern):
            continue
        if not fit_pattern(filename, includePattern):
            continue
        full_path = os.path.join(directory, filename)

        newpart = full_path[full_path.find(directory)+len(directory):].strip(os.path.sep)

        if os.path.isfile(full_path):
            paths.append((os.path.join(dst_directory, newpart), [full_path]))

        elif os.path.isdir(full_path) and recursive:
            paths.extend(
                    all_files_in_3(
                        os.path.join(dst_directory, newpart),
                        full_path,
                        excludePattern, includePattern, recursive))
    return paths

def all_files_in_4(dst_directory, directory, excludePattern=None,
        includePattern=None, recursive=True, prefix=''):
    if not excludePattern:
        try:
            excludePattern = EXCLUDE_PATTERN
        except NameError:
            excludePattern = ['']
    if not includePattern:
        try:
            includePattern = INCLUDE_PATTERN
        except NameError:
            includePattern = ['*']
    paths = [] # list of couples (directory, directory/file) for all files
    for filename in os.listdir(directory):
        if fit_pattern(filename, excludePattern):
            continue
        if not fit_pattern(filename, includePattern):
            continue
        full_path = os.path.join(directory, filename)
        prefixx = full_path[full_path.find(directory)+len(directory)+1:]


        if os.path.isfile(full_path):
            paths.append((
                os.path.join(dst_directory, prefix),
                [full_path]))
        elif os.path.isdir(full_path):
            paths.extend(
                    all_files_in_4(dst_directory, full_path, excludePattern,
                        includePattern, recursive, os.path.join(prefix, prefixx)))
    return paths


def all_files_in(dst_directory, directory, excludePattern=None,
        includePattern=None, recursive=True, cutSlashes_dst=0, cutSlashes_dir=0):
    """
    Returns couples (directory, directory/file) to all files in directory.
    Files (as well as directories must not fit `excludePattern' mask.
    """
    if not excludePattern:
        try:
            excludePattern = EXCLUDE_PATTERN
        except NameError:
            excludePattern = ['']
    if not includePattern:
        try:
            includePattern = INCLUDE_PATTERN
        except NameError:
            includePattern = ['*']
    paths = [] # list of couples (directory, directory/file) for all files

    #for filename in os.listdir(curdir(directory)):
    for filename in os.listdir(directory):
        if fit_pattern(filename, excludePattern):
            continue
        if not fit_pattern(filename, includePattern):
            continue
        full_path = os.path.join(directory, filename)
        #if os.path.isfile(curdir(full_path)):
        if os.path.isfile(full_path):
            # exclude first directory in path from dst path (this include
            # really only what is IN directory, not (directory AND files))
            splitted_directory = directory.split(os.path.sep, 1)
            if len(splitted_directory) > 1:
                dst_subdirectory = splitted_directory[1]
            else: # directory is only one directory yet
                dst_subdirectory = ''
            if cutSlashes_dst > 0 or cutSlashes_dir > 0:
                paths.append((os.path.join(
                    dst_directory,
                    dst_subdirectory.split(os.path.sep, cutSlashes_dst)[-1]),
                    [full_path.split(os.path.sep, cutSlashes_dir)[-1]]))
            else:
                paths.append((os.path.join(dst_directory, dst_subdirectory), [full_path]))
        #elif os.path.isdir(curdir(full_path)) and recursive:
        elif os.path.isdir(full_path) and recursive:
            paths.extend(all_files_in(dst_directory, full_path, excludePattern,
                includePattern, recursive, cutSlashes_dst, cutSlashes_dir))   
           
    return paths


def all_files_in_2(directory, excludePattern=None, includePattern=None,
        recursive=False, onlyFilenames=False, cutSlashes=0):
    """
    Returns list (for example: ['filename1', 'filename2', ...]) of files in
    directory (directories if recursive). Files must not fit `excludePattern'
    mask. If parameter `onlyFilenames' is False, each record from list contain
    also its source directory (usually something like `directory/filename'),
    otherwise only filename. Exclude pattern is list of wildcard mask, for
    further help see fnmatch module reference.
    If cutSlashes is bigger than zero, then given number of path parts (divided
    by slashes) will be removed from final path. For example if return from
    function is ['home/whatever/foo/foo.c'] (cutSlashes is zero), then when
    cutSlashes is set to 2 return will be ['foo/foo.c']
    """
    if not excludePattern:
        try:
            excludePattern = EXCLUDE_PATTERN
        except NameError:
            excludePattern = ['']
    if not includePattern:
        try:
            includePattern = INCLUDE_PATTERN
        except NameError:
            includePattern = ['*']

    paths = []
    #for filename in os.listdir(curdir(directory)):
    for filename in os.listdir(directory):
        if fit_pattern(filename, excludePattern):
            continue
        if not fit_pattern(filename, includePattern):
            continue
        full_path = os.path.join(directory, filename)
        #if os.path.isfile(curdir(full_path)):
        if os.path.isfile(full_path):
            if onlyFilenames:
                paths.append(filename)
            else:
                if cutSlashes > 0:
                    paths.append(full_path.split(os.path.sep, cutSlashes)[-1])
                else:
                    paths.append(full_path)

        #if os.path.isdir(curdir(full_path)) and recursive:
        if os.path.isdir(full_path) and recursive:
            paths.extend(all_files_in_2(full_path, excludePattern,
                includePattern, recursive, onlyFilenames, cutSlashes))
    return paths


def all_subpackages_in(folder, omit_name = 'build'):
    'Returns all subpackages (packages in subdirectories) (recursive)'
    subpackages = sets.Set()
    
    name = folder.replace(os.path.sep, '.').strip('.')
    if name == omit_name:
        # omit build folder, the name of folder could be changed by --bdist-base (-b)
        return subpackages
    
    for filename in os.listdir(folder):
        path = os.path.join(folder, filename)
        if os.path.isdir(path) and filename[0] != ".":
            # walk throught subdolder (omit .hidden-folders)
            subpackages.update(all_subpackages_in(path))
        else:
            # join only packages
            if filename == '__init__.py':
                # join python package into list
                name = folder.replace(os.path.sep, '.').strip('.')
                if name: # name might be empty after stripping
                    subpackages.add(name)
    return subpackages


def collect_data_files(data):
    data_files = []
    
    # functions which supports collect filenames in folders
    is_svn = re.compile('.svn')
    
    def collect_folder_files(prefix, folder):
        for root, dirs, files in os.walk(folder):
            if is_svn.search(root):
                continue # omit svn folders
            # strip backups
            project_files = [os.path.join(root, name) for name in files if name[-1] != '~']
            if len(project_files):
                data_files.append((os.path.join(prefix, root), project_files))

    for prefix, folder in data:
        collect_folder_files(prefix, folder)
    return data_files


def set_file_executable(filepath):
    "Set file mode to executable"
    os.chmod(filepath, os.stat(filepath)[stat.ST_MODE] | stat.S_IEXEC | 
             stat.S_IXGRP | stat.S_IXOTH)
    
    

if __name__ == '__main__':
    # test function all_subpackages_in()
    if len(sys.argv) > 1:
        print all_subpackages_in(sys.argv[1])
    else:
        print 'Test function all_subpackages_in()\nUsage: python file_util.py folder'

