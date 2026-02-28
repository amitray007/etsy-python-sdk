---
name: check
description: Fetch the latest Etsy OAS spec and diff it against the baseline to detect API changes
---

# Check for Etsy API Changes

## Steps

1. Run the fetch script to download the latest spec:
   ```bash
   python scripts/fetch_spec.py
   ```

2. If changes were detected (exit code 0), run the diff script:
   ```bash
   python scripts/diff_spec.py
   ```

3. Read the diff report at `specs/diff-report.md` and present a summary to the user.

4. Highlight:
   - **Breaking changes** (removed endpoints, removed parameters, type changes)
   - **New endpoints** that may need SDK support
   - **Deprecations** that should be noted
   - **Enum changes** that may require updating SDK enums

5. If no changes detected, report that the SDK is up to date with the spec.

6. Suggest next steps:
   - Run `/maintain:audit` to check how these changes affect SDK coverage
   - Check https://github.com/etsy/open-api/releases for human-readable changelogs
