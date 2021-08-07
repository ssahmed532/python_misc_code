#
# Python script to check how many RAR archive files inside a given directory
# 'match' a specific keyword.
#
# This script requires the following Python modules to be pip installed:
#       rarfile
#
# Additional steps needed to make rarfile work on Windows:
#       - Setup and install cygwin (latest version) 64-bit for Windows
#       - make sure to install the following cygwin packages:
#           gcc, make, makedepend
#
# rarfile needs unrar.exe to be present on the Windows path; so:
#       - perform the following steps to compile & install unrar.exe using
#         cygwin:
#           (do the following steps in a cygwin shell)
#           cd /tmp
#           wget http://www.rarlab.com/rar/unrarsrc-5.1.7.tar.gz
#           tar -xzvf unrarsrc-5.1.7.tar.gz
#           cd unrar
#           make all
#           cp unrar.exe /bin/
#
#       - After the steps above, unrar.exe is going to be present in
#         cygwin's main bin folder and can used inside a new cygwin shell
#
#       - Modify the Windows 10 user environment variable settings and add a
#         new environment variable named PATH with the following value:
#           %PATH%;C:\cygwin64\bin;
#
# Additional references that were helpful in resolving the unrar.exe issue:
#       https://wjianz.wordpress.com/2014/09/28/howto-extract-rar-files-on-cygwin/
#
#

import os
import pathlib
from pprint import pprint as pprint
import sys
import rarfile
import fileutils

from timeit import default_timer as timer


__version__ = "1.0"

VALID_FILE_EXT = ['.rar']


def match_by_filename(filename, keyword):
    """Match the given filename by presence of the keyword in the filename

    Args:
        filename (string): filename of the file to check
        keyword (string): keyword to match against

    Returns:
        Boolean: True if the filename is matched against the keyword
    """
    return (keyword in filename)


def match_by_contents(filename, keyword):
    """Match the given keyword against the contents of the archive file

    Args:
        filename (string): filename of the (archive) file to check
        keyword (string): keyword to match against

    Returns:
        Boolean: True if any of the files inside the archive file are matched (by filename) against the keyword
    """
    matching_files = []

    try:
        with rarfile.RarFile(filename) as archive:
            for entry in archive.infolist():
                if keyword in entry.filename:
                    matching_files.append(entry.filename)
    except rarfile.NeedFirstVolume as nfve:
        print(f'ERROR: unable to check a split / multi-volume RAR file: {filename}', file=sys.stderr)
        print(nfve)

    return matching_files


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f'Usage: python {os.path.basename(sys.argv[0])} </path/to/directory containing archive files> <keyword>', file=sys.stderr)
        sys.exit(1)

    dir_path = sys.argv[1]
    keyword = sys.argv[2]

    files_list = []
    startTime = timer()
    files_list = fileutils.getAllFilesRecursive(dir_path)
    endTime = timer()
    elapsed_time = round(endTime - startTime, 5)
    print(f'{len(files_list)} files found in {elapsed_time} seconds')

    # dict[filename] -> [matching file contents from inside the archive]
    matched_files = {}

    for file in files_list:
        file_ext = pathlib.Path(file).suffix
        if file_ext and (file_ext in VALID_FILE_EXT):
            # check if the filename contains the keyword being searched for
            if match_by_filename(file, keyword):
                matched_files[file] = ["***matched by filename ***"]
            elif matched_contents := match_by_contents(file, keyword):
                print(f'{len(matched_contents)} files inside archive {file} matched the keyword {keyword}')
                matched_files[file] = matched_contents
    
    print()

    print(f'Found {len(matched_files.keys())} matching files:')
    for filename in matched_files:
        print(f'Filename: {filename}')
        pprint(matched_files[filename])
        print()
