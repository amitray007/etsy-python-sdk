import warnings

import pytest

from etsy_python.v3.enums.Listing import WhenMade, WhoMade
from etsy_python.v3.models.Listing import (
    CreateDraftListingRequest,
    CreateListingTranslationRequest,
    UpdateListingRequest,
    UpdateListingInventoryRequest,
    UpdateListingPropertyRequest,
    UpdateVariationImagesRequest,
    UploadListingImageRequest,
    UploadListingFileRequest,
)
from etsy_python.v3.models.Product import Product


class TestCreateDraftListingRequest:
    def test_valid_request(self):
        req = CreateDraftListingRequest(
            quantity=10,
            title="Test Mug",
            description="A test mug",
            price=25.00,
            who_made=WhoMade.I_DID,
            when_made=WhenMade.TWENTY_TWENTIES,
            taxonomy_id=30303,
        )
        assert req.quantity == 10
        assert req.title == "Test Mug"

    def test_missing_mandatory_raises(self):
        with pytest.raises(ValueError):
            CreateDraftListingRequest(
                quantity=10,
                title="Test Mug",
                description=None,  # mandatory
                price=25.00,
                who_made=WhoMade.I_DID,
                when_made=WhenMade.TWENTY_TWENTIES,
                taxonomy_id=30303,
            )

    def test_nullable_fields_in_get_dict(self):
        req = CreateDraftListingRequest(
            quantity=10,
            title="Test Mug",
            description="A test mug",
            price=25.00,
            who_made=WhoMade.I_DID,
            when_made=WhenMade.TWENTY_TWENTIES,
            taxonomy_id=30303,
            shipping_profile_id=0,  # nullable field with zero -> becomes null
        )
        result = req.get_dict()
        assert result["shipping_profile_id"] is None

    def test_enum_serialization(self):
        req = CreateDraftListingRequest(
            quantity=10,
            title="Test Mug",
            description="A test mug",
            price=25.00,
            who_made=WhoMade.I_DID,
            when_made=WhenMade.TWENTY_TWENTIES,
            taxonomy_id=30303,
        )
        result = req.get_dict()
        assert result["who_made"] == "i_did"
        assert result["when_made"] == "2020_2026"


class TestUpdateListingRequest:
    def test_no_mandatory_fields(self):
        req = UpdateListingRequest(title="Updated Title")
        assert req.title == "Updated Title"

    def test_empty_request(self):
        req = UpdateListingRequest()
        result = req.get_dict()
        # All None fields should be excluded
        assert "title" not in result

    def test_partial_update(self):
        req = UpdateListingRequest(title="New Title", is_taxable=True)
        result = req.get_dict()
        assert result["title"] == "New Title"
        assert result["is_taxable"] is True

    def test_type_nullable_uses_underscore_prefix(self):
        """_type field in nullable list must use attribute name '_type', not API key 'type'."""
        assert "_type" in UpdateListingRequest.nullable
        assert "type" not in UpdateListingRequest.nullable


class TestUpdateListingInventoryRequest:
    def test_valid_request(self):
        product = Product(
            sku="SKU-001",
            property_values=[],
            offerings=[{"quantity": 10, "price": 25.00}],
        )
        req = UpdateListingInventoryRequest(products=[product])
        assert len(req.products) == 1

    def test_missing_products_raises(self):
        with pytest.raises(ValueError):
            UpdateListingInventoryRequest(products=None)


class TestUpdateListingPropertyRequest:
    def test_valid_request(self):
        req = UpdateListingPropertyRequest(
            value_ids=[1, 2], values=["Red", "Blue"]
        )
        assert req.value_ids == [1, 2]

    def test_missing_mandatory_raises(self):
        with pytest.raises(ValueError):
            UpdateListingPropertyRequest(value_ids=None, values=["Red"])


class TestCreateListingTranslationRequest:
    def test_valid_request(self):
        req = CreateListingTranslationRequest(
            title="Titre", description="Description en francais"
        )
        assert req.title == "Titre"

    def test_missing_mandatory_raises(self):
        with pytest.raises(ValueError):
            CreateListingTranslationRequest(title=None, description="Description")


class TestUpdateVariationImagesRequest:
    def test_valid_request(self):
        req = UpdateVariationImagesRequest(
            variation_images=[{"property_id": 1, "value_id": 1, "image_id": 100}]
        )
        result = req.get_dict()
        assert len(result["variation_images"]) == 1

    def test_missing_variation_images_raises(self):
        with pytest.raises(ValueError):
            UpdateVariationImagesRequest(variation_images=None)


