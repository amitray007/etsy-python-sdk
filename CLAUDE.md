# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Building and Installation
```bash
python setup.py build                      # Build the package
python setup.py sdist                      # Create source distribution  
python setup.py bdist_wheel                # Create wheel distribution
pip install -e .                           # Install in development mode
pip install -r etsy_python/requirements.txt # Install dependencies
```

### Version Management
```bash
# Check version consistency across files
python scripts/check_version_consistency.py

# Manual version bump (dry run)
python scripts/bump_version.py --dry-run --type patch

# Manual version bump
python scripts/bump_version.py --type [patch|minor|major]

# Create a manual release (for testing)
python scripts/release.py patch --no-push
```

### Package Publishing (for maintainers)
```bash
python setup.py sdist bdist_wheel          # Build distributions
twine upload dist/*                        # Upload to PyPI (manual)
# Note: Publishing is automated via GitHub Actions on push to master
```

### Development Environment
```bash
python -m venv venv                        # Create virtual environment
venv\Scripts\activate                      # Activate on Windows
source venv/bin/activate                   # Activate on Unix/Mac
pip install -r etsy_python/requirements.txt # Install dependencies
```

Note: No formal testing framework configured. The `etsy_python/v3/tests/` directory exists but is empty.

## Automatic Versioning & CI/CD

### Version Management System

The project uses **centralized version management** with automatic semantic versioning:

1. **Single Source of Truth**: `etsy_python/_version.py`
2. **Dynamic Version Reading**: `setup.py` reads version from `_version.py`
3. **Version Consistency**: `.bumpversion.cfg` tracks current version
4. **Automatic Bumping**: GitHub Actions bumps version on push to master

### Semantic Versioning Rules

Commit messages trigger automatic version bumps:
- `breaking:` or `BREAKING CHANGE` → Major (1.0.0 → 2.0.0)
- `feat:` or contains `feature` → Minor (1.0.0 → 1.1.0)
- All other commits → Patch (1.0.0 → 1.0.1)

### Skipping CI/CD

Include these phrases in commit messages to skip workflows:
- `[skip ci]`
- `[ci skip]`
- `skip ci`
- `[no ci]`

**Important**: Version bump commits automatically include `[skip ci]` to prevent infinite loops.

### GitHub Actions Workflow

File: `.github/workflows/python-publish.yml`

**Workflow Jobs:**
1. **check-skip**: Checks if CI should be skipped
2. **version-bump**: Bumps version and creates git tag
3. **build**: Builds distribution packages
4. **publish-to-pypi**: Publishes to PyPI
5. **create-release**: Creates GitHub Release

**Triggers:**
- Push to `master` branch (automatic)
- Manual workflow dispatch with version type selection

### Version-Related Files

```
etsy_python/_version.py      # Version source of truth
setup.py                      # Reads version dynamically
.bumpversion.cfg             # Bump version configuration
scripts/
├── bump_version.py          # Version bumping logic
├── check_version_consistency.py  # Version validation
└── release.py               # Manual release tool
```

## Architecture Deep Dive

### Core Design Principles

1. **Resource-Based Architecture**: Each Etsy API endpoint group is encapsulated in a Resource class
2. **Type Safety**: Extensive use of Python's typing module and Enums for compile-time safety
3. **Dataclass Pattern**: All resources use `@dataclass` decorator for clean initialization
4. **Inheritance Model**: Request models inherit from base `Request` class with validation
5. **Separation of Concerns**: Clear separation between models, resources, enums, and exceptions

### Directory Structure & Purpose

```
etsy_python/v3/
├── auth/          # OAuth 2.0 PKCE implementation
├── common/        # Shared utilities and environment config
├── enums/         # Type-safe API parameter constants
├── exceptions/    # Custom exception hierarchy
├── models/        # Request/response data models
├── resources/     # API endpoint implementations
└── tests/         # Empty test directory
```

### Authentication Architecture

**OAuth 2.0 Flow with PKCE**:
```python
EtsyOAuth (auth/OAuth.py)
├── Generates code_verifier and code_challenge
├── Creates authorization URL with state
├── Validates state on callback
└── Exchanges code for tokens
```

**Session Management**:
```python
EtsyClient (resources/Session.py)
├── Stores tokens with expiry tracking
├── Auto-refreshes tokens before expiry (timezone-aware)
├── Maintains persistent session headers
├── Parses rate limits from response headers
└── Supports sync_refresh callback for token persistence
```

