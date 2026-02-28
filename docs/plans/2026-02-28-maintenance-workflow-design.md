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
4. **Claude Code integration** — Skills that orchestrate these tools conversationally via `/maintain-check`, `/maintain-release-check`, and `/maintain-audit`.

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
  conftest.py                       # Shared fixtures, markers
  fixtures/                         # Mock data for unit tests
  test_session.py                   # EtsyClient session + auth
  test_request_model.py             # Request base class validation
  test_utils.py                     # Utility functions (todict, generate_get_uri)
  test_listing_resource.py          # Listing resource methods
  test_listing_models.py            # Listing request models
  test_listing_image_resource.py    # Listing image upload resource
  test_shop_resource.py             # Shop resource methods
  test_shop_models.py               # Shop request models
  test_receipt_resource.py          # Receipt resource methods
  test_receipt_models.py            # Receipt request models
  test_shipping_profile_resource.py # Shipping profile resource methods
  test_shipping_profile_models.py   # Shipping profile request models
  test_payment_resource.py          # Payment resource methods
  test_user_resource.py             # User resource methods
  test_remaining_resources.py       # Other resource methods

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

Report sections:

- **Coverage Summary** — overall mapped/unmapped/missing counts
- **Missing Endpoints** — OAS operations with no SDK method
- **Not Implemented Stubs** — SDK methods that exist but raise NotImplementedError
- **Extra SDK Methods** — SDK methods with no OAS match (possibly removed)
- **Missing Exports** — resource classes not exported from `__init__.py`
- **Query/Path Parameter Drift** — mismatches between OAS params and SDK method signatures
- **Request Body Drift** — mismatches between OAS request bodies and SDK model fields
- **Enum Staleness** — OAS enum values not reflected in SDK enum classes
- **Deprecation Notices** — operations marked deprecated in spec
- **Code Issues** — static analysis findings (e.g., implicit string concatenation)

Output goes to stdout and `specs/audit-report.md`.

#### `scripts/check_releases.py`

Fetches releases from `https://api.github.com/repos/etsy/open-api/releases` and compares against the last checked release stored in `specs/last-release-check.json`.

Two modes:
- **Default**: Check for new releases, save markdown report to `specs/release-notes.md`
- **`--update [TAG]`**: Mark a release as checked (latest by default, or specific tag)

Exit codes: 0 = new releases found, 1 = up to date, 2 = error.

### Unit Tests

Unit tests mock the HTTP layer and validate SDK behavior without hitting the Etsy API.

#### Test Structure

- **Resource tests** (`test_*_resource.py`) — verify resource methods build correct URLs, pass correct parameters, and handle responses
- **Model tests** (`test_*_models.py`) — verify `mandatory`/`nullable` field validation, `get_dict()` serialization
- **Session test** (`test_session.py`) — verify EtsyClient token refresh, header management, rate limit parsing
- **Utility tests** (`test_utils.py`) — verify `todict()`, `generate_get_uri()`, `generate_bytes_from_file()`

#### Running

```bash
pytest                                               # All tests
pytest -v                                            # Verbose
pytest --cov=etsy_python --cov-report=term-missing   # Coverage
pytest tests/test_session.py                         # Specific file
```

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

The audit skill is a 4-phase pipeline that gathers fresh data, audits, reviews, and implements:

**Phase 1 — Gather fresh data & run audit:**
1. Fetches latest OAS spec (`scripts/fetch_spec.py`)
2. Checks for new Etsy GitHub release notes (`scripts/check_releases.py`)
3. Diffs spec against baseline (`scripts/diff_spec.py`)
4. Runs `scripts/audit_sdk.py` against the latest spec
5. Reads all generated reports (audit, diff, release notes) into context

**Phase 2 — AI-driven code review:**
Claude Code reads the audit report alongside the actual SDK code, OAS spec, and release notes to catch what the script's pattern matching missed:
- Prioritizes operations mentioned in release notes or diff report
- Deep-reads flagged resource files + model classes and compares against spec
- Checks serialization correctness, type mismatches, URL/method correctness
- Verifies "unmapped" and "extra" operations
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

After implementation, suggests running tests (`pytest`), updating the baseline spec, and marking release notes as checked.

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

Dev dependencies (in `requirements-dev.txt`):

- `pytest>=7.0.0`
- `pytest-cov>=4.0.0`
