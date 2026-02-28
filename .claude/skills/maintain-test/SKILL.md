---
name: maintain-test
description: Run integration tests against the live Etsy API to validate SDK functionality
---

# Run Integration Tests

## Prerequisites

Ensure `.env` file exists with valid credentials (see `.env.example`).

## Steps

1. Ask the user what scope of tests to run:
   - **All tests**: `pytest tests/ -v`
   - **Read-only only**: `pytest tests/ -m readonly -v`
   - **Write tests only**: `pytest tests/ -m write -v`
   - **Specific resource**: `pytest tests/test_<resource>.py -v`

2. Run the selected tests.

3. For any failures:
   - Read the test file and the corresponding resource/model code
   - Determine if the failure is due to:
     - SDK bug (fix the SDK code)
     - API change (update SDK to match new API behavior)
     - Test environment issue (credentials, permissions, test data)
   - Offer to fix the issue

4. Report a summary:
   - Total tests run / passed / failed / skipped
   - Rate limit info if available
   - Any patterns in failures (e.g., all receipt tests failing = auth scope issue)
