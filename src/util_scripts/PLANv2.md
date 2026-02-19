# Plan v2: Consolidate Checksum Scripts into checksum_file_tool.py

## Objective
Update `checksum_file_tool.py` to incorporate all features from:
- `check_dir_checksum_files.py`
- `verify_checksums_in_subdirs.py`

This consolidation follows the evolution path documented in DETAILS.md:
```
check_dir_checksum_files.py  ─┐
                              ├──► checksum_file_tool.py (consolidated)
verify_checksums_in_subdirs.py─┘
```

## Files to Modify
- `D:\wa_git\python_misc_code\src\util_scripts\checksum_file_tool.py`

---

## Comprehensive Feature Gap Analysis

| Feature | check_dir_* | verify_* | checksum_file_tool | Action Required |
|---------|-------------|----------|-------------------|-----------------|
| Check for missing checksums | Yes | No | Yes | None |
| Generate missing checksums | Yes (`--calc-checksums`) | No | Yes (separate cmd) | Add `--calc-checksums` option |
| Verify existing checksums | No | Yes | Yes | None |
| **Verbose mode (`-v`)** | Yes (implemented) | Yes (declared, unused) | No | **Add global flag** |
| Colored output | No | No | Yes | None |
| Unicode symbols | No | No | Yes | None |
| Path validation | No | No | Yes (Click) | None |
| Version flag | No | No | Yes | None |
| Context object debug | No | No | Yes | None |
| Exit code for 0 subdirs | Exit(1) | Exit(1) | Mixed | Standardize |

---

## Phase 1: Add Global Verbose Flag

**Goal:** Add a `--verbose/-v` flag at the Click group level that propagates to all commands via the context object.

### Rationale (from DETAILS.md)
Both legacy scripts declare `-v/--verbose`:
- `check_dir_checksum_files.py`: Implemented - shows `++++++ Found checksum file for dir:` when verbose
- `verify_checksums_in_subdirs.py`: Declared but unused (documented as a TODO)

### Implementation

**1.1 Add constant** (after line 26):
```python
VERBOSE_FLAG = "verbose"
```

**1.2 Modify `cli()` group** (lines 44-56):
```python
@click.group()
@click.pass_context
@click.version_option("0.1.0", prog_name="checksum_file_tool")
@click.option("-v", "--verbose", is_flag=True, help="Display verbose output")
@click.argument(
    "dir_path",
    type=click.Path(
        exists=True, dir_okay=True, resolve_path=True, file_okay=False, path_type=Path
    ),
)
def cli(ctx, dir_path, verbose):
    ctx.ensure_object(dict)
    ctx.obj[DIR_PATH_ARG] = dir_path
    ctx.obj[VERBOSE_FLAG] = verbose
```

### Expected CLI Help Output
```
Usage: checksum_file_tool.py [OPTIONS] DIR_PATH COMMAND [ARGS]...

Options:
  --version      Show the version and exit.
  -v, --verbose  Display verbose output
  --help         Show this message and exit.
```

---

## Phase 2: Enhance `check-4-missing-cfv-files` Command

**Goal:** Add `--calc-checksums` option and verbose output support.

### Rationale (from DETAILS.md)
From `check_dir_checksum_files.py`, the `--calc-checksums` flag enables:
```
1. If --calc-checksums AND len(dirs_without_checksums) > 0:
   a. Initialize count_computed_checksums = 0
   b. Print "Computing checksums in N directories ..."
   c. For each dir_path in dirs_without_checksums:
      - Call do_calculate_checksums(dir_path)
      - Increment count_computed_checksums
   d. Print "Computed dir checksums for N directories"
```

### Implementation

**2.1 Add `--calc-checksums` option to command decorator:**
```python
@cli.command("check-4-missing-cfv-files")
@click.option("--calc-checksums", is_flag=True,
              help="Calculate missing checksums in sub-directories")
@click.pass_context
def checkForMissingCfvFiles(ctx, calc_checksums):
```

**2.2 Read verbose flag from context:**
```python
verbose = ctx.obj[VERBOSE_FLAG]
```

**2.3 Add verbose output for directories WITH checksums:**
When verbose is True and checksum exists, also show the full path:
```python
if verbose:
    click.echo(f"  Path: {entry.path}")
```

