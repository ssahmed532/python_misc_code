# Next Steps

## Current State

### Security Review
- Clean - no vulnerabilities found in the CLAUDE.md changes (documentation-only diff).

### Working Tree Status
| File | Status | Description |
|------|--------|-------------|
| `CLAUDE.md` | Modified (unstaged) | Expanded documentation with architecture details, key patterns, and running instructions |
| `src/util_scripts/DETAILS.md` | Untracked | Comprehensive reverse-engineered specification of all three checksum scripts |
| `src/util_scripts/PLAN.md` | Untracked | Initial consolidation plan (superseded by PLANv2) |
| `src/util_scripts/PLANv2.md` | Untracked | Detailed 4-phase implementation plan with test matrix |
| `src/util_scripts/.claude/` | Untracked | Claude Code project-local settings |
| `src/nul` | Untracked | Likely accidental artifact from a Windows `> nul` redirect |

### Planning Artifacts Produced
- **`DETAILS.md`** - Full PRD-style specification covering all three checksum scripts, their control flows, edge cases, CFV tool reference, and known limitations.
- **`PLANv2.md`** - Implementation plan with feature gap analysis, per-phase code snippets, expected output examples, a 20+ item test matrix, and a verification checklist.

---

## Recommended Next Steps

### Step 1: Commit Documentation Work
Commit the planning and documentation files before starting implementation.

**Files to stage:**
- `CLAUDE.md` (modified)
- `src/util_scripts/DETAILS.md` (new)
- `src/util_scripts/PLAN.md` (new)
- `src/util_scripts/PLANv2.md` (new)

### Step 2: Clean Up Stray File
Delete `src/nul` - this is an accidental artifact, likely created by a Windows shell redirect (`> nul` interpreted as a filename in a Unix-style shell).

### Step 3: Implement PLANv2
All changes target a single file: `src/util_scripts/checksum_file_tool.py`.

#### Phase 1: Add Global Verbose Flag
- Add `VERBOSE_FLAG = "verbose"` constant
- Add `@click.option("-v", "--verbose", ...)` to the `cli()` group
- Store `verbose` in `ctx.obj` for propagation to all subcommands

#### Phase 2: Enhance `check-4-missing-cfv-files`
- Add `--calc-checksums` flag (mirrors legacy `check_dir_checksum_files.py` behavior)
- Add verbose output showing paths for directories with existing checksums
- Add generation loop when `--calc-checksums` is set and missing directories exist

#### Phase 3: Enhance `verify-cfv-files`
- Track both success and failure counts (currently only tracks successes)
- Add colored per-directory pass/fail status in verbose mode
- Add red warning message when any verifications fail
- Show pass/fail breakdown in summary

#### Phase 4: Enhance `generate-cfv-files`
- Add verbose output for skipped directories (those already having checksums)
- Use `click.style()` for colored summary messages

### Step 4: Manual Testing
No test framework exists. Follow the test matrix in `PLANv2.md`:

| Test Group | IDs | Coverage |
|------------|-----|----------|
| Verbose flag | T1.1 - T1.3 | Flag appears in help, accepted in correct position |
| Check command | T2.1 - T2.6 | With/without verbose, with/without `--calc-checksums` |
| Verify command | T3.1 - T3.5 | All pass, with failures, empty directory, verbose mode |
| Generate command | T4.1 - T4.4 | With/without verbose, all present vs some missing |
| Integration | T5.1 - T5.4 | Full workflow, single-command check+generate, legacy comparison |
| Regression | T6.1 - T6.3 | `--version`, invalid path, debug command |

### Step 5: Retire Legacy Scripts
After confirming feature parity between `checksum_file_tool.py` and the two legacy scripts:
- `check_dir_checksum_files.py` (argparse, check + generate)
- `verify_checksums_in_subdirs.py` (argparse, verify only, incomplete)

Options: archive to a `legacy/` directory or delete outright.

---

## Future Enhancements (Out of Scope for Current Work)
Documented in `DETAILS.md` and `PLANv2.md` as known limitations:

1. Staleness detection - identify checksum files that are out of date relative to directory contents
2. Use the `cfv` Python package instead of shelling out to `cfv.bat`
3. Recursive scanning of nested directory structures
4. Parallel processing for large directory trees
5. Dry-run mode
6. Progress bars using tqdm
