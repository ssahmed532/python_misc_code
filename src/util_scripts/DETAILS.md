# CFV Checksum Tools - Consolidated Requirements & Technical Specification

This document provides a comprehensive reverse-engineered specification of three related Python scripts for managing CFV-format checksum files. It is intended to serve as a Product Requirements Document (PRD) for consolidation or reimplementation.

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Source Scripts Overview](#source-scripts-overview)
3. [External Dependencies](#external-dependencies)
4. [Core Concepts & Terminology](#core-concepts--terminology)
5. [Shared Constants & Conventions](#shared-constants--conventions)
6. [Feature Matrix](#feature-matrix)
7. [Detailed Functionality Analysis](#detailed-functionality-analysis)
   - [Feature 1: Check for Missing Checksum Files](#feature-1-check-for-missing-checksum-files)
   - [Feature 2: Generate Checksum Files](#feature-2-generate-checksum-files)
   - [Feature 3: Verify Checksum Files](#feature-3-verify-checksum-files)
8. [Command-Line Interfaces](#command-line-interfaces)
9. [Core Functions & Implementation Details](#core-functions--implementation-details)
10. [Control Flow Diagrams](#control-flow-diagrams)
11. [Error Handling & Edge Cases](#error-handling--edge-cases)
12. [Exit Codes](#exit-codes)
13. [Output Formatting & User Feedback](#output-formatting--user-feedback)
14. [Assumptions Baked Into The Code](#assumptions-baked-into-the-code)
15. [Known Limitations & TODOs](#known-limitations--todos)
16. [Platform & Environment Requirements](#platform--environment-requirements)
17. [Appendix: CFV Tool Reference](#appendix-cfv-tool-reference)

---

## Executive Summary

These three scripts provide functionality to manage SHA1 checksum files in a directory structure using the external CFV (Checksum File Validator) tool. The primary use cases are:

1. **Detection**: Identify subdirectories missing checksum files
2. **Generation**: Create checksum files for subdirectories that lack them
3. **Verification**: Validate existing checksum files against actual file contents

All scripts operate on **immediate subdirectories only** (single-level, non-recursive) and depend on an external Windows batch file (`C:\Windows\cfv.bat`).

---

## Source Scripts Overview

| Script | CLI Framework | Primary Purpose | Version |
|--------|---------------|-----------------|---------|
| `check_dir_checksum_files.py` | argparse | Check + Generate | N/A |
| `verify_checksums_in_subdirs.py` | argparse | Verify only | N/A |
| `checksum_file_tool.py` | Click | All-in-one | 0.1.0 |

### Evolution Path
```
check_dir_checksum_files.py  ─┐
                              ├──► checksum_file_tool.py (consolidated)
verify_checksums_in_subdirs.py─┘
```

The Click-based `checksum_file_tool.py` appears to be a modernized consolidation of the two argparse-based scripts, adding colored output and a subcommand architecture.

---

## External Dependencies

### CFV Tool (Critical Dependency)

| Property | Value |
|----------|-------|
| **Executable Path** | `C:\Windows\cfv.bat` |
| **Download URL** | https://cfv.sourceforge.net/ |
| **Required** | Yes (scripts will fail without it) |
| **Validation** | None (scripts assume it exists) |

### Python Dependencies

| Module | Used In | Purpose |
|--------|---------|---------|
| `argparse` | check_dir_*, verify_* | CLI argument parsing |
| `click` | checksum_file_tool | CLI framework with colors |
| `os` | All | Directory operations, path handling |
| `sys` | All | Exit codes, stderr |
| `subprocess` | All | Execute external CFV tool |
| `pathlib.Path` | checksum_file_tool | Path type validation |
| `pprint` | checksum_file_tool | Debug output (check-context-object) |

---

## Core Concepts & Terminology

### Checksum File Naming Convention

**Pattern**: `<directory_name><extension>`

**Location**: Inside the directory being checksummed

**Example**:
```
D:\Archive\
├── Photos2023\
│   ├── image1.jpg
│   ├── image2.jpg
│   └── Photos2023.sha1    ← Checksum file
├── Videos2023\
│   ├── video1.mp4
│   └── Videos2023.sha1    ← Checksum file
```

**Path Construction Logic** (identical across all scripts):
```python
sha1_checksum_filepath = os.path.join(entry.path, entry.name) + SHA1_EXT
```

Where:
- `entry.path` = Full path to subdirectory (e.g., `D:\Archive\Photos2023`)
- `entry.name` = Directory name only (e.g., `Photos2023`)
- `SHA1_EXT` = `.sha1`
- Result: `D:\Archive\Photos2023\Photos2023.sha1`

### Directory Scanning Scope

**CRITICAL**: All scripts use **single-level scanning only**.

```python
with os.scandir(root_dir) as it:
    for entry in it:
        if entry.is_dir():
            # Only immediate children, NOT recursive
```

This means:
- `D:\Archive\Photos2023` is scanned
- `D:\Archive\Photos2023\Subfolder` is **NOT** scanned
- Nested directories are ignored entirely

---

## Shared Constants & Conventions

### Constants Defined

| Constant | Value | Used In |
|----------|-------|---------|
| `SHA1_EXT` | `".sha1"` | All scripts |
| `DIR_PATH_ARG` | `"dir_path"` | checksum_file_tool.py only |

### Hardcoded Values

| Value | Location | Purpose |
|-------|----------|---------|
| `"C:\\Windows\\cfv.bat"` | All scripts | CFV executable path |
| `"0.1.0"` | checksum_file_tool.py | Version string |
| `"sha1"` | CFV `-t` flag | Hash algorithm |

---

## Feature Matrix

| Feature | check_dir_* | verify_* | checksum_file_tool |
|---------|-------------|----------|-------------------|
| Check for missing checksums | Yes | No | Yes (`check-4-missing-cfv-files`) |
| Generate missing checksums | Yes (`--calc-checksums`) | No | Yes (`generate-cfv-files`) |
| Verify existing checksums | No | Yes | Yes (`verify-cfv-files`) |
| Verbose mode | Yes (`-v`) | Yes (`-v`) | N/A (always verbose) |
| Colored output | No | No | Yes (green/red) |
| Unicode symbols | No | No | Yes (checkmark/cross) |
| Path validation | No | No | Yes (Click validates) |
| Version flag | No | No | Yes (`--version`) |
| Context object debug | No | No | Yes (`check-context-object`) |

---

## Detailed Functionality Analysis

### Feature 1: Check for Missing Checksum Files

**Purpose**: Scan subdirectories and identify those without a corresponding `.sha1` file.

#### Implementation in `check_dir_checksum_files.py`

**Trigger**: Always runs (primary function)

**Control Flow**:
```
1. Parse arguments (dir_path, --verbose, --calc-checksums)
2. Initialize counters (count_dirs, count_dirs_with_checksums, count_dirs_without_checksums)
3. Initialize list (dirs_without_checksums)
4. For each entry in os.scandir(root_dir):
   a. Skip if not a directory
   b. Increment count_dirs
   c. Construct expected checksum path: <entry.path>/<entry.name>.sha1
   d. If checksum file exists:
      - If verbose: print success message
      - Increment count_dirs_with_checksums
   e. Else:
      - Print warning message (always)
      - Increment count_dirs_without_checksums
      - Append entry.path to dirs_without_checksums
5. If count_dirs == 0:
   - Print error to stderr
   - Exit with code 1
6. Print summary statistics
7. If count_dirs_without_checksums == 0:
   - Print "all up-to-date" message
   - Exit with code 0
8. If --calc-checksums and dirs_without_checksums not empty:
   - [Trigger Feature 2: Generate]
```

**Output Messages**:
```
# Always shown for missing:
WARNING: checksum file doesn't exist for dir: <dirname>

# Verbose only for present:
++++++ Found checksum file for dir: <dirname>

# Summary (always):
# of directories with checksum files: <N>
# of directories without checksum files: <N>

# All OK (when count_dirs_without_checksums == 0):
All checksums appear to be up-to-date
```

#### Implementation in `checksum_file_tool.py`

**Trigger**: Subcommand `check-4-missing-cfv-files`

**Control Flow**:
```
1. Retrieve dir_path from Click context object
2. Initialize counters (same as above)
3. For each entry in os.scandir(dirPath):
   a. Skip if not a directory
   b. Increment count_dirs
   c. Construct expected checksum path
   d. If checksum file exists:
      - Print GREEN checkmark message (always, no verbose flag)
      - Increment count_dirs_with_checksums
   e. Else:
      - Print RED cross mark message
      - Increment count_dirs_without_checksums
      - Append to dirs_without_checksums
4. Print blank line
5. If count_dirs == 0:
   - Print "nothing to do" message (NOT to stderr, no exit)
6. Else:
   - Print summary statistics
   - If count_dirs_without_checksums == 0:
     - Assert invariants
     - Print GREEN "all set" message
```

**Output Messages** (with Unicode and ANSI colors):
```
# Present (green, bold):
✓ checksum file found for [<dirname>]

# Missing (red, bold):
✗ checksum file not found for [<dirname>]

# Summary:
# of directories with CFV files: <N>
# of directories without CFV files: <N>

# All OK (green):
All checksums appear to be up-to-date: you are all set!
```

**Key Differences**:
| Aspect | check_dir_* | checksum_file_tool |
|--------|-------------|-------------------|
| Verbose control | Yes (`-v` flag) | No (always shows all) |
| Colors | No | Yes (green/red) |
| Unicode symbols | No | Yes (✓ ✗) |
| Error handling for 0 dirs | stderr + exit(1) | Friendly message, no exit |
| Can trigger generation | Yes (`--calc-checksums`) | No (separate command) |

---

### Feature 2: Generate Checksum Files

**Purpose**: Create SHA1 checksum files for subdirectories that don't have them.

#### Core Function: `do_calculate_checksums(dir_path) -> bool`

**Identical implementation in both scripts that have it**:

```python
def do_calculate_checksums(dir_path) -> bool:
    program = "C:\\Windows\\cfv.bat"
    result = subprocess.run([program, "-C", "-rr", "-t", "sha1"], cwd=dir_path)
    return result.returncode == 0
```

**CFV Command Breakdown**:
| Flag | Meaning | Effect |
|------|---------|--------|
| `-C` | Create mode | Generate checksum file |
| `-rr` | Recursive files only | Include files in subdirs but create ONE checksum file |
| `-t sha1` | Type SHA1 | Use SHA1 algorithm |

**Working Directory**: Set to `dir_path` via `cwd=` parameter, so CFV creates the file in the correct location.

**Return Value**: Boolean indicating success (return code 0) or failure (non-zero).

**NOTE**: The return value is captured but **never used** for error handling in any script.

#### Implementation in `check_dir_checksum_files.py`

**Trigger**: `--calc-checksums` flag AND `dirs_without_checksums` is not empty

**Control Flow**:
```
1. If --calc-checksums AND len(dirs_without_checksums) > 0:
   a. Initialize count_computed_checksums = 0
   b. Print "Computing checksums in N directories ..."
   c. For each dir_path in dirs_without_checksums:
      - Call do_calculate_checksums(dir_path)
      - Increment count_computed_checksums (unconditionally)
   d. Print "Computed dir checksums for N directories"
```

**Output Messages**:
```
Computing checksums in <N> directories ...
Computed dir checksums for <N> directories
```

**Edge Case**: Counter increments even if CFV fails (no error checking).

#### Implementation in `checksum_file_tool.py`

**Trigger**: Subcommand `generate-cfv-files`

**Control Flow**:
```
1. Retrieve dir_path from context
2. Initialize counters (countCfvFilesGenerated, countDirsScanned)
3. For each entry in os.scandir(dirPath):
   a. Skip if not a directory
   b. Increment countDirsScanned
   c. Construct expected checksum path
   d. If checksum file does NOT exist:
      - Print "Generating cfv checksum file for <path> ..."
      - Call do_calculate_checksums(entry.path)
      - Increment countCfvFilesGenerated
4. If countCfvFilesGenerated > 0:
   - Print "Generated cfv checksums for N directories"
5. Else:
   - Print "No cfv files generated; all sub-directories appear to be up-to-date"
6. Print "Total no. of sub-directories scanned: N"
```

**Output Messages**:
```
# Per directory:
Generating cfv checksum file for <full_path> ...

# Summary (if generated any):
Generated cfv checksums for <N> directories

# Summary (if none generated):
No cfv files generated; all sub-directories appear to be up-to-date

# Always:
Total no. of sub-directories scanned: <N>
```

**Key Differences**:
| Aspect | check_dir_* | checksum_file_tool |
|--------|-------------|-------------------|
| Pre-check for existing | Done in check phase | Done inline |
| Per-file progress | No | Yes |
| Up-to-date message | No | Yes |
| Total scanned count | No | Yes |

---

### Feature 3: Verify Checksum Files

**Purpose**: Validate that existing checksum files match actual file contents.

#### Core Function: `do_verify_checksums(dir_path, checksum_file) -> bool`

**Identical implementation in both scripts that have it**:

```python
def do_verify_checksums(dir_path, checksum_file) -> bool:
    program = "C:\\Windows\\cfv.bat"
    result = subprocess.run([program, "-f", checksum_file], cwd=dir_path)
    return result.returncode == 0
```

**CFV Command Breakdown**:
| Flag | Meaning | Effect |
|------|---------|--------|
| `-f <file>` | Specify checksum file | Use this file for verification |

**Working Directory**: Set to `dir_path` so relative paths in checksum file resolve correctly.

**Return Value**: Boolean indicating verification success/failure.

#### Implementation in `verify_checksums_in_subdirs.py`

**Control Flow**:
```
1. Parse arguments (dir_path, --verbose)
2. Print "Checking all sub-directories in root dir path: <path> ..."
3. Initialize counters and list (but most are unused/commented out)
4. For each entry in os.scandir(root_dir):
   a. Skip if not a directory
   b. Increment count_dirs
   c. Print "dir full path: <entry.path>"
   d. Construct checksum path
   e. Call do_verify_checksums(entry.path, sha1_checksum_filepath)
   f. (Return value ignored)
5. If count_dirs == 0:
   - Print error to stderr
   - Exit with code 1
6. (Remaining code is commented out - incomplete implementation)
```

**Output Messages**:
```
Checking all sub-directories in root dir path: <path> ...
dir full path: <path>
# CFV's own output appears here
```

**NOTE**: This script is **incomplete**:
- Counters `count_dirs_with_checksums` and `count_dirs_without_checksums` are declared but never updated
- Summary statistics are commented out
- `--verbose` flag is parsed but never used
- No success/failure tracking from verification results

#### Implementation in `checksum_file_tool.py`

**Trigger**: Subcommand `verify-cfv-files`

**Control Flow**:
```
1. Retrieve dir_path from context
2. Initialize counters (countDirsScanned, countCfvFilesVerified)
3. For each entry in os.scandir(dirPath):
   a. Skip if not a directory
   b. Increment countDirsScanned
   c. Construct checksum path
   d. Print "Verifying CFV checksum file in <path> ..."
   e. If do_verify_checksums(entry.path, sha1_checksum_filepath) returns True:
      - Increment countCfvFilesVerified
4. If countDirsScanned == 0:
   - Print error to stderr
   - Exit with code 1
5. Print "Tested and verified cfv checksums for N directories"
6. Print "Total no. of sub-directories scanned: N"
```

**Output Messages**:
```
# Per directory:
Verifying CFV checksum file in <full_path> ...
# CFV's own output appears here

# Summary:
Tested and verified cfv checksums for <N> directories
Total no. of sub-directories scanned: <N>

# Error (0 dirs):
ERROR: No sub-directories found
```

**Key Differences**:
| Aspect | verify_* | checksum_file_tool |
|--------|----------|-------------------|
| Progress output | Directory path only | "Verifying..." prefix |
| Success tracking | No | Yes (countCfvFilesVerified) |
| Summary stats | Commented out | Fully implemented |
| Verbose flag | Declared, unused | Not available |

---

## Command-Line Interfaces

### `check_dir_checksum_files.py`

```
usage: check_dir_checksum_files.py [-h] [-v] [--calc-checksums] dir_path

Script to check (and calculate) CFV style checksums in a root directory

positional arguments:
  dir_path          path to the root directory to check

optional arguments:
  -h, --help        show this help message and exit
  -v, --verbose     display verbose output
  --calc-checksums  calculate missing checksums in sub-directories
```

**argparse Configuration**:
- `allow_abbrev=False` - Prevents ambiguous flag abbreviations

### `verify_checksums_in_subdirs.py`

```
usage: verify_checksums_in_subdirs.py [-h] [-v] dir_path

Script to verify/validate CFV style checksums in all sub-dirs of a given root directory

positional arguments:
  dir_path       path to the root directory to start in

optional arguments:
  -h, --help     show this help message and exit
  -v, --verbose  display verbose output
```

**argparse Configuration**:
- `allow_abbrev=False` - Prevents ambiguous flag abbreviations

### `checksum_file_tool.py`

```
Usage: checksum_file_tool.py [OPTIONS] DIR_PATH COMMAND [ARGS]...

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  check-4-missing-cfv-files  Check for missing checksum files (cfv format)
  check-context-object       (Debug command)
  generate-cfv-files         Generate (cfv format) checksum files
  verify-cfv-files           Verify the (cfv format) checksum files
```

**Click Configuration**:
- Uses `@click.group()` for subcommand architecture
- `@click.pass_context` for sharing state between group and commands
- Path validation: `click.Path(exists=True, dir_okay=True, resolve_path=True, file_okay=False, path_type=Path)`
- Version: `@click.version_option("0.1.0", prog_name="checksum_file_tool")`

**Context Object Pattern**:
```python
@click.group()
@click.pass_context
@click.argument("dir_path", type=click.Path(...))
def cli(ctx, dir_path):
    ctx.ensure_object(dict)
    ctx.obj[DIR_PATH_ARG] = dir_path  # DIR_PATH_ARG = "dir_path"
```

Each subcommand retrieves via:
```python
dirPath = ctx.obj[DIR_PATH_ARG]
```

---

## Core Functions & Implementation Details

### Function: `do_calculate_checksums(dir_path) -> bool`

**Present in**: `check_dir_checksum_files.py`, `checksum_file_tool.py`

**Signature**: `def do_calculate_checksums(dir_path) -> bool`

**Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `dir_path` | str or Path | Directory where checksum file should be created |

**Returns**: `bool` - `True` if CFV exited with code 0, `False` otherwise

**Implementation**:
```python
def do_calculate_checksums(dir_path) -> bool:
    program = "C:\\Windows\\cfv.bat"
    result = subprocess.run([program, "-C", "-rr", "-t", "sha1"], cwd=dir_path)
    return result.returncode == 0
```

**Subprocess Details**:
| Aspect | Value |
|--------|-------|
| Command | `cfv.bat -C -rr -t sha1` |
| Working Directory | `dir_path` |
| stdout | Not captured (goes to console) |
| stderr | Not captured (goes to console) |
| Timeout | None (can hang indefinitely) |

**Side Effects**:
- Creates file `<dir_path>/<dirname>.sha1`
- CFV output printed to console

---

### Function: `do_verify_checksums(dir_path, checksum_file) -> bool`

**Present in**: `verify_checksums_in_subdirs.py`, `checksum_file_tool.py`

**Signature**: `def do_verify_checksums(dir_path, checksum_file) -> bool`

**Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `dir_path` | str or Path | Directory containing files to verify |
| `checksum_file` | str | Full path to the `.sha1` checksum file |

**Returns**: `bool` - `True` if verification passed (code 0), `False` otherwise

**Implementation**:
```python
def do_verify_checksums(dir_path, checksum_file) -> bool:
    program = "C:\\Windows\\cfv.bat"
    result = subprocess.run([program, "-f", checksum_file], cwd=dir_path)
    return result.returncode == 0
```

**Subprocess Details**:
| Aspect | Value |
|--------|-------|
| Command | `cfv.bat -f <checksum_file>` |
| Working Directory | `dir_path` |
| stdout | Not captured (goes to console) |
| stderr | Not captured (goes to console) |

---

## Control Flow Diagrams

### Master Control Flow: `check_dir_checksum_files.py`

```
┌─────────────────────────────────────────────────────────────────┐
│                        PROGRAM START                             │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│  PARSE ARGUMENTS                                                 │
│  ├─ dir_path (required, positional)                             │
│  ├─ --verbose / -v (optional flag)                              │
│  └─ --calc-checksums (optional flag)                            │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│  INITIALIZE STATE                                                │
│  ├─ dirs_without_checksums = []                                 │
│  ├─ count_dirs_with_checksums = 0                               │
│  ├─ count_dirs_without_checksums = 0                            │
│  └─ count_dirs = 0                                              │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│  SCAN DIRECTORY: os.scandir(root_dir)                           │
└─────────────────────────────────────────────────────────────────┘
                                 │
                    ┌────────────┴────────────┐
                    ▼                         │
           ┌───────────────┐                  │
           │ Next entry    │◄─────────────────┤
           └───────┬───────┘                  │
                   │                          │
                   ▼                          │
           ┌───────────────┐                  │
           │ entry.is_dir? │──No──────────────┤
           └───────┬───────┘                  │
                   │Yes                       │
                   ▼                          │
           ┌───────────────┐                  │
           │ count_dirs++  │                  │
           └───────┬───────┘                  │
                   │                          │
                   ▼                          │
    ┌──────────────────────────────┐          │
    │ Construct checksum path:     │          │
    │ <entry.path>/<entry.name>.sha1│         │
    └──────────────┬───────────────┘          │
                   │                          │
                   ▼                          │
           ┌───────────────┐                  │
           │ File exists?  │                  │
           └───────┬───────┘                  │
                   │                          │
         ┌─────Yes─┴─No─────┐                 │
         ▼                  ▼                 │
┌─────────────────┐ ┌─────────────────┐       │
│ If verbose:     │ │ Print WARNING   │       │
│ Print "+++++"   │ │ counter++       │       │
│ counter++       │ │ Append to list  │       │
└────────┬────────┘ └────────┬────────┘       │
         │                   │                │
         └─────────┬─────────┘                │
                   │                          │
                   └──────────────────────────┘
                                 │ (loop exhausted)
                                 ▼
                   ┌─────────────────────────┐
                   │ count_dirs == 0?        │
                   └────────────┬────────────┘
                                │
                     ┌────Yes───┴───No────┐
                     ▼                    ▼
          ┌─────────────────┐   ┌─────────────────┐
          │ Print ERROR     │   │ Print summary   │
          │ Exit(1)         │   │ stats           │
          └─────────────────┘   └────────┬────────┘
                                         │
                                         ▼
                   ┌─────────────────────────────────┐
                   │ count_dirs_without_checksums == 0? │
                   └────────────────┬────────────────┘
                                    │
                     ┌─────Yes──────┴──────No──────┐
                     ▼                             ▼
          ┌─────────────────┐           ┌─────────────────────┐
          │ Assert invariants│          │ --calc-checksums    │
          │ Print "up-to-date"│         │ enabled?            │
          │ Exit(0)          │          └──────────┬──────────┘
          └─────────────────┘                      │
                                        ┌────Yes───┴───No────┐
                                        ▼                    ▼
                             ┌─────────────────┐   ┌─────────────────┐
                             │ GENERATION LOOP │   │ Exit (implicit 0)│
                             │ For each dir in │   └─────────────────┘
                             │ dirs_without:   │
                             │ do_calculate()  │
                             └────────┬────────┘
                                      │
                                      ▼
                             ┌─────────────────┐
                             │ Print "Computed"│
                             │ Exit (implicit 0)│
                             └─────────────────┘
```

### Master Control Flow: `verify_checksums_in_subdirs.py`

```
┌─────────────────────────────────────────────────────────────────┐
│                        PROGRAM START                             │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│  PARSE ARGUMENTS                                                 │
│  ├─ dir_path (required, positional)                             │
│  └─ --verbose / -v (optional flag, BUT UNUSED)                  │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│  INITIALIZE STATE (most variables are unused)                    │
│  ├─ dirs_without_checksums = [] (UNUSED)                        │
│  ├─ count_dirs_with_checksums = 0 (UNUSED)                      │
│  ├─ count_dirs_without_checksums = 0 (UNUSED)                   │
│  └─ count_dirs = 0                                              │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│  Print "Checking all sub-directories..."                         │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│  SCAN DIRECTORY: os.scandir(root_dir)                           │
└─────────────────────────────────────────────────────────────────┘
                                 │
                    ┌────────────┴────────────┐
                    ▼                         │
           ┌───────────────┐                  │
           │ Next entry    │◄─────────────────┤
           └───────┬───────┘                  │
                   │                          │
                   ▼                          │
           ┌───────────────┐                  │
           │ entry.is_dir? │──No──────────────┤
           └───────┬───────┘                  │
                   │Yes                       │
                   ▼                          │
           ┌───────────────┐                  │
           │ count_dirs++  │                  │
           └───────┬───────┘                  │
                   │                          │
                   ▼                          │
    ┌──────────────────────────────┐          │
    │ Print "dir full path: ..."   │          │
    └──────────────┬───────────────┘          │
                   │                          │
                   ▼                          │
    ┌──────────────────────────────┐          │
    │ Construct checksum path      │          │
    └──────────────┬───────────────┘          │
                   │                          │
                   ▼                          │
    ┌──────────────────────────────┐          │
    │ do_verify_checksums()        │          │
    │ (return value IGNORED)       │          │
    └──────────────┬───────────────┘          │
                   │                          │
                   └──────────────────────────┘
                                 │ (loop exhausted)
                                 ▼
                   ┌─────────────────────────┐
                   │ count_dirs == 0?        │
                   └────────────┬────────────┘
                                │
                     ┌────Yes───┴───No────┐
                     ▼                    ▼
          ┌─────────────────┐   ┌─────────────────┐
          │ Print ERROR     │   │ (No summary -   │
          │ Exit(1)         │   │ code commented) │
          └─────────────────┘   │ Exit (implicit) │
                                └─────────────────┘
```

### Master Control Flow: `checksum_file_tool.py`

```
┌─────────────────────────────────────────────────────────────────┐
│                        PROGRAM START                             │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│  CLICK GROUP: cli()                                              │
│  ├─ Validate dir_path exists (Click.Path validation)           │
│  ├─ Resolve to absolute path                                    │
│  ├─ Store in context: ctx.obj["dir_path"] = dir_path           │
│  └─ Route to subcommand                                         │
└─────────────────────────────────────────────────────────────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              ▼                  ▼                  ▼
┌───────────────────┐ ┌───────────────────┐ ┌───────────────────┐
│ check-4-missing-  │ │ generate-cfv-     │ │ verify-cfv-       │
│ cfv-files         │ │ files             │ │ files             │
└─────────┬─────────┘ └─────────┬─────────┘ └─────────┬─────────┘
          │                     │                     │
          ▼                     ▼                     ▼
    [See Feature 1]       [See Feature 2]       [See Feature 3]
    [Control Flow]        [Control Flow]        [Control Flow]
```

---

## Error Handling & Edge Cases

### Edge Case 1: Empty Root Directory (No Subdirectories)

| Script | Behavior |
|--------|----------|
| `check_dir_checksum_files.py` | Print "ERROR: No sub-directories found" to stderr, exit(1) |
| `verify_checksums_in_subdirs.py` | Print "ERROR: No sub-directories found" to stderr, exit(1) |
| `checksum_file_tool.py` (check) | Print "No sub-directories found in [path], there is nothing to do." (no exit) |
| `checksum_file_tool.py` (generate) | Print nothing, shows counts as 0 |
| `checksum_file_tool.py` (verify) | Print "ERROR: No sub-directories found" to stderr, exit(1) |

### Edge Case 2: Directory Path Does Not Exist

| Script | Behavior |
|--------|----------|
| `check_dir_checksum_files.py` | `os.scandir()` raises `FileNotFoundError` (unhandled) |
| `verify_checksums_in_subdirs.py` | `os.scandir()` raises `FileNotFoundError` (unhandled) |
| `checksum_file_tool.py` | Click validation prevents execution: "Error: Invalid value for 'DIR_PATH'" |

### Edge Case 3: CFV Tool Not Installed

| Script | Behavior |
|--------|----------|
| All | `subprocess.run()` raises `FileNotFoundError` for missing executable (unhandled) |

### Edge Case 4: CFV Returns Non-Zero Exit Code

| Script | Behavior |
|--------|----------|
| `check_dir_checksum_files.py` | Return value captured but not used; counter increments anyway |
| `verify_checksums_in_subdirs.py` | Return value completely ignored |
| `checksum_file_tool.py` (generate) | Return value captured but not used |
| `checksum_file_tool.py` (verify) | Only counts successful verifications; failures silently excluded |

### Edge Case 5: Permission Denied on Directory

| Script | Behavior |
|--------|----------|
| All | `os.scandir()` raises `PermissionError` (unhandled) |

### Edge Case 6: Checksum File Exists But Is Empty/Corrupted

| Script | Behavior |
|--------|----------|
| Check operations | File existence check passes (considers it "present") |
| Verify operations | CFV will fail verification; behavior per "non-zero exit code" |
| Generate operations | File exists, so generation is skipped |

### Edge Case 7: Subdirectory Name Contains Special Characters

| Script | Behavior |
|--------|----------|
| All | Path construction uses `os.path.join()` which handles this correctly |

### Edge Case 8: Nested Subdirectories

| Script | Behavior |
|--------|----------|
| All | **NOT SCANNED** - only immediate children are processed |

### Edge Case 9: Files (Not Directories) in Root

| Script | Behavior |
|--------|----------|
| All | Silently skipped via `if entry.is_dir()` check |

### Edge Case 10: Symlinks to Directories

| Script | Behavior |
|--------|----------|
| All | `entry.is_dir()` returns True for symlinks to directories; they ARE processed |

---

## Exit Codes

| Code | Script | Condition |
|------|--------|-----------|
| `0` | check_dir_* | All directories have checksums |
| `0` | check_dir_* | Some missing, with or without --calc-checksums (implicit) |
| `0` | verify_* | Normal completion (implicit) |
| `0` | checksum_file_tool | Normal completion (implicit) |
| `1` | check_dir_* | No subdirectories found |
| `1` | verify_* | No subdirectories found |
| `1` | checksum_file_tool (verify) | No subdirectories found |
| `2` | checksum_file_tool | Click usage error (invalid arguments) |

**Note**: None of the scripts exit with an error code when:
- CFV fails to create a checksum
- CFV fails to verify a checksum
- Individual operations fail

---

## Output Formatting & User Feedback

### Message Prefixes and Styles

| Script | Success | Warning/Error |
|--------|---------|---------------|
| check_dir_* | `++++++ Found checksum file for dir:` | `WARNING: checksum file doesn't exist for dir:` |
| verify_* | `dir full path:` | N/A |
| checksum_file_tool | `✓ checksum file found for [name]` (green, bold) | `✗ checksum file not found for [name]` (red, bold) |

### Unicode Characters Used

| Character | Unicode | Description | Used In |
|-----------|---------|-------------|---------|
| ✓ | `\N{check mark}` | Check mark | checksum_file_tool |
| ✗ | `\N{cross mark}` | Cross mark | checksum_file_tool |

### ANSI Color Codes

Used via `click.style()`:
| Color | Meaning | Bold |
|-------|---------|------|
| `green` | Success/present | Yes |
| `red` | Warning/missing | Yes |
| `green` | "All set" message | No |

---

## Assumptions Baked Into The Code

### Critical Assumptions

1. **CFV Installation Location**: All scripts assume CFV is installed at exactly `C:\Windows\cfv.bat`. No fallback, no configuration option.

2. **Checksum File Naming**: The checksum file MUST be named `<dirname>.sha1` and located INSIDE the directory. No support for:
   - Different naming conventions
   - Checksum files in parent directory
   - Multiple checksum files per directory

3. **Single-Level Directory Structure**: Scripts assume a flat structure where the root contains subdirectories, each with their own files. No support for deeper nesting.

4. **SHA1 Algorithm**: Hardcoded to SHA1. No support for SHA256, MD5, or other algorithms.

5. **Windows Platform**: Hardcoded Windows paths and batch file extension.

6. **Directory Homogeneity**: All subdirectories in root are treated equally - no filtering, no exclusions, no patterns.

### Implicit Behavioral Assumptions

7. **CFV Creates Predictable Output**: Assumes CFV creates a file named `<dirname>.sha1` when run with `-C` in a directory. If CFV changes this behavior, scripts break.

8. **CFV Exit Codes**: Assumes:
   - `0` = success
   - Non-zero = failure
   No distinction between different types of failures.

9. **No Concurrent Access**: No file locking or atomic operations. Scripts assume exclusive access to the directory structure.

10. **Immediate Subdirectories Are Relevant**: No filtering mechanism. If a directory exists, it should have a checksum file.

11. **Files Inside Directories Matter**: Assumes each subdirectory contains files worth checksumming. Empty directories are treated the same as populated ones.

---

## Known Limitations & TODOs

### Documented TODOs (from source code comments)

Present in both `check_dir_checksum_files.py` and `verify_checksums_in_subdirs.py`:

```python
# TODO:
#   - add verbose output when the --verbose flag is enabled
#   - also highlight those folders where the existing SHA1 checksum file
#     is "out of date" with respect to the contents of that folder.
#   - look into using the cfv Python package instead of shelling out
#     and calling the cfv program installed on Windows.
```

### Functional Limitations

1. **No Staleness Detection**: Cannot detect when:
   - Files have been added after checksum creation
   - Files have been modified after checksum creation
   - Files have been deleted after checksum creation
   - Only existence of checksum file is checked, not its validity

2. **No Recursive Scanning**: Cannot process nested directory structures.

3. **No Parallel Processing**: Directories are processed sequentially, which is slow for large directory trees.

4. **No Progress Bar**: Long operations provide minimal feedback (tqdm not used despite being available in the project).

5. **No Dry-Run Mode**: Cannot preview what would be done without executing.

6. **No Selective Processing**: Cannot include/exclude directories by pattern or name.

7. **No Logging**: No file-based logging, only console output.

8. **No Configuration File**: All settings are hardcoded or passed via CLI.

### Code Quality Limitations

9. **Inconsistent Naming**:
   - `do_calculate_checksums` vs `do_verify_checksums` (verbs differ)
   - `dirs_without_checksums` vs `countCfvFilesGenerated` (style differs)
   - `SHA1_EXT` vs `sha1_checksum_filepath` (naming convention differs)

10. **Dead Code**: `verify_checksums_in_subdirs.py` has large blocks of commented-out code.

11. **Unused Variables**: Several initialized variables never used (counters in verify script).

12. **No Unit Tests**: No test files found.

13. **No Type Hints**: Function signatures lack complete type annotations.

---

## Platform & Environment Requirements

| Requirement | Value | Notes |
|-------------|-------|-------|
| Operating System | Windows 10/11 | Hardcoded paths |
| Python Version | 3.12 | As specified in CLAUDE.md |
| Package Manager | Pipenv | As specified in CLAUDE.md |
| External Tool | CFV | Must be at `C:\Windows\cfv.bat` |

### Required Python Packages

From scripts:
- `click` (checksum_file_tool.py only)
- `argparse` (stdlib)
- `os` (stdlib)
- `sys` (stdlib)
- `subprocess` (stdlib)
- `pathlib` (stdlib)
- `pprint` (stdlib)

---

## Appendix: CFV Tool Reference

### Installation

Download from: https://cfv.sourceforge.net/

Place `cfv.bat` in `C:\Windows\` directory.

### Flags Used By Scripts

| Flag | Description | Used In |
|------|-------------|---------|
| `-C` | Create checksum file | do_calculate_checksums |
| `-rr` | Recursive files only (not directories) | do_calculate_checksums |
| `-t sha1` | Use SHA1 algorithm | do_calculate_checksums |
| `-f <file>` | Specify checksum file to verify | do_verify_checksums |

### CFV Exit Codes (Observed)

| Code | Meaning |
|------|---------|
| `0` | Success |
| Non-zero | Failure (verification mismatch, file not found, etc.) |

### Checksum File Format

CFV creates files in this format:
```
; Generated by cfv v3.0
;
abcdef1234567890abcdef1234567890abcdef12 *filename1.ext
1234567890abcdef1234567890abcdef12345678 *filename2.ext
```

Each line contains:
- SHA1 hash (40 hex characters)
- Space
- Asterisk (binary mode indicator)
- Filename (relative to checksum file location)

---

## Revision History

| Version | Date | Description |
|---------|------|-------------|
| 1.0 | 2026-01-31 | Initial consolidated specification |