**2.4 Add generation logic at end of function:**
After the existing logic, before the final summary:
```python
if calc_checksums and dirs_without_checksums:
    click.echo()
    click.echo(f"Computing checksums in {len(dirs_without_checksums)} directories ...")
    count_computed = 0
    for dir_path in dirs_without_checksums:
        if verbose:
            click.echo(f"  Generating checksum for: {dir_path}")
        do_calculate_checksums(dir_path)
        count_computed += 1
    click.echo(
        click.style(
            f"Computed checksums for {count_computed} directories",
            fg="green",
        )
    )
```

### Expected Output Messages

**Normal mode (missing checksum):**
```
✗ checksum file not found for [dirname]
```

**Verbose mode (found checksum):**
```
✓ checksum file found for [dirname]
  Path: D:\Archive\dirname
```

**With `--calc-checksums`:**
```
Computing checksums in 3 directories ...
Computed checksums for 3 directories
```

---

## Phase 3: Enhance `verify-cfv-files` Command

**Goal:** Add verbose output and improve verification status tracking with colored output.

### Rationale (from DETAILS.md)
Current `checksum_file_tool.py` verify command:
- Only counts successful verifications
- Failures silently excluded from count
- No colored per-directory status

The legacy `verify_checksums_in_subdirs.py`:
- Prints `dir full path: <path>` for each directory
- Has documented TODO for verbose output

### Implementation

**3.1 Read verbose flag:**
```python
verbose = ctx.obj[VERBOSE_FLAG]
```

**3.2 Track both success and failure counts:**
```python
countCfvFilesVerified = 0
countCfvFilesFailed = 0
```

**3.3 Add colored status output for each verification:**
```python
if do_verify_checksums(entry.path, sha1_checksum_filepath):
    countCfvFilesVerified += 1
    if verbose:
        click.echo(
            click.style(f"  ✓ Verification passed", fg="green")
        )
else:
    countCfvFilesFailed += 1
    click.echo(
        click.style(f"  ✗ Verification FAILED", fg="red", bold=True)
    )
```

**3.4 Enhanced summary:**
```python
click.echo()
click.echo(f"Verified: {countCfvFilesVerified} | Failed: {countCfvFilesFailed}")
click.echo(f"Total sub-directories scanned: {countDirsScanned}")

if countCfvFilesFailed > 0:
    click.echo(
        click.style(
            f"WARNING: {countCfvFilesFailed} verification(s) failed!",
            fg="red",
            bold=True,
        )
    )
```

### Expected Output

**Normal mode:**
```
Verifying CFV checksum file in D:\Archive\Photos2023 ...
[CFV output here]
Verifying CFV checksum file in D:\Archive\Videos2023 ...
[CFV output here]

Verified: 2 | Failed: 0
Total sub-directories scanned: 2
```

**Verbose mode with failure:**
```
Verifying CFV checksum file in D:\Archive\Photos2023 ...
[CFV output here]
  ✓ Verification passed
Verifying CFV checksum file in D:\Archive\Videos2023 ...
[CFV output here]
  ✗ Verification FAILED

Verified: 1 | Failed: 1
Total sub-directories scanned: 2
WARNING: 1 verification(s) failed!
```

---

## Phase 4: Enhance `generate-cfv-files` Command

**Goal:** Add verbose output support with colored styling.

### Implementation

**4.1 Read verbose flag:**
```python
verbose = ctx.obj[VERBOSE_FLAG]
```

**4.2 Add verbose detail for skipped directories:**
Currently, directories with existing checksums are silently skipped. In verbose mode, report them:
```python
if not os.path.exists(sha1_checksum_filepath):
    click.echo(f"Generating cfv checksum file for {entry.path} ...")
    do_calculate_checksums(entry.path)
    countCfvFilesGenerated += 1
elif verbose:
    click.echo(
        click.style(
            f"Skipping {entry.name} (checksum already exists)",
            fg="yellow",
        )
    )
```

**4.3 Use Click styled output for consistency:**
```python
if countCfvFilesGenerated > 0:
    click.echo(
        click.style(
            f"Generated cfv checksums for {countCfvFilesGenerated} directories",
            fg="green",
        )
    )
else:
    click.echo(
        click.style(
            "No cfv files generated; all sub-directories appear to be up-to-date",
            fg="green",
        )
    )
click.echo(f"Total sub-directories scanned: {countDirsScanned}")
```

