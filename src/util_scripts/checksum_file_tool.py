#
# A utility script to scan a given root directory (dir_path) and identify
# those sub-directories that have missing (non-existent) CFV checksum files.
#
# Note:
#   1) This script has only been tested and developed for Windows OSes.
#   2) This script will not work on any other OS/platform.
#   3) This script depends on the external CFV windows utility package (d/l from https://cfv.sourceforge.net/)
#
# Various references for click library usage:
#   - https://www.assemblyai.com/blog/the-definitive-guide-to-python-click/
#   - https://realpython.com/python-click/
#   - https://www.codium.ai/blog/building-user-friendly-python-command-line-interfaces-with-click-and-command-line/
#

import os
import pprint
import subprocess
import sys
from pathlib import Path

import click

DIR_PATH_ARG = "dir_path"
SHA1_EXT = ".sha1"


def do_calculate_checksums(dir_path) -> bool:
    program = "C:\\Windows\\cfv.bat"
    result = subprocess.run([program, "-C", "-rr", "-t", "sha1"], cwd=dir_path)
    # print("returncode: " + str(result.returncode))
    # print(result)
    return result.returncode == 0


def do_verify_checksums(dir_path, checksum_file) -> bool:
    program = "C:\\Windows\\cfv.bat"
    result = subprocess.run([program, "-f", checksum_file], cwd=dir_path)
    # print("returncode: " + str(result.returncode))
    # print(result)
    return result.returncode == 0


@click.group()
@click.pass_context
@click.version_option("0.1.0", prog_name="checksum_file_tool")
@click.argument(
    "dir_path",
    type=click.Path(
        exists=True, dir_okay=True, resolve_path=True, file_okay=False, path_type=Path
    ),
)
def cli(ctx, dir_path):
    ctx.ensure_object(dict)
    ctx.obj[DIR_PATH_ARG] = dir_path


@cli.command("check-context-object")
@click.pass_context
def checkContext(ctx):
    pprint.pprint(type(ctx.obj))
    pprint.pprint(ctx.obj)


@cli.command("check-4-missing-cfv-files")
@click.pass_context
def checkForMissingCfvFiles(ctx):
    """Check for missing checksum files (cfv format) in the
       specified directory.

    Args:
        ctx (_type_): context object that contains context info & data
    """

    # retrieve the dir_path argument from the context object
    # this is the directoryu path within which to start checking for
    # missing CFV format files
    dirPath = ctx.obj[DIR_PATH_ARG]

    dirs_without_checksums = []
    count_dirs_with_checksums = 0
    count_dirs_without_checksums = 0
    count_dirs = 0

    with os.scandir(dirPath) as entries:
        for entry in entries:
            if entry.is_dir():
                count_dirs += 1
                sha1_checksum_filepath = os.path.join(entry.path, entry.name) + SHA1_EXT
                if os.path.exists(sha1_checksum_filepath):
                    click.echo(f"+++ Found checksum file for dir: {entry.name}")
                    count_dirs_with_checksums += 1
                else:
                    click.echo(
                        click.style(
                            f"WARNING: checksum file doesn't exist for dir: {entry.name}",
                            fg="red",
                            bold=True,
                        )
                    )
                    count_dirs_without_checksums += 1
                    dirs_without_checksums.append(entry.path)

    if count_dirs == 0:
        click.echo(f"No sub-directories found in [{dirPath}], there is nothing to do.")
    else:
        print(f"# of directories with CFV files: {count_dirs_with_checksums}")
        print(f"# of directories without CFV files: {count_dirs_without_checksums}")
        print()

        if count_dirs_without_checksums == 0:
            assert count_dirs_with_checksums == count_dirs
            assert not dirs_without_checksums
            click.echo(
                click.style(
                    f"All checksums appear to be up-to-date: you are all set!",
                    fg="green",
                )
            )


@cli.command("generate-cfv-files")
@click.pass_context
def generateCfvFiles(ctx):
    """Generate (cfv format) checksum files for each sub-directory
       found within the specified directory.

    Args:
        ctx (_type_): context object that contains context info & data
    """
    dirPath = ctx.obj[DIR_PATH_ARG]

    countCfvFilesGenerated = 0
    countDirsScanned = 0

    with os.scandir(dirPath) as entries:
        for entry in entries:
            if entry.is_dir():
                countDirsScanned += 1
                sha1_checksum_filepath = os.path.join(entry.path, entry.name) + SHA1_EXT
                if not os.path.exists(sha1_checksum_filepath):
                    print(f"Generating cfv checksum file for {entry.path} ...")
                    do_calculate_checksums(entry.path)
                    countCfvFilesGenerated += 1

        if countCfvFilesGenerated > 0:
            print(f"Generated cfv checksums for {countCfvFilesGenerated} directories")
        else:
            print(
                f"No cfv files generated; all sub-directories appear to be up-to-date"
            )
        print(f"Total no. of sub-directories scanned: {countDirsScanned}")


@cli.command("verify-cfv-files")
@click.pass_context
def verifyCfvFiles(ctx):
    """Recursively scan the specified dir_path and verify the
       (cfv format) checksum files found in its sub-directories.

    Args:
        ctx (_type_): context object that contains context info & data
    """
    dirPath = ctx.obj[DIR_PATH_ARG]

    countDirsScanned = 0
    countCfvFilesVerified = 0

    with os.scandir(dirPath) as entries:
        for entry in entries:
            if entry.is_dir():
                countDirsScanned += 1
                sha1_checksum_filepath = os.path.join(entry.path, entry.name) + SHA1_EXT
                print(f"Verifying CFV checksum file in {entry.path} ...")
                if do_verify_checksums(entry.path, sha1_checksum_filepath):
                    countCfvFilesVerified += 1

    if countDirsScanned == 0:
        print("ERROR: No sub-directories found", file=sys.stderr)
        sys.exit(1)

    print(f"Tested and verified cfv checksums for {countCfvFilesVerified} directories")
    print(f"Total no. of sub-directories scanned: {countDirsScanned}")


if __name__ == "__main__":
    cli()
