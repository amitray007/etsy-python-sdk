<p align="center">
    <h1 align="center">Etsy API Client Library for Python</h1>
</p>
<p align="center">
	<img src="https://img.shields.io/github/license/amitray007/etsy-python-sdk?style=default&color=0080ff" alt="license">
	<img src="https://img.shields.io/github/last-commit/amitray007/etsy-python-sdk?style=default&color=0080ff" alt="last-commit">
	<img src="https://img.shields.io/github/languages/top/amitray007/etsy-python-sdk?style=default&color=0080ff" alt="repo-top-language">
<p>
<p align="center">
    <img src="https://www.etsy.com/images/apps/documentation/edc_badge3.gif" alt="etsy-api-badge">
</p>
<p align="center">
	<!-- default option, no dependency badges. -->
</p>
<hr>

##  Quick Links

> - [ Overview](#-overview)
> - [ Features](#-features)
> - [ Repository Structure](#-repository-structure)
> - [ Modules](#-modules)
> - [ Getting Started](#-getting-started)
>     - [ Installation](#-installation)
> - [ Contributing](#-contributing)
> - [ License](#-license)

---

##  Overview

The etsy-python-sdk is a project that provides a Python wrapper for the Etsy API, allowing developers to easily interact with the Etsy platform. With features such as OAuth authentication, users can authenticate and access the API to perform actions like retrieving listings, managing inventory, and creating shipping profiles. This project simplifies the process of integrating Etsy functionality into Python applications, enabling developers to build applications that interact with the Etsy marketplace seamlessly.

---

##  Features

|    |   Feature         | Description |
|----|-------------------|---------------------------------------------------------------|
| ⚙️  | **Architecture**  | The project's architecture is not explicitly mentioned in the repository. More information would be required to provide a detailed analysis. |
| 🔩 | **Code Quality**  | The code quality and style are not explicitly mentioned in the repository. No linting or code analysis tools are mentioned. |
| 📄 | **Documentation** | The extent and quality of documentation are not explicitly mentioned in the repository. No specific documentation files or guidelines are provided. |
| 🔌 | **Integrations**  | The project has dependencies on the following libraries: requests, requests-oauthlib. These libraries are used for making HTTP requests and OAuth authentication. |
| 🧩 | **Modularity**    | The modularity and reusability of the codebase cannot be determined based on the repository's contents and information available. |
| ⚡️  | **Performance**   | The efficiency, speed, and resource usage of the project cannot be evaluated based on the repository's contents and information available. |
| 🛡️ | **Security**      | The measures used for data protection and access control are not explicitly mentioned in the repository. Further information would be required for a detailed assessment. |
| 📦 | **Dependencies**  | The key external libraries and dependencies include requests and requests-oauthlib. These are required for making HTTP requests and implementing OAuth authentication. |
| 🚀 | **Scalability**   | The ability of the project to handle increased traffic and load cannot be determined based on the repository's contents and information available. |


---

##  Repository Structure

```sh
└── etsy-python-sdk/
    └── etsy_python
        ├── requirements.txt
        └── v3
            ├── auth
            ├── common
            ├── enums
            ├── exceptions
            ├── models
            └── resources
```

---

##  Modules

<details closed><summary>etsy_python</summary>

| File                                                                                                       | Summary                                                                                                                                                                                                                                              |
| ---                                                                                                        | ---                                                                                                                                                                                                                                                  |
| [requirements.txt](https://github.com/amitray007/etsy-python-sdk/blob/master/etsy_python/requirements.txt) | This code snippet, located in the `requirements.txt` file, specifies the dependencies required for the Etsy Python SDK. It includes the `requests` library and `requests-oauthlib`, which are critical for making API requests to the Etsy platform. |

</details>

<details closed><summary>etsy_python.v3.enums</summary>

| File                                                                                                                      | Summary                                                                                                                                                                                                                                                                                                      |
| ---                                                                                                                       | ---                                                                                                                                                                                                                                                                                                          |
| [ListingInventory.py](https://github.com/amitray007/etsy-python-sdk/blob/master/etsy_python/v3/enums/ListingInventory.py) | The `ListingInventory.py` file in the `enums` directory of the `etsy-python-sdk` repository defines the `Includes` enum, which represents the different options for including listing information in the inventory.                                                                                          |
| [Language.py](https://github.com/amitray007/etsy-python-sdk/blob/master/etsy_python/v3/enums/Language.py)                 | The Language.py file in the enums directory of the etsy-python-sdk repository defines an Enum class representing different languages. It provides a set of predefined language options as constants.                                                                                                         |
| [ShippingProfile.py](https://github.com/amitray007/etsy-python-sdk/blob/master/etsy_python/v3/enums/ShippingProfile.py)   | This code snippet, located at etsy_python/v3/enums/ShippingProfile.py, defines various enums related to shipping profiles in the parent repository. These enums include processing time units, destination regions, shipping types, and providers.                                                           |
| [ShopReceipt.py](https://github.com/amitray007/etsy-python-sdk/blob/master/etsy_python/v3/enums/ShopReceipt.py)           | The code snippet in the ShopReceipt.py file defines two enums, SortOn and SortOrder, which are used for sorting shop receipts in ascending or descending order based on different criteria. This code snippet is part of the Etsy Python SDK repository and resides in the enums directory of the v3 module. |
| [Listing.py](https://github.com/amitray007/etsy-python-sdk/blob/master/etsy_python/v3/enums/Listing.py)                   | The code snippet in `Listing.py` defines several enums used in the parent `etsy-python-sdk` repository, such as `WhoMade`, `WhenMade`, `ItemWeightUnit`, and others. These enums provide standardized values for various attributes of a listing in the Etsy marketplace.                                    |

</details>

<details closed><summary>etsy_python.v3.resources</summary>

| File                                                                                                                                      | Summary                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| ---                                                                                                                                       | ---                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| [Response.py](https://github.com/amitray007/etsy-python-sdk/blob/master/etsy_python/v3/resources/Response.py)                             | The code snippet in `Response.py` defines a `Response` class that represents a response from the Etsy API. It includes the response code, message, and optional rate limits. The `__str__` method provides a string representation of the response.                                                                                                                                                                                                                |
| [UserAddress.py](https://github.com/amitray007/etsy-python-sdk/blob/master/etsy_python/v3/resources/UserAddress.py)                       | This code snippet is part of the etsy-python-sdk repository and is located at etsy_python/v3/resources/UserAddress.py. It provides methods for interacting with user addresses, including deleting an address, getting a specific address, and retrieving a list of addresses. The code relies on the EtsyClient session and makes use of the make_request method.                                                                                                 |
| [Session.py](https://github.com/amitray007/etsy-python-sdk/blob/master/etsy_python/v3/resources/Session.py)                               | The `Session.py` code snippet in the `v3/resources` directory of the `etsy-python-sdk` repository implements a `EtsyClient` class that handles authentication, token management, and making HTTP requests to the Etsy API. It provides methods for updating tokens, making requests, and processing responses.                                                                                                                                                     |
| [ShopSection.py](https://github.com/amitray007/etsy-python-sdk/blob/master/etsy_python/v3/resources/ShopSection.py)                       | The `ShopSectionResource` code snippet is a module within the `etsy-python-sdk` repository. It provides functions to create, retrieve, update, and delete shop sections in the Etsy API. It utilizes the `EtsyClient` session to make requests and handles possible exceptions.                                                                                                                                                                                    |
| [PaymentLedgerEntry.py](https://github.com/amitray007/etsy-python-sdk/blob/master/etsy_python/v3/resources/PaymentLedgerEntry.py)         | This code snippet, located at `etsy_python/v3/resources/PaymentLedgerEntry.py`, is responsible for handling payment ledger entries in the Etsy Python SDK repository. It provides methods to retrieve specific ledger entries for a shop and to retrieve a list of ledger entries for a shop within a specific time range. The code interacts with the `EtsyClient` session and returns either a successful `Response` or a `RequestException` if an error occurs. |
| [User.py](https://github.com/amitray007/etsy-python-sdk/blob/master/etsy_python/v3/resources/User.py)                                     | The UserResource class in User.py is responsible for retrieving user information from the Etsy API. It utilizes the EtsyClient session to make the API requests and returns a response or an exception.                                                                                                                                                                                                                                                            |
| [ReceiptTransactions.py](https://github.com/amitray007/etsy-python-sdk/blob/master/etsy_python/v3/resources/ReceiptTransactions.py)       | The code in ReceiptTransactions.py is responsible for retrieving information about shop receipt transactions from the Etsy API. It provides methods to get transactions related to a listing, a specific receipt, a specific transaction, and all transactions for a shop. The code interacts with the API using the EtsyClient session and handles the request and response handling through the make_request method.                                             |
| [ListingOffering.py](https://github.com/amitray007/etsy-python-sdk/blob/master/etsy_python/v3/resources/ListingOffering.py)               | This code snippet is part of the Etsy Python SDK repository and is located in the ListingOffering.py file. It defines a ListingOfferingResource class that interacts with the Etsy API to retrieve a specific listing offering. It utilizes session and response objects to make the API request.                                                                                                                                                                  |
| [ShopProductionPartner.py](https://github.com/amitray007/etsy-python-sdk/blob/master/etsy_python/v3/resources/ShopProductionPartner.py)   | The code snippet in ShopProductionPartner.py is a resource class that interacts with the production partners of a shop in the Etsy Python SDK. It provides a method to retrieve the production partners of a shop using the Etsy API.                                                                                                                                                                                                                              |
| [ListingInventory.py](https://github.com/amitray007/etsy-python-sdk/blob/master/etsy_python/v3/resources/ListingInventory.py)             | The `ListingInventory.py` code snippet in the `etsy-python-sdk` repository is responsible for managing listings' inventory. It provides functions to retrieve and update listing inventory using the Etsy API. It utilizes dataclasses, typing, and other resources from the parent repository.                                                                                                                                                                    |
| [ListingImage.py](https://github.com/amitray007/etsy-python-sdk/blob/master/etsy_python/v3/resources/ListingImage.py)                     | This code snippet defines a ListingImageResource class in the Etsy Python SDK. It provides methods for interacting with listing images in the Etsy API, such as deleting, getting, and uploading images. The class encapsulates the necessary logic for making requests to the API using the provided EtsyClient session.                                                                                                                                          |
| [Shop.py](https://github.com/amitray007/etsy-python-sdk/blob/master/etsy_python/v3/resources/Shop.py)                                     | This code snippet in Shop.py defines a ShopResource class that provides methods for interacting with the Etsy API to get, update, find shops, and get shops by owner user ID. It relies on the EtsyClient session to make API requests with appropriate endpoints and parameters.                                                                                                                                                                                  |
| [Receipt.py](https://github.com/amitray007/etsy-python-sdk/blob/master/etsy_python/v3/resources/Receipt.py)                               | The ReceiptResource code snippet in the Etsy Python SDK repository provides methods for interacting with shop receipts. It allows users to retrieve, update, and create shipments for receipts. This code plays a critical role in managing the receipt-related functionality of the application.                                                                                                                                                                  |
| [ShopReturnPolicy.py](https://github.com/amitray007/etsy-python-sdk/blob/master/etsy_python/v3/resources/ShopReturnPolicy.py)             | This code snippet represents the ShopReturnPolicy resource in the Etsy Python SDK. It provides methods for creating, updating, retrieving, and deleting shop return policies. It communicates with the Etsy API using the EtsyClient session.                                                                                                                                                                                                                      |
| [Taxonomy.py](https://github.com/amitray007/etsy-python-sdk/blob/master/etsy_python/v3/resources/Taxonomy.py)                             | This code snippet contains two classes, BuyerTaxonomy and SellerTaxonomy, which are responsible for making API requests related to buyer and seller taxonomies, respectively. These classes utilize the EtsyClient session object to interact with the API endpoints and retrieve taxonomic data.                                                                                                                                                                  |
| [ListingVariationImages.py](https://github.com/amitray007/etsy-python-sdk/blob/master/etsy_python/v3/resources/ListingVariationImages.py) | This code snippet, located at etsy_python/v3/resources/ListingVariationImages.py, is responsible for handling listing variation images in the Etsy Python SDK. It provides functions to get and update variation images for a listing. The code interacts with the Etsy API through a session and uses dataclasses and typing for proper type annotations.                                                                                                         |
| [ShippingProfile.py](https://github.com/amitray007/etsy-python-sdk/blob/master/etsy_python/v3/resources/ShippingProfile.py)               | The `ShippingProfileResource` class in the `ShippingProfile.py` file is responsible for interacting with the shipping profile endpoints of the Etsy API. It provides methods for creating, updating, deleting, and retrieving shipping profiles and their destinations and upgrades. The class uses the `EtsyClient` session to make requests to the API.                                                                                                          |
| [ListingVideo.py](https://github.com/amitray007/etsy-python-sdk/blob/master/etsy_python/v3/resources/ListingVideo.py)                     | This code snippet provides a ListingVideoResource class that interacts with the Etsy API. It allows for deleting, getting, and uploading videos associated with listings. It uses the EtsyClient session for making API requests.                                                                                                                                                                                                                                  |
| [ListingProduct.py](https://github.com/amitray007/etsy-python-sdk/blob/master/etsy_python/v3/resources/ListingProduct.py)                 | This code snippet is a resource file in the etsy-python-sdk repository's v3 package. It provides a method to retrieve a specific product for a listing by making a request to the Etsy API. The code uses dataclasses and types to handle the response and any potential exceptions.                                                                                                                                                                               |
| [ListingTranslation.py](https://github.com/amitray007/etsy-python-sdk/blob/master/etsy_python/v3/resources/ListingTranslation.py)         | This code snippet in ListingTranslation.py provides functions to create, retrieve, and update listing translations in the Etsy Python SDK. It communicates with the Etsy API using the `EtsyClient` session and handles requests and responses, encapsulating the logic for listing translation operations.                                                                                                                                                        |
| [ListingFile.py](https://github.com/amitray007/etsy-python-sdk/blob/master/etsy_python/v3/resources/ListingFile.py)                       | This code snippet in ListingFile.py is part of the etsy-python-sdk repository. It provides functions to interact with listing files in the Etsy API, including deleting, getting, getting all, and uploading listing files. The code relies on the EtsyClient class and various other modules within the repository.                                                                                                                                               |
| [Payment.py](https://github.com/amitray007/etsy-python-sdk/blob/master/etsy_python/v3/resources/Payment.py)                               | The `PaymentResource` class in `Payment.py` is responsible for handling payments-related operations in the Etsy Python SDK. It provides methods to retrieve shop payment account ledger entries, shop payments by receipt ID, and individual payments by ID. These methods make requests to the Etsy API using the provided session.                                                                                                                               |
| [Review.py](https://github.com/amitray007/etsy-python-sdk/blob/master/etsy_python/v3/resources/Review.py)                                 | The `ReviewResource` class in the `Review.py` file is part of the `etsy-python-sdk` repository. It provides methods to retrieve reviews either by listing or by shop. The class takes a session object as a parameter and uses it to make API requests.                                                                                                                                                                                                            |
| [Listing.py](https://github.com/amitray007/etsy-python-sdk/blob/master/etsy_python/v3/resources/Listing.py)                               | The code snippet in `Listing.py` is responsible for managing and interacting with the Listing resource in the Etsy API. It provides functions to create, retrieve, update, and delete listings, as well as perform various operations related to listings, such as getting listings by shop, by IDs, by shop section, and by return policy. The code demonstrates proper resource structuring and implements error handling for making requests to the Etsy API.   |
| [Miscellaneous.py](https://github.com/amitray007/etsy-python-sdk/blob/master/etsy_python/v3/resources/Miscellaneous.py)                   | This code snippet in `Miscellaneous.py` defines a `MiscellaneousResource` class that represents a resource for making various API requests. It includes methods for pinging the server and getting token scopes. The class uses a session object to make the requests.                                                                                                                                                                                             |

</details>

<details closed><summary>etsy_python.v3.resources.enums</summary>

| File                                                                                                                  | Summary                                                                                                                                                                                                                                                                                                                                |
| ---                                                                                                                   | ---                                                                                                                                                                                                                                                                                                                                    |
| [Request.py](https://github.com/amitray007/etsy-python-sdk/blob/master/etsy_python/v3/resources/enums/Request.py)     | The code snippet in `Request.py` defines an enumeration of HTTP methods (`GET`, `POST`, `PUT`, etc.) used for making API requests. It is part of the `etsy-python-sdk` repository and is located in the `enums` module within the `v3` package of the codebase.                                                                        |
| [RateLimit.py](https://github.com/amitray007/etsy-python-sdk/blob/master/etsy_python/v3/resources/enums/RateLimit.py) | The code snippet in the file RateLimit.py defines a data class called RateLimit that represents rate limit information. It includes attributes such as limit per second, remaining requests this second, limit per day, and remaining requests today. This class is part of the enums module in the larger etsy-python-sdk repository. |

</details>

<details closed><summary>etsy_python.v3.common</summary>

| File                                                                                                     | Summary                                                                                                                                                                                                                                                                                                                         |
| ---                                                                                                      | ---                                                                                                                                                                                                                                                                                                                             |
| [Request.py](https://github.com/amitray007/etsy-python-sdk/blob/master/etsy_python/v3/common/Request.py) | The code snippet in the file `Request.py` defines a set of error codes and default response messages used in the common module of the `etsy-python-sdk` repository. It provides a standardized way of handling HTTP responses.                                                                                                  |
| [Utils.py](https://github.com/amitray007/etsy-python-sdk/blob/master/etsy_python/v3/common/Utils.py)     | This code snippet in `etsy_python/v3/common/Utils.py` provides utility functions for the Etsy Python SDK. It includes functions to generate a URI with query parameters, convert objects to dictionaries, and read bytes from a file. These functions are critical for various operations within the repository's architecture. |
| [Env.py](https://github.com/amitray007/etsy-python-sdk/blob/master/etsy_python/v3/common/Env.py)         | This code snippet defines the environment configuration for the Etsy Python SDK. It sets the authorization and request URLs based on the environment (production in this case).                                                                                                                                                 |

</details>

<details closed><summary>etsy_python.v3.auth</summary>

| File                                                                                               | Summary                                                                                                                                                                                                                                                                                              |
| ---                                                                                                | ---                                                                                                                                                                                                                                                                                                  |
| [OAuth.py](https://github.com/amitray007/etsy-python-sdk/blob/master/etsy_python/v3/auth/OAuth.py) | The code snippet in the file OAuth.py in the auth directory of the etsy-python-sdk repository handles OAuth authentication for the Etsy API. It allows users to obtain an authorization code, set the code, and retrieve an access token. The code also generates a challenge for the code verifier. |

</details>

<details closed><summary>etsy_python.v3.exceptions</summary>

| File                                                                                                                           | Summary                                                                                                                                                                                                                                                                                                                                         |
| ---                                                                                                                            | ---                                                                                                                                                                                                                                                                                                                                             |
| [BaseAPIException.py](https://github.com/amitray007/etsy-python-sdk/blob/master/etsy_python/v3/exceptions/BaseAPIException.py) | The code snippet in BaseAPIException.py defines a base class for API exceptions in the etsy-python-sdk repository. It includes properties for code, message, and type, and overrides the __str__ method to display the exception details.                                                                                                       |
| [RequestException.py](https://github.com/amitray007/etsy-python-sdk/blob/master/etsy_python/v3/exceptions/RequestException.py) | This code snippet in the file RequestException.py is a data class that represents a RequestException in the Etsy Python SDK repository. It inherits from the BaseAPIException class and includes a rate_limits attribute. The __str__() method overrides the parent class method to provide a formatted string representation of the exception. |

</details>

<details closed><summary>etsy_python.v3.models</summary>

| File                                                                                                                       | Summary                                                                                                                                                                                                                                                                                                                                                                                                                          |
| ---                                                                                                                        | ---                                                                                                                                                                                                                                                                                                                                                                                                                              |
| [Request.py](https://github.com/amitray007/etsy-python-sdk/blob/master/etsy_python/v3/models/Request.py)                   | The Request.py code snippet in the etsy-python-sdk repository defines a class that represents a request object. It has methods to check for mandatory fields, get nullable fields, and convert the object to a dictionary.                                                                                                                                                                                                       |
| [Shop.py](https://github.com/amitray007/etsy-python-sdk/blob/master/etsy_python/v3/models/Shop.py)                         | The code snippet in the Shop.py file defines request models for creating and updating shop sections, and for updating shop details. The models specify the mandatory and nullable fields required for each request. These models are used in the Etsy Python SDK repository to handle requests related to shop management.                                                                                                       |
| [Product.py](https://github.com/amitray007/etsy-python-sdk/blob/master/etsy_python/v3/models/Product.py)                   | This code snippet defines the `Product` data model in the `etsy-python-sdk` repository. It includes properties like `sku`, `property_values`, and `offerings`. These models are used for handling product-related data in the Etsy API integration.                                                                                                                                                                              |
| [Receipt.py](https://github.com/amitray007/etsy-python-sdk/blob/master/etsy_python/v3/models/Receipt.py)                   | This code snippet contains the implementation of two request models, namely `CreateReceiptShipmentRequest` and `UpdateShopReceiptRequest`, which are used in the Etsy Python SDK repository. These models define the attributes and behavior required for creating and updating receipts in the Etsy platform.                                                                                                                   |
| [ShopReturnPolicy.py](https://github.com/amitray007/etsy-python-sdk/blob/master/etsy_python/v3/models/ShopReturnPolicy.py) | Summary:The code in ShopReturnPolicy.py defines three request classes: ConsolidateShopReturnPoliciesRequest, CreateShopReturnPolicyRequest, and UpdateShopReturnPolicyRequest. These classes inherit from the Request class and contain attributes related to shop return policies, such as acceptance of returns and exchanges.                                                                                                 |
| [ShippingProfile.py](https://github.com/amitray007/etsy-python-sdk/blob/master/etsy_python/v3/models/ShippingProfile.py)   | The code snippet in `ShippingProfile.py` defines classes for creating and updating shipping profiles in the Etsy Python SDK. These classes handle requests related to shipping profiles, including destination information and profile upgrades. They ensure the required and optional parameters are included in the requests.                                                                                                  |
| [FileRequest.py](https://github.com/amitray007/etsy-python-sdk/blob/master/etsy_python/v3/models/FileRequest.py)           | The `FileRequest` class in the `FileRequest.py` file is a subclass of the `Request` class. It handles file-related requests by accepting optional lists of nullable and mandatory fields. The class initializes the `file` and `data` attributes and calls the parent class constructor. This code snippet contributes to the model layer of the etsy-python-sdk repository, providing functionality for handling file requests. |
| [Utils.py](https://github.com/amitray007/etsy-python-sdk/blob/master/etsy_python/v3/models/Utils.py)                       | This code snippet defines data classes for offerings, property values, and variation images. These classes are utilized in the `etsy-python-sdk` repository's architecture for managing and manipulating data related to offerings, properties, and variation images in the Etsy e-commerce platform.                                                                                                                            |
| [Listing.py](https://github.com/amitray007/etsy-python-sdk/blob/master/etsy_python/v3/models/Listing.py)                   | This code snippet defines various request models for creating, updating, and managing listings in the Etsy Python SDK. It includes models for creating draft listings, updating listing properties, uploading images and files, and managing variations and translations for listings.                                                                                                                                           |
| [Miscellaneous.py](https://github.com/amitray007/etsy-python-sdk/blob/master/etsy_python/v3/models/Miscellaneous.py)       | The code snippet in the file Miscellaneous.py defines a class called GetTokenScopes. It inherits from the Request class and is used to retrieve the scopes of a token. The class has a token parameter and handles the nullable and mandatory fields required for the request.                                                                                                                                                   |

</details>

---

##  Getting Started

***Requirements***

Ensure you have the following dependencies installed on your system:

* **Python**: `version 3.8+`

###  Installation

1. Clone the etsy-python-sdk repository:

```sh
git clone https://github.com/amitray007/etsy-python-sdk
```

2. Change to the project directory:

```sh
cd etsy-python-sdk
```

3. Install the dependencies:

```sh
pip install -r requirements.txt
```

##  Contributing

Contributions are welcome! Here are several ways you can contribute:

- **[Report Issues](https://github/amitray007/etsy-python-sdk/issues)**: Submit bugs found or log feature requests for Etsy-python-sdk.

<details closed>
    <summary>Contributing Guidelines</summary>

1. **Fork the Repository**: Start by forking the project repository to your GitHub account.
2. **Clone Locally**: Clone the forked repository to your local machine using a Git client.
   ```sh
   git clone https://github.com/amitray007/etsy-python-sdk
   ```
3. **Create a New Branch**: Always work on a new branch, giving it a descriptive name.
   ```sh
   git checkout -b new-feature-x
   ```
4. **Make Your Changes**: Develop and test your changes locally.
5. **Commit Your Changes**: Commit with a clear message describing your updates.
   ```sh
   git commit -m 'Implemented new feature x.'
   ```
6. **Push to GitHub**: Push the changes to your forked repository.
   ```sh
   git push origin new-feature-x
   ```
7. **Submit a Pull Request**: Create a PR against the original project repository. Clearly describe the changes and their motivations.

Once your PR is reviewed and approved, it will be merged into the main branch.

</details>

---

##  License

This project is protected under the [MIT License](https://github.com/amitray007/etsy-python-sdk/blob/master/LICENSE) License.
