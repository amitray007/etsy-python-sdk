---
name: maintain-release-check
description: Check for new Etsy Open API releases on GitHub and analyze their impact on the SDK
---

# Check Etsy API Release Notes

Fetch new releases from the Etsy Open API GitHub repo, analyze their impact on the SDK, and guide the user through reviewing changes.

## Step 1: Fetch New Releases

Run the release check script:
```bash
python scripts/check_releases.py
```

- **Exit code 0** — New releases found. Continue to Step 2.
- **Exit code 1** — Up to date. Report this to the user, suggest `/maintain-check` for spec-level changes, and stop.
- **Exit code 2** — Error. Report the error and stop.

## Step 2: Analyze Release Notes

Read `specs/release-notes.md` to load the full release notes.

Present a summary to the user, organized by impact category:

1. **Breaking changes** — Removed fields, deleted endpoints, renamed parameters, changed required fields
2. **Deprecations** — Newly deprecated endpoints, fields, or parameters
3. **Bug fixes affecting SDK behavior** — Fixes that change how the API responds or validates
4. **Schema/type changes** — New fields, type changes, new enum values

For each change, map it to the likely affected SDK files:
- Endpoint changes → `etsy_python/v3/resources/` (resource classes)
- Field/parameter changes → `etsy_python/v3/models/` (request models)
- Enum changes → `etsy_python/v3/enums/` (enum classes)
- Auth/session changes → `etsy_python/v3/resources/Session.py`
- Serialization changes → `etsy_python/v3/common/Utils.py`

## Step 3: Ask User How to Proceed

Use **AskUserQuestion** with these options:

- **"Start reviewing codebase and plan changes"** — Go to Step 4A.
- **"Need more investigation"** — Go to Step 4B.

## Step 4A: Batch Review

For each identified change from Step 2:
1. Read the relevant SDK file(s) mentioned in the mapping
2. Compare current code against what the release notes describe changed
3. Note whether the SDK already handles the change or needs updating

After reviewing all changes, prepare a change list in the same format as `/maintain-audit` Phase 3:

**Must Fix (Breaking/Correctness):**
- Removed fields/endpoints still in SDK
- Changed required fields not reflected in models
- Type mismatches from schema changes

**Should Fix (Completeness):**
- New optional parameters not yet in SDK
- New enum values not reflected in SDK
- Deprecated items not yet marked

**Informational:**
- Bug fixes that don't affect SDK code
- Response-only changes
- Documentation updates

Each item includes: category, description, `file_path:line_number`, and concrete action.

Present the change list to the user, then ask whether to implement or refine.

## Step 4B: Interactive Investigation

Walk through changes one at a time:
1. Present the change from the release notes
2. Read the relevant SDK code
3. Explain the current state vs what changed
4. Ask the user how to proceed (fix now, skip, investigate more)

After all changes are reviewed, summarize decisions made.

## Step 5: Post-Processing

After review is complete:

1. Suggest updating the release check state:
   ```bash
   python scripts/check_releases.py --update
   ```

2. Suggest running `/maintain-audit` for a full spec-level audit to catch any structural changes the release notes didn't mention.

3. If `specs/release-notes.md` was used as context, note that `/maintain-audit` will also pick it up during its Phase 2 review.
