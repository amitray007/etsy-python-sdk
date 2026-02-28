---
name: maintain-audit
description: Audit SDK coverage against the Etsy OAS spec to find gaps, drift, and stale enums
---

# Audit SDK Coverage

Run a full 7-phase audit pipeline: gather fresh data (spec + release notes + diff), run script-based
detection, AI-verified review, change list preparation, branch setup, implementation with test
verification, and post-implementation workflow (PR, code review, further changes).

## Phase 1: Gather Fresh Data & Run Audit

Before auditing, ensure we're working against the latest API state — not stale files from a previous
session.

1. **Fetch the latest OAS spec:**
   ```bash
   python scripts/fetch_spec.py
   ```
   This saves the live spec to `specs/latest.json`. If the fetch fails (network error), fall back
   to `specs/baseline.json` in subsequent steps.

2. **Check for new Etsy API release notes:**
   ```bash
   python scripts/check_releases.py
   ```
   - Exit code 0 → new releases found, `specs/release-notes.md` generated
   - Exit code 1 → already up to date, no new release notes
   - Exit code 2 → error (report to user, continue with spec-only audit)

3. **Diff spec against baseline** (if spec was fetched successfully):
   ```bash
   python scripts/diff_spec.py
   ```
   This generates `specs/diff-report.md` showing what changed since the baseline.

4. **Run the audit script** against the latest spec:
   ```bash
   python scripts/audit_sdk.py --spec specs/latest.json
   ```
   If `latest.json` doesn't exist (fetch failed), omit `--spec` to use the baseline:
   ```bash
   python scripts/audit_sdk.py
   ```

5. **Verify the audit report was generated:**
   ```bash
   test -f specs/audit-report.md && echo "OK" || echo "FAIL: audit-report.md not generated"
   ```
   If the file was not generated, stop and report the error to the user.

6. **Read all generated reports into context:**
   - `specs/audit-report.md` (always — this is the primary input)
   - `specs/diff-report.md` (if it exists — shows what changed since baseline)
   - `specs/release-notes.md` (if it exists — human-readable changelog from Etsy)

7. **Verify the audit report** contains all expected sections:
   - Coverage Summary
   - Missing Endpoints
   - Not Implemented Stubs
   - Extra SDK Methods
   - Missing Exports
   - Query/Path Parameter Drift
   - Request Body Drift
   - Enum Staleness
   - Deprecation Notices
   - Code Issues

   If any section is missing, the script may have errored — check stderr output.

## Phase 2: AI-Driven Code Review

The audit script handles pattern matching, parameter comparison, enum diffing, and static analysis
automatically. This phase **reads actual SDK code and spec data** to find semantic issues the script
cannot detect. Do not skip this phase — the script catches structural drift but cannot verify logic.

Use the release notes and diff report to **prioritize** which operations to review first. Operations
mentioned in release notes or the diff report are most likely to have issues.

8. Load the OAS spec from `specs/latest.json`. If it doesn't exist, fall back to `specs/baseline.json`.

9. **Deep-read flagged resource files** — For every operation flagged in Request Body Drift or
   Query/Path Parameter Drift, read the actual resource file in `etsy_python/v3/resources/` AND
   its corresponding model class in `etsy_python/v3/models/`. Compare against the OAS spec entry:
   - Does the model's `mandatory` list match the spec's `required` fields?
   - Does the SDK use the right types? (int vs str, Optional vs required, List vs scalar)
   - Does the SDK enum in `etsy_python/v3/enums/` cover all spec enum values for that parameter?

10. **Serialization correctness** — For POST/PUT/PATCH methods, read the model class and check:
    - Does `todict()` in `etsy_python/v3/common/Utils.py` correctly map field names? The `_type` ->
      `type` mapping is handled, but check for any other `_`-prefixed fields that need similar treatment.
    - Are there fields stored in `self.data` / `self.file` dicts (FileRequest subclasses) that the
      script's body drift comparison could not resolve?

11. **Type mismatches** — The script reports enum value differences but not type mismatches. Spot-check:
    - Integer enum values in spec (e.g., `[0, 1]`) vs SDK string enum values (`"0"`, `"1"`)
    - Spec `integer` fields that SDK accepts as `str` or vice versa
    - Spec `array` fields that SDK types as `Optional[int]` instead of `Optional[List[int]]`

12. **URL path and HTTP method correctness** — For operations flagged in any drift section, compare
    the spec path and method against the SDK endpoint string literal and `Method.*` argument. Ensure
    path parameters match in order and name.

13. **Spot-check mapped operations** — Focus on operations most likely to have issues:
    - Operations mentioned in release notes or diff report
    - Operations with complex request bodies (POST/PUT/PATCH with 10+ fields)
    - Operations with many parameters (5+)

    Read the actual resource and model code. Check that `nullable` lists don't omit fields that
    should be nullable, and `mandatory` lists match the spec's `required` array.

14. **Review stubs** — For "Not Implemented Stubs", determine if the endpoint is needed (active in
    spec, not deprecated) or intentionally skipped. Check if there are related models or enums that
    were partially implemented.

15. **Verify unmapped operations** — For operations the script listed as "Missing Endpoints", search
    SDK resource files manually for naming mismatches. Determine if each is truly missing or just
    named differently.

16. **Verify extra SDK methods** — For methods the script flagged as having no OAS match, check
    if they map to deprecated, removed, or renamed endpoints in the spec.

## Phase 3: Prepare Change List