---

## Implementation Checklist

### Constants (add after line 26)
- [x] `VERBOSE_FLAG = "verbose"` ✓ COMPLETED

### `cli()` Group (lines 44-56)
- [x] Add `@click.option("-v", "--verbose", is_flag=True, ...)` ✓ COMPLETED
- [x] Update function signature: `def cli(ctx, dir_path, verbose):` ✓ COMPLETED
- [x] Store in context: `ctx.obj[VERBOSE_FLAG] = verbose` ✓ COMPLETED

### Additional Improvements (Phase 1)
- [x] Added custom `validate_dir_path()` callback for styled error messages ✓ COMPLETED
- [x] Standardized all console output to use `click.echo()` instead of `print()` ✓ COMPLETED
- [x] Applied consistent rich-text formatting throughout script ✓ COMPLETED

### `checkForMissingCfvFiles()` (lines 65-126)
- [ ] Add `@click.option("--calc-checksums", is_flag=True, ...)`
- [ ] Update function signature to include `calc_checksums`
- [ ] Read `verbose` from context
- [ ] Add verbose output for directories with checksums
- [ ] Add generation logic when `--calc-checksums` is set

### `verifyCfvFiles()` (lines 161-189)
- [ ] Read `verbose` from context
- [ ] Add `countCfvFilesFailed` counter
- [ ] Add colored status output per verification
- [ ] Show pass/fail counts in summary
- [ ] Add warning message when failures exist

### `generateCfvFiles()` (lines 128-158)
- [ ] Read `verbose` from context
- [ ] Add verbose output for skipped directories
- [ ] Use `click.style()` for summary messages

---

## Edge Case Handling (from DETAILS.md)

| Edge Case | Current Behavior | Expected After Changes |
|-----------|------------------|------------------------|
| Empty root directory (0 subdirs) | check: friendly message; verify: exit(1) | Keep existing behavior |
| Directory path doesn't exist | Click validates and rejects | Keep existing behavior |
| CFV tool not installed | FileNotFoundError (unhandled) | Keep existing behavior (out of scope) |
| CFV returns non-zero | Failures silently excluded | Show failure count and warning |
| Permission denied on directory | PermissionError (unhandled) | Keep existing behavior (out of scope) |
| Checksum file exists but empty/corrupted | Treated as "present" for check; fails verify | Keep existing behavior |
| Symlinks to directories | Processed (is_dir=True) | Keep existing behavior |

---

## Testing Plan

### Test Environment Setup
```bash
cd D:\wa_git\python_misc_code\src\util_scripts
pipenv shell
```

### Test Directory Structure
Create the following structure for testing:
```
test_checksums/
├── dir_with_valid_checksum/
│   ├── file1.txt
│   └── dir_with_valid_checksum.sha1    # Valid checksum
├── dir_with_invalid_checksum/
│   ├── file2.txt                        # Modified after checksum
│   └── dir_with_invalid_checksum.sha1   # Now invalid
├── dir_without_checksum/
│   └── file3.txt
└── empty_dir/
```

---

### Phase 1 Tests: Global Verbose Flag

| ID | Test Case | Command | Expected Result |
|----|-----------|---------|-----------------|
| T1.1 | Help shows verbose flag | `python checksum_file_tool.py --help` | Shows `-v, --verbose` option |
| T1.2 | Verbose flag accepted before dir | `python checksum_file_tool.py -v <dir> check-4-missing-cfv-files` | Runs without error |
| T1.3 | Verbose flag position | `python checksum_file_tool.py <dir> -v check-4-missing-cfv-files` | Error (flag must be before positional arg) |

---

### Phase 2 Tests: Check Command Enhancements

| ID | Test Case | Command | Expected Result |
|----|-----------|---------|-----------------|
| T2.1 | Check without verbose | `python checksum_file_tool.py <dir> check-4-missing-cfv-files` | Standard output (checkmarks/crosses only) |
| T2.2 | Check with verbose | `python checksum_file_tool.py -v <dir> check-4-missing-cfv-files` | Shows paths for found checksums |
| T2.3 | Check shows calc-checksums in help | `python checksum_file_tool.py <dir> check-4-missing-cfv-files --help` | Shows `--calc-checksums` option |
| T2.4 | Check with calc-checksums (missing dirs) | `python checksum_file_tool.py <dir_with_missing> check-4-missing-cfv-files --calc-checksums` | Lists missing AND generates checksums |
| T2.5 | Check with calc-checksums (all present) | `python checksum_file_tool.py <dir_all_present> check-4-missing-cfv-files --calc-checksums` | Reports all up-to-date, no generation |
| T2.6 | Verify generation actually created files | After T2.4, run check again | Previously missing dirs now show checkmarks |

