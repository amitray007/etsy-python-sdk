---
name: maintain-audit
description: Audit SDK coverage against the Etsy OAS spec to find gaps, drift, and stale enums
---

# Audit SDK Coverage

Run a full 4-phase audit pipeline: script-based detection, AI-verified review, change list preparation, and user-driven implementation.

## Phase 1: Run Audit Script

1. Run the audit script:
   ```bash
   python scripts/audit_sdk.py
   ```

2. Verify the audit report was generated:
   ```bash
   test -f specs/audit-report.md && echo "OK" || echo "FAIL: audit-report.md not generated"
   ```
   If the file was not generated, stop and report the error to the user.

3. Read `specs/audit-report.md` to load all findings into context.

## Phase 2: Verify & Review Findings

The audit script uses pattern matching (snake_case conversion, AST parsing) which can miss semantic
issues. Now read the actual SDK code and OAS spec to verify and augment the script's findings.

4. Load the OAS spec from `specs/latest.json`. If it doesn't exist, fall back to `specs/baseline.json`.
   Also load `specs/diff-report.md` if it exists (it highlights what changed since the last baseline).

5. **Spot-check "mapped" operations** — focus on operations most likely to have issues:
   - Operations whose endpoints had changes in the diff report (if available)
   - Operations with complex request bodies (POST/PUT/PATCH)
   - Operations with many parameters (5+)

   For each selected operation, read the actual resource file in `etsy_python/v3/resources/` and its
   corresponding model class in `etsy_python/v3/models/`. Compare against the OAS spec entry:
   - Does the model's `mandatory` list match the spec's `required` fields?
   - Are there spec parameters not exposed in the SDK method signature or model?
   - Does the SDK use the right types (int vs str, Optional vs required)?
   - Does the SDK enum in `etsy_python/v3/enums/` cover all spec enum values for that parameter?

6. **Verify "unmapped" operations** — for operations the script couldn't auto-match, search SDK
   resource files manually for naming mismatches. Determine for each: truly missing from the SDK,
   or just named differently?

7. **Verify "extra" SDK methods** — for methods the script flagged as having no OAS match, check
   if they map to deprecated, removed, or renamed endpoints in the spec.

8. **Deep-check request models** — for each model class in `etsy_python/v3/models/`, compare its
   `mandatory` and `nullable` field lists against the corresponding OAS request body's `required`
   array. Flag any discrepancies with `file_path:line_number` references.

## Phase 3: Prepare Change List

9. Consolidate ALL findings (script-detected + review-detected) into a single categorized list:

   **Must Fix (Breaking/Correctness):**
   - Mandatory fields that changed (added or removed from `required`)
   - Removed parameters still present in SDK
   - Type mismatches that would cause API errors
   - Endpoints removed from spec but still in SDK

   **Should Fix (Completeness):**
   - New optional parameters not yet in SDK
   - New enum values not reflected in SDK enum classes
   - Missing endpoints (in spec, not in SDK)
   - Default value mismatches

   **Informational:**
   - Deprecation notices
   - Response schema changes (no SDK code impact, but good to know)
   - Naming inconsistencies between spec and SDK

   Each item MUST include:
   - Category (Must Fix / Should Fix / Informational)
   - Description of the issue
   - Specific `file_path:line_number` reference
   - What the change should be (concrete action)

10. Present the full change list to the user in a clear, readable format.

## Phase 4: User Decision

11. Use the **AskUserQuestion** tool to ask the user how to proceed:

    - **"Start implementing"** — Proceed to implement all Must Fix and Should Fix items from the
      change list.
    - **"Need changes to the audit tasks"** — Walk through items one at a time or in groups. For
      each item, ask the user to approve, reject, or modify. After all items are reviewed, prepare
      an implementation plan from only the approved items, then implement.

12. After implementation is complete, suggest next steps:
    - Run integration tests to validate changes (if available locally)
    - Update the baseline spec:
      ```bash
      cp specs/latest.json specs/baseline.json
      ```