class TestUploadListingImageRequest:
    def test_sets_file_and_data(self):
        req = UploadListingImageRequest(image_bytes=b"fake-png-data", rank=2)
        assert req.file is not None
        assert req.data is not None
        assert req.data["rank"] == 2

    def test_default_rank(self):
        req = UploadListingImageRequest(image_bytes=b"fake-png-data")
        assert req.data["rank"] == 1


class TestUploadListingFileRequest:
    def test_sets_file_and_data(self):
        req = UploadListingFileRequest(file_bytes=b"fake-pdf-data", name="test.pdf")
        assert req.file is not None
        assert req.data is not None


class TestPersonalizationDeprecationWarnings:
    def _make_create_kwargs(self):
        return dict(
            quantity=10,
            title="Test",
            description="A test",
            price=25.00,
            who_made=WhoMade.I_DID,
            when_made=WhenMade.TWENTY_TWENTIES,
            taxonomy_id=30303,
        )

    def test_create_no_warning_without_personalization(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            CreateDraftListingRequest(**self._make_create_kwargs())
            deprecation_warnings = [x for x in w if issubclass(x.category, DeprecationWarning)]
            assert len(deprecation_warnings) == 0

    def test_create_warns_with_personalization_is_required(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            CreateDraftListingRequest(
                **self._make_create_kwargs(),
                personalization_is_required=True,
            )
            deprecation_warnings = [x for x in w if issubclass(x.category, DeprecationWarning)]
            assert len(deprecation_warnings) == 1
            assert "deprecated by the Etsy API" in str(deprecation_warnings[0].message)
            assert "personalization-migration" in str(deprecation_warnings[0].message)

    def test_update_no_warning_without_personalization(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            UpdateListingRequest(title="Updated")
            deprecation_warnings = [x for x in w if issubclass(x.category, DeprecationWarning)]
            assert len(deprecation_warnings) == 0

    def test_update_warns_with_personalization_instructions(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            UpdateListingRequest(personalization_instructions="Enter name")
            deprecation_warnings = [x for x in w if issubclass(x.category, DeprecationWarning)]
            assert len(deprecation_warnings) == 1
            assert "update_listing_personalization" in str(deprecation_warnings[0].message)

    def test_create_warns_with_is_personalizable(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            CreateDraftListingRequest(
                **self._make_create_kwargs(),
                is_personalizable=True,
            )
            deprecation_warnings = [x for x in w if issubclass(x.category, DeprecationWarning)]
            assert len(deprecation_warnings) == 1
            assert "is_personalizable" in str(deprecation_warnings[0].message)
            assert "personalization-migration" in str(deprecation_warnings[0].message)

    def test_update_warns_with_is_personalizable(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            UpdateListingRequest(is_personalizable=True)
            deprecation_warnings = [x for x in w if issubclass(x.category, DeprecationWarning)]
            assert len(deprecation_warnings) == 1
            assert "is_personalizable" in str(deprecation_warnings[0].message)

    def test_create_no_warning_with_is_personalizable_false(self):
        # False matches the API's documented default and is a no-op once
        # the field is removed, so explicit opt-out should not warn.
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            CreateDraftListingRequest(
                **self._make_create_kwargs(),
                is_personalizable=False,
                personalization_is_required=False,
            )
            deprecation_warnings = [x for x in w if issubclass(x.category, DeprecationWarning)]
            assert len(deprecation_warnings) == 0

    def test_update_no_warning_with_falsy_personalization_values(self):
        # 0 char count and empty instructions are equivalent to "not used".
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            UpdateListingRequest(
                is_personalizable=False,
                personalization_char_count_max=0,
                personalization_instructions="",
            )
            deprecation_warnings = [x for x in w if issubclass(x.category, DeprecationWarning)]
            assert len(deprecation_warnings) == 0

    def test_create_warns_once_with_multiple_personalization_fields(self):
        # Setting several deprecated fields together must produce exactly one
        # DeprecationWarning, not one per field.
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            CreateDraftListingRequest(
                **self._make_create_kwargs(),
                is_personalizable=True,
                personalization_is_required=True,
                personalization_char_count_max=256,
                personalization_instructions="Enter name",
            )
            deprecation_warnings = [x for x in w if issubclass(x.category, DeprecationWarning)]
            assert len(deprecation_warnings) == 1
            assert "is_personalizable" in str(deprecation_warnings[0].message)
