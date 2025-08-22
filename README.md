<p align="center">
    <h1 align="center">Etsy API Client Library for Python</h1>
</p>

<p align="center">
    <img src="https://img.shields.io/pypi/v/etsy-python?style=for-the-badge&color=0080ff&style=default" alt="PyPI version">
	<img src="https://img.shields.io/github/license/amitray007/etsy-python-sdk?style=default&color=0080ff" alt="license">
	<img src="https://img.shields.io/github/last-commit/amitray007/etsy-python-sdk?style=default&color=0080ff" alt="last-commit">
	<img src="https://img.shields.io/github/languages/top/amitray007/etsy-python-sdk?style=default&color=0080ff" alt="repo-top-language">
<p>

<p align="center">
    <img src="https://www.etsy.com/images/apps/documentation/edc_badge3.gif" alt="etsy-api-badge">
</p>

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
  - [Install from PyPI](#install-from-pypi)
  - [Install from Source](#install-from-source)
  - [Dependencies](#dependencies)
- [Quick Start](#quick-start)
  - [1. Authentication Setup](#1-authentication-setup)
  - [2. Initialize Client Session](#2-initialize-client-session)
  - [3. Make API Calls](#3-make-api-calls)
- [Usage Examples](#usage-examples)
  - [Managing Listings](#managing-listings)
  - [Working with Receipts](#working-with-receipts)
  - [Uploading Images](#uploading-images)
  - [Handling Shipping Profiles](#handling-shipping-profiles)
  - [Token Management with Callback](#token-management-with-callback)
- [API Resources](#api-resources)
  - [Core Resources](#core-resources)
  - [Media Resources](#media-resources)
  - [Commerce Resources](#commerce-resources)
  - [Shop Management](#shop-management)
- [Error Handling](#error-handling)
- [Environment Configuration](#environment-configuration)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
  - [Development Setup](#development-setup)
- [Support](#support)
- [License](#license)
- [Changelog](#changelog)

---

## Overview

A comprehensive Python client library for the Etsy API v3, providing a modern, type-safe interface for interacting with the Etsy marketplace. This SDK simplifies OAuth 2.0 authentication, automatic token refresh, and provides complete coverage of Etsy's API endpoints.

## Features

✨ **Complete API Coverage** - Full support for Etsy API v3 endpoints including:

- Listings management (create, update, delete, search)
- Shop operations (sections, policies, production partners)
- Receipt and transaction handling
- Shipping profiles and destinations
- Product taxonomy and attributes
- File, image, and video uploads
- Reviews and payment processing

🔐 **Robust Authentication** - OAuth 2.0 with PKCE support:

- Secure authorization code flow
- Automatic token refresh before expiry
- Custom token synchronization callbacks
- Session management with timezone-aware expiry handling

🏗️ **Developer-Friendly Architecture**:

- Type-safe request/response models using dataclasses
- Comprehensive enum definitions for API parameters
- Consistent error handling with detailed exceptions
- Rate limiting information in responses
- Clean separation of concerns with resource-based structure

⚡ **Production Ready**:

- Built-in retry logic for failed requests
- Configurable environments (production/staging)
- Extensive error handling and validation
- Support for file uploads and multipart requests

## Requirements

- Python 3.8 or higher
- An Etsy App API Key (get one at [Etsy Developers](https://www.etsy.com/developers))

## Installation

### Install from PyPI

```bash
pip install etsy-python
```

### Install from Source

```bash
git clone https://github.com/amitray007/etsy-python-sdk.git
cd etsy-python-sdk
pip install -e .
```

### Dependencies

The SDK requires:

- `requests>=2.32.2` - HTTP client library
- `requests-oauthlib>=1.3.1` - OAuth 2.0 support

## Quick Start

### 1. Authentication Setup

```python
from etsy_python.v3.auth.OAuth import EtsyOAuth

# Initialize OAuth client
oauth = EtsyOAuth(
    keystring="your_api_key",
    redirect_uri="http://localhost:8000/callback",
    scopes=["listings_r", "listings_w", "shops_r", "shops_w"]
)

# Get authorization URL
auth_url, state = oauth.get_auth_code()
print(f"Visit this URL to authorize: {auth_url}")

# After user authorizes, set the authorization code
oauth.set_authorisation_code(code="auth_code_from_callback", state=state)

# Get access token
token_data = oauth.get_access_token()
```

### 2. Initialize Client Session

```python
from datetime import datetime
from etsy_python.v3.resources.Session import EtsyClient

# Create client with tokens
client = EtsyClient(
    keystring="your_api_key",
    access_token=token_data["access_token"],
    refresh_token=token_data["refresh_token"],
    expiry=datetime.utcnow() + timedelta(seconds=token_data["expires_in"])
)
```

### 3. Make API Calls

```python
from etsy_python.v3.resources.Listing import ListingResource
from etsy_python.v3.enums.Listing import State, SortOn, SortOrder

# Initialize resource
listing_resource = ListingResource(session=client)

# Get active listings for a shop
response = listing_resource.get_listings_by_shop(
    shop_id=12345,
    state=State.ACTIVE,
    limit=25,
    sort_on=SortOn.CREATED,
    sort_order=SortOrder.DESC
)

print(f"Found {len(response.message['results'])} listings")
```

## Usage Examples

### Managing Listings

```python
from etsy_python.v3.models.Listing import CreateDraftListingRequest
from etsy_python.v3.enums.Listing import WhoMade, WhenMade

# Create a draft listing
draft_listing = CreateDraftListingRequest(
    title="Handmade Ceramic Mug",
    description="Beautiful handcrafted ceramic mug",
    price=25.00,
    quantity=10,
    who_made=WhoMade.I_DID,
    when_made=WhenMade.MADE_TO_ORDER,
    taxonomy_id=1234,
    tags=["ceramic", "mug", "handmade"]
)

response = listing_resource.create_draft_listing(
    shop_id=12345,
    listing=draft_listing
)
```

### Working with Receipts

```python
from etsy_python.v3.resources.Receipt import ReceiptResource
from etsy_python.v3.models.Receipt import CreateReceiptShipmentRequest

receipt_resource = ReceiptResource(session=client)

# Get shop receipts
receipts = receipt_resource.get_shop_receipts(
    shop_id=12345,
    limit=50
)

# Create shipment for a receipt
shipment_request = CreateReceiptShipmentRequest(
    tracking_number="1Z999AA10123456784",
    carrier_name="USPS",
    notification_sent=True
)

receipt_resource.create_receipt_shipment(
    shop_id=12345,
    receipt_id=67890,
    shipment=shipment_request
)
```

### Uploading Images

```python
from etsy_python.v3.resources.ListingImage import ListingImageResource
from etsy_python.v3.models.Listing import UploadListingImageRequest

image_resource = ListingImageResource(session=client)

# Upload image to listing
with open("product_photo.jpg", "rb") as image_file:
    upload_request = UploadListingImageRequest(
        image=image_file,
        alt_text="Front view of ceramic mug"
    )

    response = image_resource.upload_listing_image(
        shop_id=12345,
        listing_id=67890,
        image=upload_request
    )
```

### Handling Shipping Profiles

```python
from etsy_python.v3.resources.ShippingProfile import ShippingProfileResource
from etsy_python.v3.models.ShippingProfile import CreateShopShippingProfileRequest
from etsy_python.v3.enums.ShippingProfile import ProcessingTimeUnit

shipping_resource = ShippingProfileResource(session=client)

# Create shipping profile
profile_request = CreateShopShippingProfileRequest(
    title="Standard Shipping",
    processing_time_value=3,
    processing_time_unit=ProcessingTimeUnit.BUSINESS_DAYS,
    origin_country_iso="US",
    primary_cost=5.00,
    secondary_cost=2.00
)

response = shipping_resource.create_shop_shipping_profile(
    shop_id=12345,
    profile=profile_request
)
```

### Token Management with Callback

```python
def save_tokens_to_database(access_token, refresh_token, expiry):
    """Custom function to persist tokens"""
    # Your database logic here
    pass

# Initialize client with token sync callback
client = EtsyClient(
    keystring="your_api_key",
    access_token=access_token,
    refresh_token=refresh_token,
    expiry=expiry,
    sync_refresh=save_tokens_to_database
)

# Tokens will be automatically refreshed and saved when expired
```

## API Resources

The SDK provides comprehensive coverage of Etsy API v3 resources:

### Core Resources

- **Listing** - Create, read, update, delete listings
- **Shop** - Manage shop information and settings
- **Receipt** - Handle orders and transactions
- **User** - User profiles and addresses
- **ShippingProfile** - Configure shipping options

### Media Resources

- **ListingImage** - Upload and manage listing images
- **ListingVideo** - Upload and manage listing videos
- **ListingFile** - Digital file management

### Commerce Resources

- **ListingInventory** - Stock and SKU management
- **Payment** - Payment processing and ledger entries
- **Review** - Customer reviews management

### Shop Management

- **ShopSection** - Organize listings into sections
- **ShopReturnPolicy** - Define return policies
- **ShopProductionPartner** - Manage production partners

## Error Handling

The SDK provides detailed error information through custom exceptions:

```python
from etsy_python.v3.exceptions.RequestException import RequestException

try:
    response = listing_resource.get_listing(listing_id=12345)
except RequestException as e:
    print(f"Error Code: {e.code}")
    print(f"Error Message: {e.error}")
    print(f"Error Description: {e.type}")

    # Rate limit information (if available)
    if e.rate_limits:
        print(f"Daily Limit: {e.rate_limits.limit_per_day}")
        print(f"Remaining Today: {e.rate_limits.remaining_today}")
```

## Environment Configuration

Configure the SDK environment using environment variables:

```bash
# Set environment (defaults to PROD)
export ETSY_ENV=PROD
```

## Project Structure

```
etsy-python-sdk/
├── etsy_python/
│   └── v3/
│       ├── auth/          # OAuth authentication
│       ├── common/        # Shared utilities
│       ├── enums/         # API enum definitions
│       ├── exceptions/    # Custom exceptions
│       ├── models/        # Request/response models
│       └── resources/     # API endpoint implementations
├── setup.py               # Package configuration
├── LICENSE                # MIT License
└── README.md              # Documentation
```

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Automatic Versioning

This project uses automatic semantic versioning based on commit messages:

- **Commits with `breaking:` or `BREAKING CHANGE`** → Major version bump (1.0.0 → 2.0.0)
- **Commits with `feat:` or containing `feature`** → Minor version bump (1.0.0 → 1.1.0)
- **All other commits** → Patch version bump (1.0.0 → 1.0.1)

The version is automatically bumped when changes are pushed to the `master` branch, and the package is automatically published to PyPI.

#### Skipping CI/CD

To skip the automatic versioning and publishing workflow, include one of these phrases in your commit message:
- `[skip ci]`
- `[ci skip]`
- `skip ci`
- `[no ci]`

Example:
```bash
git commit -m "docs: update README [skip ci]"
```

#### Manual Release (for maintainers)

For local testing or manual releases:

```bash
# Install development dependencies
pip install -e .

# Create a patch release
python scripts/release.py patch

# Create a minor release
python scripts/release.py minor

# Create a major release
python scripts/release.py major

# Dry run (local only, no push)
python scripts/release.py patch --no-push
```

### Development Setup

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/yourusername/etsy-python-sdk.git
   cd etsy-python-sdk
   ```
3. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. Install dependencies:
   ```bash
   pip install -r etsy_python/requirements.txt
   ```
5. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```
6. Make your changes and commit:
   ```bash
   git commit -m "Add your feature"
   ```
7. Push and create a pull request

## Support

- **Documentation**: [GitHub Wiki](https://github.com/amitray007/etsy-python-sdk/wiki)
- **Issues**: [GitHub Issues](https://github.com/amitray007/etsy-python-sdk/issues)
- **Etsy API Docs**: [developers.etsy.com](https://developers.etsy.com/documentation)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

See [Releases](https://github.com/amitray007/etsy-python-sdk/releases) for full changelog.

---

<p align="center">Made with ❤️ for the Etsy developer community</p>

