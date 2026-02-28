# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Development Setup
```bash
python -m venv venv
venv\Scripts\activate                      # Windows
source venv/bin/activate                   # Unix/Mac
pip install -e .
pip install -r etsy_python/requirements.txt
```

### Building
```bash
python setup.py build
python setup.py sdist bdist_wheel
```

### Version Management
```bash
python scripts/check_version_consistency.py              # Validate versions match
python scripts/bump_version.py --dry-run --type patch    # Preview bump
python scripts/bump_version.py --type [patch|minor|major] # Execute bump
python scripts/release.py patch --no-push                # Local release test
```

### Testing
No formal test framework. Verify changes with:
```bash
python scripts/check_version_consistency.py
python -c "from etsy_python._version import __version__; print(__version__)"
```

## Version Management

**Single source of truth**: `etsy_python/_version.py`

`setup.py` reads version dynamically from `_version.py`. The `.bumpversion.cfg` file tracks version for the bump tool but can drift out of sync -- always trust `_version.py`.

A pre-commit hook (`.pre-commit-config.yaml`) runs `scripts/check_version_consistency.py` to validate `_version.py` and `.bumpversion.cfg` agree.

### Semantic Commit Messages

Commit messages trigger automatic version bumps on push to master:
- `breaking:` or `BREAKING CHANGE` -> Major
- `feat:` or contains `feature` -> Minor
- All other commits -> Patch

Skip CI with `[skip ci]`, `[ci skip]`, or `[no ci]` in commit message. Version bump commits automatically include `[skip ci]` to prevent infinite loops.

## Architecture

### Layer Overview

```
Resources (API endpoints) -> Models (request validation) -> EtsyClient (HTTP + auth) -> Etsy API
```

All code lives under `etsy_python/v3/`:

| Directory | Purpose |
|-----------|---------|
| `auth/` | OAuth 2.0 PKCE flow (`EtsyOAuth`) |
| `common/` | Utilities (`Utils.py`), environment config (`Env.py`), HTTP constants (`Request.py`) |
| `enums/` | Type-safe API parameter constants |
| `exceptions/` | `BaseAPIException` -> `RequestException` (with rate limits) |
| `models/` | Request data models with validation (`Request` base, `FileRequest` for uploads) |
| `resources/` | ~25 API endpoint classes + `Session.py` (EtsyClient) + `Response.py` |

### Key Components

**EtsyClient** (`resources/Session.py`): Central HTTP client. Manages OAuth tokens with auto-refresh, session headers, rate limit parsing. All resources receive it via constructor injection.

**Request base class** (`models/Request.py`): Provides `nullable`/`mandatory` field lists. `check_mandatory()` validates required fields, `get_dict()` serializes to API format excluding empty nullable fields.

**FileRequest** (`models/FileRequest.py`): Extends Request with `file` (multipart) and `data` attributes for upload endpoints.

### Request Flow

1. Resource method called with parameters
2. Request model validates mandatory fields via `super().__init__()`
3. `EtsyClient.make_request()` checks token expiry (UTC-aware), refreshes if needed
4. HTTP request sent; response parsed into `Response` or raises `RequestException`
5. Rate limits extracted from response headers when present

### Resource Pattern

Every resource is a `@dataclass` with `session: EtsyClient`. Methods return `Union[Response, RequestException]`.

- **GET/DELETE**: Parameters passed as `**kwargs`, built into query string via `generate_get_uri()`
- **POST/PUT/PATCH**: Payload is a `Request` model, serialized via `.get_dict()` to JSON
- **File uploads**: Payload is a `FileRequest`, sent as multipart form data
- **Enums**: Always use `.value` to extract the API string (e.g., `State.ACTIVE.value` -> `"active"`)

### Utility Functions (`common/Utils.py`)

- `generate_get_uri(uri, **kwargs)` -- builds query string from kwargs dict
- `todict(obj)` -- recursive serializer handling Enums, nested objects, nullable fields
- `generate_bytes_from_file(file)` -- reads file bytes for uploads

### Environment (`common/Env.py`)

Controlled by `ETSY_ENV` env var (default: `"PROD"`). Sets base URLs for OAuth (`etsy.com`) and API (`openapi.etsy.com`).

## Coding Conventions

- **Classes**: PascalCase. **Methods**: snake_case. **Constants/Enum values**: UPPER_SNAKE_CASE
- Always use type hints for parameters and return values
- Resource methods return `Union[Response, RequestException]` -- no try/catch in resource layer
- Imports: stdlib -> third-party -> internal (absolute imports: `from etsy_python.v3...`)
- All datetime comparisons use UTC timezone via `datetime.now(tz=timezone.utc)`

## Adding a New API Endpoint

1. **Model** in `models/`: Create a class extending `Request` with `nullable` and `mandatory` lists
2. **Enums** in `enums/`: Add any new type-safe constants
3. **Resource method** in `resources/`: Add method to existing or new `@dataclass` resource class
4. **Exports**: Update `resources/__init__.py` if adding a new resource class

## Dependencies

- `requests==2.32.4` -- HTTP client
- `requests-oauthlib>=1.3.1` -- OAuth 2.0

## CI/CD

GitHub Actions (`.github/workflows/python-publish.yml`) on push to master:
1. Check for skip-ci markers
2. Bump version based on commit message semantics
3. Build sdist + wheel
4. Publish to PyPI (trusted publishing)
5. Create GitHub Release

Also supports manual workflow dispatch with version type selection.

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/bump_version.py` | Semantic version bumping (supports `--dry-run`, `--type auto`) |
| `scripts/check_version_consistency.py` | Validates `_version.py` matches `.bumpversion.cfg` |
| `scripts/release.py` | Manual release orchestration (`--no-push`, `--no-build`, `--no-tag`, `--force`) |
| `scripts/generate_release_notes.py` | Generates changelog from git commits (used by CI) |