### Request/Response Flow

1. **Resource Method Called** → 
2. **Request Model Validated** (mandatory fields checked) →
3. **Model Serialized** (todict with nullable handling) →
4. **EtsyClient.make_request()** →
5. **Token Refresh Check** (if expired) →
6. **HTTP Request Sent** →
7. **Response Processed** →
8. **Returns Response or RequestException**

### Model Architecture

**Base Request Model** (`models/Request.py`):
```python
class Request:
    nullable: List[str]   # Fields that can be None/empty
    mandatory: List[str]  # Required fields
    
    - check_mandatory()   # Validates required fields exist
    - get_nulled()       # Identifies empty nullable fields
    - get_dict()         # Serializes to dict, removing nulled fields
```

**Model Pattern**:
```python
class CreateDraftListingRequest(Request):
    nullable = ["shipping_profile_id", "tags", ...]  # Optional fields
    mandatory = ["title", "price", "quantity", ...]  # Required fields
    
    def __init__(self, ...):
        # Set all attributes
        super().__init__(nullable=self.nullable, mandatory=self.mandatory)
```

**FileRequest Model** (for uploads):
- Extends Request with `file` and `data` attributes
- Used for multipart/form-data uploads

### Resource Pattern

**Standard Resource Structure**:
```python
@dataclass
class ResourceName:
    session: EtsyClient  # Injected session dependency
    
    def method_name(self, required_params, optional_params=None) -> Union[Response, RequestException]:
        endpoint = f"/path/{param}"
        
        # For GET requests with query params
        kwargs = {"param": value, ...}
        return self.session.make_request(endpoint, **kwargs)
        
        # For POST/PUT with payload
        return self.session.make_request(endpoint, method=Method.POST, payload=model)
```

### Enum Design

**Purpose**: Type-safe API parameters preventing invalid values

**Pattern**:
```python
class EnumName(Enum):
    OPTION_ONE = "api_value_1"  # Human-readable name → API value
    OPTION_TWO = "api_value_2"
```

**Usage in Resources**:
```python
def get_listings(self, state: State = State.ACTIVE):
    kwargs = {"state": state.value}  # .value extracts API string
```

### Exception Hierarchy

```
BaseAPIException (base class)
├── code: int                    # HTTP status code
├── error: Optional[str]         # Error message
├── error_description: Optional[str]  # Detailed description
└── type: str = "ERROR"          # Error classification

RequestException (extends BaseAPIException)
└── rate_limits: Optional[RateLimit]  # Rate limit info if available
```

### Utility Functions

**`common/Utils.py`**:
- `generate_get_uri()`: Builds query string from kwargs dict
- `todict()`: Recursive serializer handling Enums, nested objects, nullable fields
- `generate_bytes_from_file()`: File reading for uploads

**`common/Env.py`**:
- Environment configuration (PROD/DEV)
- Base URLs for OAuth and API endpoints
- Configurable via `ETSY_ENV` environment variable

## Coding Style Guidelines

### Naming Conventions
- **Classes**: PascalCase (e.g., `ListingResource`, `CreateDraftListingRequest`)
- **Methods**: snake_case (e.g., `get_listings_by_shop`, `create_draft_listing`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `ERROR_CODES`, `NO_RESPONSE_CODES`)
- **Enums**: PascalCase class, UPPER_SNAKE_CASE values
- **Private attributes**: Leading underscore (e.g., `_nullable`, `_mandatory`)

### Type Annotations
- **Always use type hints** for parameters and return values
- **Use Union** for methods that can return Response or Exception
- **Use Optional** for nullable parameters
- **Import types** from typing module

### Method Signatures
```python
def method_name(
    self,
    required_param: int,
    optional_param: Optional[str] = None,
    list_param: Optional[List[str]] = None,
) -> Union[Response, RequestException]:
```

### Error Handling
- Methods return `Union[Response, RequestException]` - no try/catch in resources
- Validation happens in Request model constructors
- EtsyClient handles all HTTP errors and converts to RequestException

### Import Organization
```python
from datetime import datetime  # Standard library
from typing import Optional, List  # Type imports

from requests import Session  # Third-party

from etsy_python.v3.common.Request import ERROR_CODES  # Internal absolute imports
from etsy_python.v3.models.Request import Request
```

### Commit Message Conventions

