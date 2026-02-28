# Etsy SDK Maintenance Workflow Design

**Date**: 2026-02-28
**Status**: Approved
**Author**: Amit Ray + Claude Code

## Problem

As a solo maintainer, keeping the Etsy Python SDK in sync with Etsy's evolving OpenAPI spec is entirely manual. The current workflow involves reading release notes, manually comparing documentation, and hoping nothing breaks. There are no tests to catch drift, no automated diffing, and no structured way to identify what SDK code needs updating.

## Goals

1. **Detect API changes** — On-demand tooling to fetch the latest Etsy OAS spec and produce a structured diff report against a known baseline.
2. **Audit SDK coverage** — Cross-reference the OAS spec against SDK resource/model/enum code to identify gaps, stale parameters, and missing endpoints — then verify findings against actual code and prepare actionable changes.
3. **Test against live API** — Full CRUD integration test suite hitting a real Etsy test shop to validate the SDK works against the current API.
4. **Claude Code integration** — Skills that orchestrate these tools conversationally via `/maintain-check` and `/maintain-audit`.

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
  last-release-check.json    # Tracks last checked GitHub release (committed)
  release-notes.md           # Output from check_releases.py (gitignored)

scripts/
  fetch_spec.py              # Downloads latest OAS spec from Etsy
  diff_spec.py               # Diffs baseline vs latest, outputs structured report
  audit_sdk.py               # Maps OAS spec to SDK code, finds coverage gaps
  check_releases.py          # Fetches GitHub releases, compares against stored state

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

.claude/skills/
  maintain-check/SKILL.md          # /maintain-check skill
  maintain-audit/SKILL.md          # /maintain-audit skill (4-phase pipeline: audit + verify + change list + implement)
  maintain-release-check/SKILL.md  # /maintain-release-check skill (GitHub release notes check)
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

#### `scripts/check_releases.py`

Fetches releases from `https://api.github.com/repos/etsy/open-api/releases` and compares against the last checked release stored in `specs/last-release-check.json`.

Two modes:
- **Default**: Check for new releases, save markdown report to `specs/release-notes.md`
- **`--update [TAG]`**: Mark a release as checked (latest by default, or specific tag)

Exit codes: 0 = new releases found, 1 = up to date, 2 = error.

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

#### `/maintain-check` (`.claude/skills/maintain-check/SKILL.md`)

1. Runs `scripts/fetch_spec.py`
2. Runs `scripts/diff_spec.py`
3. Presents the diff report conversationally
4. Highlights breaking changes and action items

#### `/maintain-release-check` (`.claude/skills/maintain-release-check/SKILL.md`)

1. Runs `scripts/check_releases.py`
2. If new releases found, reads `specs/release-notes.md` and presents an impact summary
3. Maps each change to likely affected SDK files (resources, models, enums)
4. Asks user: batch review (prepare change list) or interactive investigation (one-by-one)
5. After review, suggests `--update` to mark releases as checked and `/maintain-audit` for full spec audit

#### `/maintain-audit` (`.claude/skills/maintain-audit/SKILL.md`)

The audit skill is a 4-phase pipeline that handles everything from detection through to implementation:

**Phase 1 — Run audit script:**
1. Runs `scripts/audit_sdk.py`
2. Verifies `specs/audit-report.md` was generated successfully
3. Reads the audit report into context

**Phase 2 — Verify & review findings:**
Claude Code reads the audit report alongside the actual SDK code and OAS spec to catch what the script's pattern matching missed:
- Loads OAS spec from `specs/latest.json` (fallback: `specs/baseline.json`) and `specs/diff-report.md` if available
- Spot-checks "mapped" operations — focuses on those with diff-report changes, complex request bodies, or many parameters; reads actual resource files + model classes and compares against spec
- Verifies "unmapped" operations — searches SDK resource files manually for naming mismatches the script missed
- Verifies "extra" SDK methods — checks if they map to deprecated/removed/renamed endpoints
- Deep-checks model `mandatory`/`nullable` lists against spec `required` arrays, with `file:line` references

**Phase 3 — Prepare change list:**
Consolidates all findings (script-detected + review-detected) into a categorized change list:
- **Must Fix** — Breaking/correctness issues (mandatory fields changed, removed params still in SDK, type mismatches)
- **Should Fix** — Completeness issues (new optional params, new enum values, missing endpoints)
- **Informational** — Deprecation notices, response schema changes, naming inconsistencies

Each item includes: category, description, specific `file:line` reference, and concrete action.

**Phase 4 — User decision:**
Uses AskUserQuestion to ask the user:
- **"Start implementing"** — Proceeds to implement all Must Fix and Should Fix items
- **"Need changes to the audit tasks"** — Walks through items one at a time (or in groups), lets the user approve/reject/modify each, then implements only approved items

After implementation, suggests running integration tests (if available locally) and updating the baseline spec.

### Workflow

Typical maintenance session:

```
/maintain-release-check  # "Are there new Etsy releases?"
  -> Review release notes for breaking changes, deprecations
  -> Batch review or investigate one-by-one
  -> Update release check state

/maintain-check          # "Are there new Etsy API changes?"
  -> Review diff report
  -> Decide what to act on

/maintain-audit          # Full 4-phase pipeline (also reads release-notes.md if present):
  -> Phase 1: Run audit script
  -> Phase 2: Claude Code verifies against actual code + spec
  -> Phase 3: Prepare categorized change list
  -> Phase 4: Ask user → implement or adjust items first
  -> Implement approved changes

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
