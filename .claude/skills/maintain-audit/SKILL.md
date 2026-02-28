---
name: maintain-audit
description: Audit SDK coverage against the Etsy OAS spec to find gaps, drift, and stale enums
---

# Audit SDK Coverage

Run a full 4-phase audit pipeline: script-based detection, AI-verified review, change list preparation, and user-driven implementation.

## Phase 1: Fetch Spec & Run Audit Script

1. Fetch the latest OAS spec from Etsy:
   ```bash
   python scripts/fetch_spec.py
   ```
   This saves the live spec to `specs/latest.json`. If the fetch fails (network error), fall back
   to `specs/baseline.json` in the next step.

2. Run the audit script against the latest spec:
   ```bash
   python scripts/audit_sdk.py --spec specs/latest.json
   ```
   If `latest.json` doesn't exist (fetch failed), omit `--spec` to use the baseline:
   ```bash
   python scripts/audit_sdk.py
   ```

3. Verify the audit report was generated:
   ```bash
   test -f specs/audit-report.md && echo "OK" || echo "FAIL: audit-report.md not generated"
   ```
   If the file was not generated, stop and report the error to the user.

4. Read `specs/audit-report.md` to load all findings into context.

5. Verify the report contains all expected sections:
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

6. Load the OAS spec from `specs/latest.json`. If it doesn't exist, fall back to `specs/baseline.json`.
   Also load `specs/diff-report.md` if it exists (it highlights what changed since the last baseline).
   Also check for `specs/release-notes.md`. If it exists, read it and use the release notes as additional
   context throughout this phase. Release notes provide human-readable descriptions of what Etsy changed,
   while the spec diff shows structural changes. Cross-reference the two: verify field removals match spec
   changes, check deprecations are marked in spec, note behavioral changes as informational. Prioritize
   reviewing operations mentioned in the release notes during steps 7-14.

7. **Deep-read flagged resource files** — For every operation flagged in Request Body Drift or
   Query/Path Parameter Drift, read the actual resource file in `etsy_python/v3/resources/` AND
   its corresponding model class in `etsy_python/v3/models/`. Compare against the OAS spec entry:
   - Does the model's `mandatory` list match the spec's `required` fields?
   - Does the SDK use the right types? (int vs str, Optional vs required, List vs scalar)
   - Does the SDK enum in `etsy_python/v3/enums/` cover all spec enum values for that parameter?

8. **Serialization correctness** — For POST/PUT/PATCH methods, read the model class and check:
   - Does `todict()` in `etsy_python/v3/common/Utils.py` correctly map field names? The `_type` ->
     `type` mapping is handled, but check for any other `_`-prefixed fields that need similar treatment.
   - Are there fields stored in `self.data` / `self.file` dicts (FileRequest subclasses) that the
     script's body drift comparison could not resolve?

9. **Type mismatches** — The script reports enum value differences but not type mismatches. Spot-check:
   - Integer enum values in spec (e.g., `[0, 1]`) vs SDK string enum values (`"0"`, `"1"`)
   - Spec `integer` fields that SDK accepts as `str` or vice versa
   - Spec `array` fields that SDK types as `Optional[int]` instead of `Optional[List[int]]`

10. **URL path and HTTP method correctness** — For operations flagged in any drift section, compare
   the spec path and method against the SDK endpoint string literal and `Method.*` argument. Ensure
   path parameters match in order and name.

11. **Spot-check mapped operations** — Focus on operations most likely to have issues:
    - Operations whose endpoints had changes in the diff report (if available)
    - Operations with complex request bodies (POST/PUT/PATCH with 10+ fields)
    - Operations with many parameters (5+)

    Read the actual resource and model code. Check that `nullable` lists don't omit fields that
    should be nullable, and `mandatory` lists match the spec's `required` array.

12. **Review stubs** — For "Not Implemented Stubs", determine if the endpoint is needed (active in
    spec, not deprecated) or intentionally skipped. Check if there are related models or enums that
    were partially implemented.

13. **Verify unmapped operations** — For operations the script listed as "Missing Endpoints", search
    SDK resource files manually for naming mismatches. Determine if each is truly missing or just
    named differently.

14. **Verify extra SDK methods** — For methods the script flagged as having no OAS match, check
    if they map to deprecated, removed, or renamed endpoints in the spec.

## Phase 3: Prepare Change List

15. Consolidate ALL findings (script-detected + review-detected) into a single categorized list:

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

    Each item MUST include:
    - Category (Must Fix / Should Fix / Informational)
    - Description of the issue
    - Specific `file_path:line_number` reference
    - What the change should be (concrete action)

16. Present the full change list to the user in a clear, readable format.

## Phase 4: User Decision

17. Use the **AskUserQuestion** tool to ask the user how to proceed:

    - **"Start implementing"** — Proceed to implement all Must Fix and Should Fix items from the
      change list.
    - **"Need changes to the audit tasks"** — Walk through items one at a time or in groups. For
      each item, ask the user to approve, reject, or modify. After all items are reviewed, prepare
      an implementation plan from only the approved items, then implement.

18. After implementation is complete, suggest next steps:
    - Run tests to validate changes (if available locally)
    - Update the baseline spec:
      ```bash
      cp specs/latest.json specs/baseline.json
      ```
