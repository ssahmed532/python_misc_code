# given a target directory path, scan all sub-directories in that folder/path
# and highlight those ones that do not have a checksum file present in them.
#

import os
import sys

SHA1_EXT = ".sha1"


# TODO:
#   also highlight those folders where the existing SHA1 checksum file
#   is "out of date" with respect to the contents of that folder.

if __name__ == '__main__':
    if len(sys.argv) == 1:
        print('Usage: python check_dir_checksum_files.py <dirPath>', file=sys.stderr)
        sys.exit(1)

    dir_path = os.path.abspath(sys.argv[1])

    print("Checking all sub-directories in root dir path: " + dir_path)

    with os.scandir(dir_path) as it:
        for entry in it:
            if entry.is_dir():
                #print("dir name:      " + entry.name)
                #print("dir full path: " + entry.path)
                sha1_checksum_filepath = os.path.join(entry.path, entry.name) + SHA1_EXT
                # print("***: " + sha1_checksum_filepath)
                if os.path.exists(sha1_checksum_filepath):
                    print("++++++ Found SHA1 checksum file for dir: " + entry.name)
                else:
                    print("WARNING: SHA1 checksum file doesn't exist for dir: " + entry.name)
