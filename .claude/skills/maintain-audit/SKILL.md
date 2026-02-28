---
name: maintain-audit
description: Audit SDK coverage against the Etsy OAS spec to find gaps, drift, and stale enums
---

# Audit SDK Coverage

## Steps

1. Run the audit script:
   ```bash
   python scripts/audit_sdk.py
   ```

2. Read the audit report at `specs/audit-report.md` and present findings to the user.

3. For each category of findings, provide actionable guidance:

   **Missing Endpoints:**
   - Show the OAS operation details (method, path, parameters)
   - Identify which resource file should contain the new method
   - Offer to implement the missing method following existing patterns

   **Extra SDK Methods:**
   - Check if the method was removed from the spec or renamed
   - Suggest deprecation or removal

   **Parameter Drift:**
   - Show what the spec expects vs what the SDK has
   - Identify the specific file and line to modify
   - Offer to update the method signature or model class

   **Enum Staleness:**
   - Show missing/extra enum values
   - Identify the enum file to update
   - Offer to add missing values

4. Suggest next steps:
   - Implement the changes identified
   - Run `/maintain-test` to validate changes work against the live API
   - After all changes are applied, update the baseline:
     ```bash
     cp specs/latest.json specs/baseline.json
     ```
