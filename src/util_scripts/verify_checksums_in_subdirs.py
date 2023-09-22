# Given a target directory path, scan all sub-directories in that folder/path
# and verify/validate the CFV style checksums file in that sub-directory.
#

import argparse
import os
import sys
import subprocess

SHA1_EXT = ".sha1"


# TODO:
#   - add verbose output when the --verbose flag is enabled
#   - also highlight those folders where the existing SHA1 checksum file
#     is "out of date" with respect to the contents of that folder.
#   - look into using the cfv Python package instead of shelling out
#     and calling the cfv program installed on Windows.
#


def do_verify_checksums(dir_path, checksum_file) -> bool:
    program = "C:\\Windows\\cfv.bat"
    result = subprocess.run([program, "-f", checksum_file], cwd=dir_path)
    # print("returncode: " + str(result.returncode))
    # print(result)
    return result.returncode == 0


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(
        allow_abbrev=False,
        description="Script to verify/validate CFV style checksums in all sub-dirs of a given root directory",
    )

    arg_parser.add_argument(
        "-v",
        "--verbose",
        required=False,
        action="store_true",
        help="display verbose output",
    )

    arg_parser.add_argument(
        "dir_path",
        type=str,
        help="path to the root directory to start in"
    )

    args = arg_parser.parse_args()

    verbose = args.verbose
    root_dir = args.dir_path

    print(f"Checking all sub-directories in root dir path: {root_dir} ...")

    dirs_without_checksums = []
    count_dirs_with_checksums = 0
    count_dirs_without_checksums = 0
    count_dirs = 0

    with os.scandir(root_dir) as it:
        for entry in it:
            if entry.is_dir():
                count_dirs += 1
                #print("dir name:      " + entry.name)
                print("dir full path: " + entry.path)
                sha1_checksum_filepath = os.path.join(entry.path, entry.name) + SHA1_EXT
                #print("***: " + sha1_checksum_filepath)
                do_verify_checksums(entry.path, sha1_checksum_filepath)

    if count_dirs == 0:
        print("ERROR: No sub-directories found", file=sys.stderr)
        sys.exit(1)

    #print(f"# of directories with checksum files: {count_dirs_with_checksums}")
    #print(f"# of directories without checksum files: {count_dirs_without_checksums}")
    #print()

    #if count_dirs_without_checksums == 0:
    #    assert count_dirs_with_checksums == count_dirs
    #    assert not dirs_without_checksums
    #    print("All checksums appear to be up-to-date")
    #    sys.exit(0)

    #if calculate_checksums and (len(dirs_without_checksums) > 0):
    #    count_computed_checksums = 0
    #    print(f"Computing checksums in {len(dirs_without_checksums)} directories ...")
    #    for dir_path in dirs_without_checksums:
    #        do_calculate_checksums(dir_path)
    #        count_computed_checksums += 1

    #    print(f"Computed dir checksums for {count_computed_checksums} directories")
