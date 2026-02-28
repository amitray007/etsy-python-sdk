# Etsy SDK Maintenance Workflow Design

**Date**: 2026-02-28
**Status**: Approved
**Author**: Amit Ray + Claude Code

## Problem

As a solo maintainer, keeping the Etsy Python SDK in sync with Etsy's evolving OpenAPI spec is entirely manual. The current workflow involves reading release notes, manually comparing documentation, and hoping nothing breaks. There are no tests to catch drift, no automated diffing, and no structured way to identify what SDK code needs updating.

## Goals

1. **Detect API changes** — On-demand tooling to fetch the latest Etsy OAS spec and produce a structured diff report against a known baseline.
2. **Audit SDK coverage** — Cross-reference the OAS spec against SDK resource/model/enum code to identify gaps, stale parameters, and missing endpoints.
3. **Test against live API** — Full CRUD integration test suite hitting a real Etsy test shop to validate the SDK works against the current API.
4. **Claude Code integration** — Skills that orchestrate these tools conversationally via `/maintain:check`, `/maintain:audit`, `/maintain:test`.

## Non-Goals

- Scheduled/automated CI checks (on-demand only)
- Auto-generating SDK code from the OAS spec (audit identifies what needs changing; implementation is manual/assisted)
- Mock/sandbox testing (real API only)

## Architecture

### Component Overview

```
specs/
  baseline.json              # Last-known-good OAS spec (committed)
  latest.json                # Freshly fetched spec (gitignored)
  diff-report.md             # Output from diff_spec.py (gitignored)
  audit-report.md            # Output from audit_sdk.py (gitignored)

scripts/
  fetch_spec.py              # Downloads latest OAS spec from Etsy
  diff_spec.py               # Diffs baseline vs latest, outputs structured report
  audit_sdk.py               # Maps OAS spec to SDK code, finds coverage gaps

tests/
  conftest.py                # Shared fixtures: EtsyClient, credentials, markers
  test_listing.py            # Listing CRUD
  test_listing_image.py      # Image upload/delete
  test_listing_file.py       # Digital file upload/delete
  test_listing_inventory.py  # Inventory management
  test_shop.py               # Shop read/update
  test_shipping_profile.py   # Shipping CRUD
  test_receipt.py            # Receipt/order operations
  test_user.py               # User endpoints
  test_taxonomy.py           # Taxonomy reads
  test_misc.py               # Ping, token scopes

.claude/skills/maintain/
  check.md                   # /maintain:check skill
  audit.md                   # /maintain:audit skill
  test.md                    # /maintain:test skill
```

### Script Details

#### `scripts/fetch_spec.py`

- Fetches `https://www.etsy.com/openapi/generated/oas/3.0.0.json`
- Saves to `specs/latest.json`
- Prints whether changes were detected vs baseline
- Exit code: 0 if spec differs from baseline, 1 if identical

#### `scripts/diff_spec.py`

Reads `specs/baseline.json` and `specs/latest.json`. Produces a structured markdown report with sections:

- **New Endpoints** — paths in latest not in baseline
- **Removed Endpoints** — paths in baseline not in latest
- **Changed Endpoints** — parameter additions/removals/type changes, request body changes
- **Schema Changes** — new/modified/removed response schemas and properties
- **Enum Changes** — new/changed/removed enum values
- **Deprecations** — anything newly marked deprecated

Output goes to stdout and `specs/diff-report.md`.

#### `scripts/audit_sdk.py`

Cross-references the OAS spec against SDK code. Auto-infers mappings using naming conventions:

- OAS `operationId` (e.g., `getListingsByShop`) -> snake_case (`get_listings_by_shop`) -> scan resource files for method match
- OAS tags (e.g., `ShopListing`) -> match to resource file names
- OAS request body schemas -> match to model class names by convention

Reports:

- **Missing endpoints** — OAS operations with no SDK method
- **Extra endpoints** — SDK methods with no OAS match (possibly removed)
- **Parameter drift** — mismatches between OAS params and SDK method signatures/model fields
- **Enum staleness** — OAS enum values not reflected in SDK enum classes
- **Unmapped operations** — anything that couldn't be auto-matched (needs manual review)

Output goes to stdout and `specs/audit-report.md`.

### Integration Tests

#### Credentials

Loaded from environment variables (or `.env` file, gitignored):

- `ETSY_API_KEY`
- `ETSY_ACCESS_TOKEN`
- `ETSY_REFRESH_TOKEN`
- `ETSY_SHOP_ID`
- `ETSY_TOKEN_EXPIRY`

#### Test Pattern

Write operations follow a create-read-update-delete lifecycle:

1. Create a resource (draft listing, shipping profile, etc.)
2. Read it back, assert fields match
3. Update it, verify changes
4. Delete/cleanup

Read-only endpoints (taxonomy, reviews, user info) call and validate response shape.

#### Markers

- `@pytest.mark.readonly` — safe to run anytime
- `@pytest.mark.write` — creates/modifies data on test shop
- Run subsets: `pytest tests/ -m readonly`

#### Response Validation

Tests check response fields exist and have expected types, catching schema drift early (not just HTTP 200).

### Claude Code Skills

#### `/maintain:check` (`.claude/skills/maintain/check.md`)

1. Runs `scripts/fetch_spec.py`
2. Runs `scripts/diff_spec.py`
3. Presents the diff report conversationally
4. Highlights breaking changes and action items

#### `/maintain:audit` (`.claude/skills/maintain/audit.md`)

1. Runs `scripts/audit_sdk.py`
2. Presents coverage gaps mapped to specific SDK files
3. Offers to implement changes for each gap

#### `/maintain:test` (`.claude/skills/maintain/test.md`)

1. Runs `pytest tests/` (all or filtered by resource/marker)
2. Reports results
3. Helps debug failures

### Workflow

Typical maintenance session:

```
/maintain:check          # "Are there new Etsy API changes?"
  -> Review diff report
  -> Decide what to act on

/maintain:audit          # "How does my SDK compare to the spec?"
  -> Review gap report
  -> Implement changes (manually or with Claude Code)

/maintain:test           # "Does everything work?"
  -> Run integration tests
  -> Fix failures

# When done:
cp specs/latest.json specs/baseline.json
git add . && git commit -m "feat: sync SDK with Etsy OAS spec YYYY-MM-DD"
```

## Baseline Spec Management

- `specs/baseline.json` is committed to the repo. It represents "the OAS spec version my SDK currently matches."
- `specs/latest.json` is gitignored. It's ephemeral — fetched fresh each time.
- After applying SDK changes, copy latest to baseline and commit. This marks "I'm in sync up to this point."

## Dependencies

New dev dependencies for tests:

- `pytest`
- `python-dotenv` (for loading `.env` credentials)

