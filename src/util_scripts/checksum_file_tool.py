#
# A utility script to scan a given root directory (dir_path) and identify
# those sub-directories that have missing (non-existent) CFV checksum files.
#
# Note:
#   1) This script has only been tested and developed for Windows OSes.
#   2) This script will not work on any other OS/platform.
#   3) This script depends on the external CFV windows utility package (d/l from https://cfv.sourceforge.net/)
#

import os
import pprint
import sys
from pathlib import Path

import click

DIR_PATH_ARG = "dir_path"
SHA1_EXT = ".sha1"


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


if __name__ == "__main__":
    cli()
