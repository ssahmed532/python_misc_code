# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Python miscellaneous utilities repository containing file checksum tools, AWS/S3 operations, and general development examples. **Windows-only** - scripts target Windows 10/11.

## Development Setup

**Python Version:** 3.12
**Package Manager:** Pipenv

```bash
cd src/util_scripts
pipenv install
pipenv shell
```

**Dependencies:** tqdm, pefile, click

**Additional dependencies for AWS scripts (not in Pipfile):** boto3, botocore

## Running the Main CLI Tool

The primary tool is `checksum_file_tool.py` - a Click-based CLI for managing CFV checksum files.

```bash
# Check for missing checksum files
python src/util_scripts/checksum_file_tool.py <dir_path> check-4-missing-cfv-files

# Generate checksum files for subdirectories
python src/util_scripts/checksum_file_tool.py <dir_path> generate-cfv-files

# Verify existing checksum files
python src/util_scripts/checksum_file_tool.py <dir_path> verify-cfv-files
```

**Requires:** `C:\Windows\cfv.bat` (CFV utility from https://cfv.sourceforge.net/)

## Code Architecture

```
src/
├── util_scripts/       # Main utility scripts (most active)
│   ├── checksum_file_tool.py  # Primary CLI tool (Click framework)
│   ├── fileutils.py           # Shared file operations
│   ├── hashutils.py           # SHA1/256/512 hash functions
│   └── findduplicates.py      # Duplicate file finder with tqdm progress
├── aws/s3/             # S3 bucket operations (CRUD, upload, download)
├── general_dev/        # Development examples and benchmarks
├── misc/               # Educational examples (concurrency, design patterns)
└── webscraping/        # BeautifulSoup-based web scrapers
```

## Key Patterns

- **Shared utilities:** `fileutils.py` and `hashutils.py` provide common functions imported by other scripts
- **Click CLI:** Main tool uses Click with context objects to pass `dir_path` between commands
- **Progress bars:** Long operations use `tqdm` for progress visualization
- **External tool dependency:** Checksum operations shell out to `cfv.bat` rather than using pure Python
