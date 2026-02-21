# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Python miscellaneous utilities repository containing file checksum tools, AWS/S3 operations, and general development examples. **Windows-only** - scripts target Windows 10/11, have only been tested on the Windows platform, and have lots of hard-coded assumptions for Windows platforms (e.g. hardcoded `C:\Windows\cfv.bat` path).

## Development Setup

**Python Version:** 3.14 (see `.python-version` and `pyproject.toml`)
**Package Manager:** Pipenv (legacy) or uv (preferred)

```bash
cd src/util_scripts

# Option 1: uv (preferred — no activation needed)
uv run checksum_file_tool.py --help

# Option 2: Pipenv (legacy)
pipenv install
pipenv shell
```

**Note:** The Pipfile still declares `python_version = "3.12"` and has not been updated to match the `.python-version` (3.14) or `pyproject.toml` (`requires-python = ">=3.14"`). Use uv for the most accurate environment.

**Dependencies (pyproject.toml):** click, tqdm, pefile

**Optional dependency groups (pyproject.toml):** `aws` (boto3, botocore), `archive` (rarfile)

## Running Scripts

Scripts in `src/util_scripts/` must be run **from within that directory** because they use direct imports (`import fileutils`, `import hashutils`) rather than package-level imports.

```bash
cd src/util_scripts

# Primary CLI tool — preferred: uv run (handles deps automatically via inline script metadata)
uv run checksum_file_tool.py -v <dir_path> check-4-missing-cfv-files
uv run checksum_file_tool.py <dir_path> generate-cfv-files
uv run checksum_file_tool.py <dir_path> verify-cfv-files

# Or with python directly (after pipenv shell or uv venv activation)
python checksum_file_tool.py <dir_path> check-4-missing-cfv-files

# Duplicate file finder (takes one or more directory paths)
python findduplicates.py <dirPath1> [dirPath2 ...]

# Archive keyword search (requires rarfile + unrar.exe via cygwin)
python find_matching_archives.py <dir_path> <keyword>
```

**External tool required:** `C:\Windows\cfv.bat` (CFV utility from https://cfv.sourceforge.net/) for all checksum operations.

## Code Architecture

The most active code is in `src/util_scripts/`. Other directories (`aws/`, `general_dev/`, `misc/`, `webscraping/`) contain standalone scripts and examples.

### Key files in util_scripts

- **`checksum_file_tool.py`** - Primary CLI tool using Click with `@click.group()` subcommand architecture. Uses `ctx.obj` dict to pass `dir_path` and `verbose` between the group and subcommands. Has inline `# /// script` uv metadata (run with `uv run`). **Phase 1 complete:** global `-v/--verbose` flag implemented with custom `validate_dir_path()` callback and standardized `click.echo()` output. Phases 2-4 (--calc-checksums, verify failure tracking, verbose generate) are still pending per PLANv2.md. This is the consolidated replacement for the older `check_dir_checksum_files.py` (argparse) and `verify_checksums_in_subdirs.py` (argparse, incomplete).
- **`fileutils.py`** - Shared file operations: `getFileList()`, `getAllFilesRecursive()`, `getFileVersionInfo()` (uses pefile), `copyFile()`. Imported by findduplicates.py, find_matching_archives.py, and others.
- **`hashutils.py`** - SHA1/256/512 file hashing via hashlib with chunked reads (BLOCKSIZE=65526). Imported by findduplicates.py.
- **`findduplicates.py`** - Standalone script (not Click). Builds a hash-to-files dict using `defaultdict(list)`, reports duplicates with disk space calculations. Uses tqdm for progress.
- **`DETAILS.md`** - Comprehensive reverse-engineered specification of the checksum scripts, including control flow, edge cases, and CFV tool reference.
- **`main.py`** - Stub entry point (`print("Hello from util-scripts!")`) created as part of uv project setup. Not functionally used.
- **`find_payment_txn_files.py`** - Standalone script to find files by last-modified date range within a directory. Has a hardcoded `DIR_PATH` default; accepts an optional CLI arg to override it.
- **`html_link_extractor.py`** - Standalone script (purpose: extract links from HTML).
- **`list_rarfiles_contents.py`** - Standalone script (purpose: list contents of RAR archives).

### Legacy scripts (superseded by checksum_file_tool.py)

- **`check_dir_checksum_files.py`** - Original argparse-based script for checking/generating checksums. Has `--calc-checksums` flag that `checksum_file_tool.py` doesn't yet replicate (uses separate `generate-cfv-files` subcommand instead).
- **`verify_checksums_in_subdirs.py`** - Original argparse-based verify script. **Incomplete**: counters declared but unused, summary stats commented out, `--verbose` flag parsed but never used.

### Checksum tool internals

The checksum tools share a common pattern: scan immediate subdirectories of a root path, expect each to contain `<dirname>.sha1` inside it. Key functions:

- `do_calculate_checksums(dir_path)` - Shells out to `cfv.bat -C -rr -t sha1` with `cwd=dir_path`
- `do_verify_checksums(dir_path, checksum_file)` - Shells out to `cfv.bat -f <checksum_file>` with `cwd=dir_path`

Both return `bool` based on CFV exit code, but callers don't always check the return value.

## Key Patterns

- **No tests exist** in this repository. There is no test framework configured.
- **Naming style is mixed:** camelCase function/variable names (e.g. `getFileList`, `dirPath`) coexist with snake_case (e.g. `dir_path`, `count_dirs`). Follow the style of the file you're editing.
- **External tool shelling:** Checksum operations use `subprocess.run()` to call `cfv.bat` rather than pure Python. CFV output goes directly to console (stdout/stderr not captured).
- **Single-level directory scanning:** The checksum tools only scan immediate subdirectories of the given path, not recursively nested ones. Each subdirectory is expected to contain a `<dirname>.sha1` checksum file inside it.
- **Planning docs exist:** `src/util_scripts/PLANv2.md` (4-phase implementation plan; Phase 1 complete) and `NEXT_STEPS.md` (at repo root, not in util_scripts) document in-progress consolidation work and planned enhancements for `checksum_file_tool.py`. `PLAN.md` (initial plan, superseded by PLANv2) may also be present.
