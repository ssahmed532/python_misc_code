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
#           ***OR***
#           https://www.rarlab.com/rar/unrarsrc-6.0.7.tar.gz
#           tar -xzvf unrarsrc-5.1.7.tar.gz
#           ***OR***
#           tar -xzvf unrarsrc-6.0.7.tar.gz
#           cd unrar
#           make all
#           make install
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

# TODOs
#   - refactor code into a Class
#   - use argparse module for proper CLI args handling
#   - add option to ignore case during matching
#   - add option to specify multiple keywords together with logical
#     operators (e.g. 'Python && Cloud')
#   - 
#


class FileFinder:
    def __init__(self, dir_path: str) -> None:
        self.dir_path = dir_path
        # dict[filename] -> [matching file contents from inside the archive]
        self.matched_files = {}


    def match_by_filename(self, filename: str, keyword: str) -> bool:
        """ Match the given filename by presence of the keyword in the filename

        Args:
            filename (string): filename of the file to check
            keyword (string): keyword to match against

        Returns:
            bool: True if the filename is matched against the keyword
        """

        #   Only match the last filename portion of filename.
        #   For example, if filename is "D:\eBooks_repo\EBOOKS\NLP\Natural Language Processing with TensorFlow.rar",
        #   check the keyword in the filename portion ("Natural Language Processing with TensorFlow.rar")
        #   only and not in the entire file path string
        #
        return (keyword in os.path.basename(filename))


    def match_by_contents(self, filename: str, keyword: str):
        """ Match the given keyword against the contents of the archive file

        Args:
            filename (string): filename of the (archive) file to check
            keyword (string): keyword to match against

        Returns:
            List: a list of matching filenames found inside the archive file
            that matched the given keyword
        """

        matched_files = []

        # TODO
        #   improve error handling
        #   propagate exceptions to calling function/code
        #

        try:
            with rarfile.RarFile(filename) as archive:
                for entry in archive.infolist():
                    if keyword in entry.filename:
                        matched_files.append(entry.filename)
        except rarfile.NeedFirstVolume as nfve:
            print(f'ERROR: unable to check a split / multi-volume RAR file: {filename}', file=sys.stderr)
            print(nfve)
        except rarfile.NotRarFile as nrfe:
            print(f'ERROR: {filename} is not a RAR archive', file=sys.stderr)
            print(nrfe)
        except rarfile.RarCannotExec as rcee:
            print(f'ERROR: Unable to extract archive {filename} due to missing unrar tool', file=sys.stderr)
            print(rcee)

        return matched_files


    def find_matching_archives(self, keyword: str) -> int:
        files_list = []
        startTime = timer()
        files_list = fileutils.getAllFilesRecursive(self.dir_path)
        endTime = timer()
        elapsed_time = round(endTime - startTime, 5)
        print(f'{len(files_list)} files found in {elapsed_time} seconds')

        self.matched_files.clear()

        for file in files_list:
            file_ext = pathlib.Path(file).suffix
            if file_ext and (file_ext in VALID_FILE_EXT):
                # check if the filename contains the keyword being searched for
                if self.match_by_filename(file, keyword):
                    self.matched_files[file] = ["***matched by filename ***"]
                elif matched_contents := self.match_by_contents(file, keyword):
                    print(f'{len(matched_contents)} files inside archive {file} matched the keyword {keyword}')
                    self.matched_files[file] = matched_contents

        return len(self.matched_files)


    def print_matched_files(self) -> None:
        for filename in self.matched_files:
            print(f'Filename: {filename}')
            pprint(self.matched_files[filename])
            print()
        print()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f'Usage: python {os.path.basename(sys.argv[0])} </path/to/directory containing archive files> <keyword>', file=sys.stderr)
        sys.exit(1)

    dir_path = sys.argv[1]
    keyword = sys.argv[2]

    file_finder = FileFinder(dir_path)
    
    count = file_finder.find_matching_archives(keyword)
    print(f'Found {count} files matching keyword {keyword}:')
    file_finder.print_matched_files()