17. Consolidate ALL findings (script-detected + review-detected + release-note-informed) into a
    single categorized list:

    **Must Fix (Breaking/Correctness):**
    - Implicit string concatenation bugs from Code Issues (script-detected — these are real bugs)
    - Mandatory fields that changed (added or removed from `required`)
    - Type mismatches that would cause API errors
    - Endpoints removed from spec but still in SDK

    **Should Fix (Completeness):**
    - Missing `__init__.py` exports for resource classes intended to be public
    - Request body field drift (fields in spec not in model, or vice versa)
    - Not-implemented stubs for endpoints that have active spec definitions
    - New optional parameters not yet in SDK
    - New enum values not reflected in SDK enum classes
    - Missing endpoints (in spec, not in SDK)

    **Informational:**
    - Deprecation notices (from both `deprecated: true` and description text)
    - Response schema changes (no SDK code impact, but good to know)
    - Naming inconsistencies between spec and SDK
    - Behavioral changes from release notes that don't require code changes

    Each item MUST include:
    - Category (Must Fix / Should Fix / Informational)
    - Description of the issue
    - Specific `file_path:line_number` reference
    - What the change should be (concrete action)

18. Present the full change list to the user in a clear, readable format. Include a summary line
    at the top: "Found N Must Fix, N Should Fix, N Informational items."

## Phase 4: User Decision

19. Use the **AskUserQuestion** tool to ask the user how to proceed:

    - **"Start implementing"** — Proceed to Phase 5 (branch setup) then Phase 6 (implementation).
    - **"Need changes to the audit tasks"** — Walk through items one at a time or in groups. For
      each item, ask the user to approve, reject, or modify. After all items are reviewed, prepare
      an implementation plan from only the approved items, then proceed to Phase 5.

## Phase 5: Branch Setup

Before writing any code, establish the correct git branch.

20. Use **AskUserQuestion** to ask the user about branch strategy:

    - **"Work on current branch"** — Stay on the current git branch. Verify it is clean
      (`git status`). If there are uncommitted changes, warn the user and ask whether to proceed
      or stash first.
    - **"Create a new release branch"** — Create a new branch from `master` using a release-style
      name derived from the latest Etsy release tag found in step 2 (e.g.,
      `release/etsy-api-2025-10-24`). If no new releases were found, use the current date
      (e.g., `release/sdk-audit-2026-03-01`).

21. If creating a new branch:
    ```bash
    git fetch origin master
    git checkout -b <branch-name> origin/master
    ```
    Verify the branch is up to date with master before proceeding. If `master` does not exist,
    try `main` as a fallback.

22. If working on the current branch, simply confirm the branch name and proceed.

## Phase 6: Implementation & Test Verification

23. Implement all approved changes from the change list (Must Fix + Should Fix items). Use
    **TaskCreate** to track progress on each item. Mark tasks `in_progress` when starting and
    `completed` when done.

24. After all changes are implemented, run the test suite:
    ```bash
    pytest -v
    ```

25. **If tests fail:**
    - Read the failure output and identify which tests broke.
    - Determine if failures are caused by the audit changes (expected — update tests to match)
      or by regressions (unexpected — fix the implementation).
    - Fix all failures and re-run `pytest -v` until all tests pass.
    - Do NOT proceed to step 26 until the full test suite is green.

26. **Once all tests pass**, update the baseline and release tracking:
    ```bash
    cp specs/latest.json specs/baseline.json
    ```
    If new releases were found in step 2:
    ```bash
    python scripts/check_releases.py --update
    ```

27. Stage and commit all changes with a descriptive commit message summarizing the audit changes.
    Use semantic commit prefix `feat:` for new endpoints or `fix:` for correctness fixes,
    whichever is dominant. Example:
    ```
    feat: sync SDK with Etsy API spec (Oct 2025 releases)
    ```

## Phase 7: Post-Implementation Workflow

After committing, use **AskUserQuestion** to ask the user what to do next. This is an iterative
loop — after completing any option, return to this question until the user is satisfied.

28. Present options via **AskUserQuestion**:

    - **"Raise a PR"** — Go to step 29.
    - **"Run code review"** — Go to step 30.
    - **"Run tests"** — Go to step 31.
    - **"Make additional changes"** — Go to step 32.

### Raise a PR (step 29)

29. Push the branch and create a pull request:
    ```bash
    git push -u origin <branch-name>
    ```
    Use `gh pr create` with:
    - Title summarizing the audit (e.g., "Sync SDK with Etsy API spec — Oct 2025 releases")
    - Body containing the change list summary from Phase 3 (Must Fix / Should Fix counts and
      key highlights), formatted with `## Summary` and `## Test plan` sections
    - Assign the current user as reviewer (`--assignee @me`)
    - Add relevant labels (`--label sdk-sync` or similar if labels exist; skip if they don't)

    After the PR is created, return the PR URL to the user and loop back to step 28.

### Run code review (step 30)

30. Use the **superpowers:requesting-code-review** skill or the **pr-review-toolkit:review-pr**
    skill to perform a thorough code review of the changes. Present all findings categorized by
    severity.

    After presenting review findings, use **AskUserQuestion** to ask for each issue:
    - **"Fix this"** — Apply the fix immediately.
    - **"Skip this"** — Move to the next issue.
    - **"Fix all remaining"** — Apply all remaining suggested fixes.

    If any fixes were applied, re-run `pytest -v` to verify nothing broke, then commit the
    review fixes as a separate commit (e.g., `fix: address code review feedback`).

    Loop back to step 28.

### Run tests (step 31)

31. Run the full test suite:
    ```bash
    pytest -v
    ```
    Report results to the user. If failures are found, use **AskUserQuestion** to ask:
    - **"Fix failures"** — Diagnose and fix each failure, then re-run.
    - **"Skip for now"** — Continue without fixing.

    Loop back to step 28.

### Make additional changes (step 32)

32. Use **AskUserQuestion** to ask the user what additional changes they want. Implement them,
    run tests to verify, and commit. Loop back to step 28.
