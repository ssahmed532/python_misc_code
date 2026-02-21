# Util Scripts - Checksum and File Management Tools

Windows-only utilities for file checksum management, duplicate detection, and archive searching.

## Prerequisites

- **Python 3.14+**
- **Windows OS** (tested on Windows 10/11)
- **CFV utility** installed at `C:\Windows\cfv.bat` (download from https://cfv.sourceforge.net/)
- **uv** package manager

## Installation

Install uv if you haven't already:
```bash
# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

No additional installation needed! uv will automatically manage dependencies when you run scripts.

## Usage

### Primary Tool: checksum_file_tool.py (Click-based CLI)

The consolidated checksum management tool with three main commands:

```bash
# Check for missing checksum files
uv run checksum_file_tool.py D:\Archive check-4-missing-cfv-files

# Check with verbose output
uv run checksum_file_tool.py -v D:\Archive check-4-missing-cfv-files

# Generate missing checksum files
uv run checksum_file_tool.py D:\Archive generate-cfv-files

# Verify existing checksums
uv run checksum_file_tool.py D:\Archive verify-cfv-files

# Show help
uv run checksum_file_tool.py --help
uv run checksum_file_tool.py D:\Archive check-4-missing-cfv-files --help
```

### Legacy Scripts

#### check_dir_checksum_files.py (argparse-based)

Check and optionally generate checksums:

```bash
uv run check_dir_checksum_files.py D:\Archive
uv run check_dir_checksum_files.py -v D:\Archive
uv run check_dir_checksum_files.py --calc-checksums D:\Archive
```

#### verify_checksums_in_subdirs.py (argparse-based)

Verify checksums in subdirectories:

```bash
uv run verify_checksums_in_subdirs.py D:\Archive
uv run verify_checksums_in_subdirs.py -v D:\Archive
```

## Features

### checksum_file_tool.py
- ✓ Global `--verbose/-v` flag for detailed output
- ✓ Colored, styled console output
- ✓ Custom error messages with rich formatting
- ✓ Three subcommands: check, generate, verify
- ✓ Click-based modern CLI interface
- ✓ Context object for parameter passing

### check_dir_checksum_files.py (Legacy)
- `--calc-checksums` flag to generate missing checksums
- Verbose output support
- Warning messages for missing files

### verify_checksums_in_subdirs.py (Legacy)
- Verify checksums in all subdirectories
- Returns exit code based on verification status

## Dependencies

### Core Dependencies
- **click** >= 8.1.0 (checksum_file_tool.py only)
- **tqdm** >= 4.65.0 (for findduplicates.py)
- **pefile** >= 2023.2.7 (for file version info)

Automatically installed by uv when running scripts.

### Optional Dependencies
Install optional dependencies for specific use cases:

```bash
# For AWS/S3 scripts
uv sync --extra aws

# For archive searching
uv sync --extra archive
```

## How It Works

1. **Directory Scanning**: Scripts scan immediate subdirectories of the given root path
2. **Checksum Files**: Each subdirectory should contain `<dirname>.sha1` inside it
3. **CFV Integration**: Uses external CFV utility to calculate/verify SHA1 checksums
4. **Single-Level Only**: Does not recursively scan nested subdirectories

## Project Structure

```
src/util_scripts/
├── checksum_file_tool.py      # Primary CLI tool (recommended)
├── check_dir_checksum_files.py # Legacy check/generate script
├── verify_checksums_in_subdirs.py # Legacy verify script
├── findduplicates.py           # Find duplicate files by hash
├── fileutils.py                # Shared file operations
├── hashutils.py                # SHA hashing utilities
├── pyproject.toml              # uv package configuration
└── README.md                   # This file
```

## Development Notes

- Scripts use mixed naming conventions (camelCase and snake_case)
- Must be run from `src/util_scripts/` directory due to direct imports
- No test framework configured
- See `PLANv2.md` for consolidation roadmap
- See `DETAILS.md` for comprehensive specification

## Troubleshooting

### "CFV not found" error
Ensure `C:\Windows\cfv.bat` exists and is executable. Download from https://cfv.sourceforge.net/

### "Invalid value for 'DIR_PATH'" error
The directory path doesn't exist or isn't a directory. Check the path and try again.

### uv command not found
Install uv: `powershell -c "irm https://astral.sh/uv/install.ps1 | iex"`

### Scripts must be run from src/util_scripts/
These scripts use direct imports (`import fileutils`) rather than package imports, so they must be executed from within the `src/util_scripts/` directory.

## License

See repository root for license information.

## Contributing

This is a personal utilities repository. See `CLAUDE.md` for development guidelines when working with Claude Code.