Follow semantic commit format for automatic versioning:
```
type: description

[optional body]
[optional footer]
```

Types:
- `fix:` - Bug fixes (patch bump)
- `feat:` - New features (minor bump)
- `breaking:` - Breaking changes (major bump)
- `docs:` - Documentation only
- `chore:` - Maintenance tasks
- `test:` - Test changes
- `refactor:` - Code refactoring
- `style:` - Code style changes
- `perf:` - Performance improvements

## API Design Patterns

### 1. Builder Pattern for Complex Requests
Models with many optional parameters use nullable/mandatory lists for validation rather than builder classes.

### 2. Resource Injection Pattern
All resources receive `EtsyClient` session via constructor injection:
```python
listing_resource = ListingResource(session=client)
```

### 3. Enum Value Pattern
Enums store API values, not display names:
```python
WhoMade.I_DID.value == "i_did"  # API expects "i_did"
```

### 4. Pagination Pattern
Standard pagination parameters across all list methods:
```python
limit: Optional[int] = 25
offset: Optional[int] = 0
```

### 5. Includes Pattern for Nested Resources
```python
includes: Optional[List[Includes]] = None
# Converted to comma-separated string: "Images,Shop,User"
```

### 6. Kwargs Pattern for Query Parameters
GET request parameters passed as kwargs dict:
```python
kwargs = {"state": state.value, "limit": limit}
return self.session.make_request(endpoint, **kwargs)
```

### 7. Timezone-Aware Token Expiry
All datetime comparisons use UTC timezone:
```python
datetime.now(tz=timezone.utc) >= self.ensure_utc(self.expiry)
```

## Common Development Tasks

### Adding a New API Endpoint

1. **Create/Update Model** in `models/`:
   ```python
   class NewFeatureRequest(Request):
       nullable = ["optional_field"]
       mandatory = ["required_field"]
   ```

2. **Add Enums** if needed in `enums/`:
   ```python
   class NewFeatureType(Enum):
       TYPE_A = "type_a"
   ```

3. **Add Resource Method**:
   ```python
   def new_feature(self, param: int, request: NewFeatureRequest):
       endpoint = f"/endpoint/{param}"
       return self.session.make_request(endpoint, method=Method.POST, payload=request)
   ```

### Handling File Uploads

Use `FileRequest` model with multipart data:
```python
class UploadFileRequest(FileRequest):
    def __init__(self, file, metadata):
        self.file = {"file": (filename, file_bytes, content_type)}
        self.data = {"metadata": metadata}
        super().__init__()
```

### Rate Limit Handling

Check response for rate limits:
```python
try:
    response = resource.method()
    if response.rate_limits:
        print(f"Remaining today: {response.rate_limits.remaining_today}")
except RequestException as e:
    if e.rate_limits:
        # Handle rate limiting
```

### Making Version-Safe Changes

1. **Documentation changes**: Use `[skip ci]` in commit
2. **Bug fixes**: Use `fix:` prefix (patch bump)
3. **New features**: Use `feat:` prefix (minor bump)
4. **Breaking changes**: Use `breaking:` prefix (major bump)

Example workflow:
```bash
# Make changes
git add .
git commit -m "feat: add new listing filters"
git push origin master
# GitHub Actions will automatically:
# - Bump version to next minor (e.g., 1.0.19 → 1.1.0)
# - Publish to PyPI
# - Create GitHub release
```

## Environment Variables

- `ETSY_ENV`: Set to "PROD" (default) or custom environment
- Affects base URLs for OAuth and API endpoints

## Dependencies

Core dependencies (pinned versions):
- `requests==2.32.2` - HTTP client with session support
- `requests-oauthlib>=1.3.1` - OAuth 2.0 implementation

## Windows-Specific Notes

This codebase is developed on Windows (B:\ drive paths). Use appropriate path separators when working with file operations. Unicode characters in console output may need special handling (use ASCII alternatives).

## CI/CD Pipeline

The project uses GitHub Actions for continuous integration and deployment:

1. **Trigger**: Push to master or manual workflow dispatch
2. **Skip Check**: Checks for `[skip ci]` in commit message
3. **Version Bump**: Automatically increments version based on commit type
4. **Build**: Creates distribution packages
5. **Publish**: Uploads to PyPI using trusted publishing
6. **Release**: Creates GitHub release with changelog

All version management is automated - developers only need to use proper commit message conventions.