---

### Phase 3 Tests: Verify Command Enhancements

| ID | Test Case | Command | Expected Result |
|----|-----------|---------|-----------------|
| T3.1 | Verify without verbose (all pass) | `python checksum_file_tool.py <dir_all_valid> verify-cfv-files` | Shows "Verifying..." and summary counts |
| T3.2 | Verify with verbose (all pass) | `python checksum_file_tool.py -v <dir_all_valid> verify-cfv-files` | Shows green checkmarks per directory |
| T3.3 | Verify with failures | `python checksum_file_tool.py <dir_with_invalid> verify-cfv-files` | Shows failure count and red warning |
| T3.4 | Verify with verbose + failures | `python checksum_file_tool.py -v <dir_with_invalid> verify-cfv-files` | Shows red X for failed, green check for passed |
| T3.5 | Verify empty directory | `python checksum_file_tool.py <empty_dir> verify-cfv-files` | Error: No sub-directories found (exit 1) |

---

### Phase 4 Tests: Generate Command Enhancements

| ID | Test Case | Command | Expected Result |
|----|-----------|---------|-----------------|
| T4.1 | Generate without verbose | `python checksum_file_tool.py <dir> generate-cfv-files` | Shows "Generating..." for missing only |
| T4.2 | Generate with verbose | `python checksum_file_tool.py -v <dir> generate-cfv-files` | Also shows "Skipping..." for existing |
| T4.3 | Generate all present | `python checksum_file_tool.py <dir_all_present> generate-cfv-files` | Shows "No cfv files generated" in green |
| T4.4 | Generate with verbose all present | `python checksum_file_tool.py -v <dir_all_present> generate-cfv-files` | Shows yellow "Skipping" for each |

---

### Integration Tests

| ID | Test Case | Steps | Expected Result |
|----|-----------|-------|-----------------|
| T5.1 | Full workflow | 1. Check (shows missing)<br>2. Generate<br>3. Verify | All steps complete, verify passes |
| T5.2 | Check + generate in one | `check-4-missing-cfv-files --calc-checksums` | Single command does both |
| T5.3 | Compare with legacy check script | Run both on same directory | Equivalent functionality (different formatting) |
| T5.4 | Compare with legacy verify script | Run both on same directory | Equivalent functionality |

---

### Regression Tests

| ID | Test Case | Command | Expected Result |
|----|-----------|---------|-----------------|
| T6.1 | Version flag still works | `python checksum_file_tool.py --version` | Shows "checksum_file_tool, version 0.1.0" |
| T6.2 | Invalid path rejected | `python checksum_file_tool.py /nonexistent check-4-missing-cfv-files` | Click error: Invalid value for 'DIR_PATH' |
| T6.3 | Debug command still works | `python checksum_file_tool.py <dir> check-context-object` | Shows context dict with dir_path and verbose |

---

## Verification Checklist

### Functional Verification
- [ ] `--verbose/-v` flag works at group level
- [ ] Verbose flag value passed to all commands
- [ ] `--calc-checksums` generates missing checksum files
- [ ] Verification tracks and reports failures
- [ ] Colored output maintained for all commands
- [ ] Unicode symbols (✓ ✗) work correctly

### Backward Compatibility
- [ ] All existing commands work without new flags
- [ ] Output format matches existing style (with enhancements)
- [ ] Exit codes unchanged for existing scenarios
- [ ] `check-context-object` debug command shows new context values

### Error Handling
- [ ] Empty directory case handled consistently
- [ ] CFV failures properly counted and reported
- [ ] Invalid path rejected by Click validation

---

## Future Enhancements (Out of Scope)

From documented TODOs in DETAILS.md (not addressed in this plan):
1. Detect "out of date" checksum files (staleness detection)
2. Use cfv Python package instead of shelling out
3. Recursive scanning of nested directories
4. Parallel processing for large directory trees
5. Dry-run mode
6. Progress bars using tqdm
