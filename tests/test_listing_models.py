import warnings

import pytest

from etsy_python.v3.enums.Listing import WhenMade, WhoMade
from etsy_python.v3.models.Listing import (
    CreateDraftListingRequest,
    CreateListingTranslationRequest,
    UpdateListingRequest,
    UpdateListingInventoryRequest,
    UpdateListingPersonalizationRequest,
    UpdateListingPropertyRequest,
    UpdateListingTranslationRequest,
    UpdateListingVideoRequest,
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
            assert "no longer sent" in str(deprecation_warnings[0].message)
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


class TestPersonalizationFieldsNotSerialized:
    """Etsy removed the four personalization fields from createDraftListing and
    updateListing (2026-09 spec). The kwargs are kept for source compatibility,
    but the values must never reach the wire."""

    PERSONALIZATION_KWARGS = dict(
        is_personalizable=True,
        personalization_is_required=True,
        personalization_char_count_max=256,
        personalization_instructions="Enter name",
    )

    def _make_create_kwargs(self):
        return dict(
            quantity=1,
            title="Test",
            description="A test",
            price=25.00,
            who_made=WhoMade.I_DID,
            when_made=WhenMade.TWENTY_TWENTIES,
            taxonomy_id=30303,
        )

    def test_create_omits_personalization_from_payload(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            req = CreateDraftListingRequest(
                **self._make_create_kwargs(), **self.PERSONALIZATION_KWARGS
            )
        payload = req.get_dict()
        assert [key for key in payload if "personaliz" in key] == []
        # Non-removed fields still serialize normally.
        assert payload["title"] == "Test"

    def test_update_omits_personalization_from_payload(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            req = UpdateListingRequest(title="Updated", **self.PERSONALIZATION_KWARGS)
        payload = req.get_dict()
        assert [key for key in payload if "personaliz" in key] == []
        assert payload["title"] == "Updated"

    def test_create_keeps_personalization_readable(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            req = CreateDraftListingRequest(
                **self._make_create_kwargs(), **self.PERSONALIZATION_KWARGS
            )
        assert req.is_personalizable is True
        assert req.personalization_is_required is True
        assert req.personalization_char_count_max == 256
        assert req.personalization_instructions == "Enter name"

    def test_update_keeps_personalization_readable(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            req = UpdateListingRequest(**self.PERSONALIZATION_KWARGS)
        assert req.is_personalizable is True
        assert req.personalization_is_required is True
        assert req.personalization_char_count_max == 256
        assert req.personalization_instructions == "Enter name"

    def test_warning_points_at_caller(self):
        # The warning is raised two frames below __init__, so stacklevel must
        # be deep enough to blame the caller's line, not the SDK internals.
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            UpdateListingRequest(is_personalizable=True)
        assert w[0].filename == __file__

    def test_post_construction_assignment_still_works(self):
        # The fields became properties; assignment must keep working for
        # callers that set them after construction, and must still not
        # serialize.
        req = UpdateListingRequest(title="Updated")
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            req.is_personalizable = True
            req.personalization_is_required = True
            req.personalization_char_count_max = 256
            req.personalization_instructions = "Enter name"
            deprecation_warnings = [
                x for x in w if issubclass(x.category, DeprecationWarning)
            ]
        assert len(deprecation_warnings) == 4
        assert req.is_personalizable is True
        assert req.personalization_is_required is True
        assert req.personalization_char_count_max == 256
        assert req.personalization_instructions == "Enter name"
        assert [key for key in req.get_dict() if "personaliz" in key] == []

    def test_setter_warning_points_at_caller(self):
        # The setter path is one frame shallower than the constructor path, so
        # it passes its own stacklevel.
        req = UpdateListingRequest(title="Updated")
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            req.is_personalizable = True
        assert w[0].filename == __file__

    def test_setter_does_not_warn_on_falsy_value(self):
        req = UpdateListingRequest(title="Updated")
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            req.is_personalizable = False
            req.personalization_char_count_max = 0
            deprecation_warnings = [
                x for x in w if issubclass(x.category, DeprecationWarning)
            ]
        assert len(deprecation_warnings) == 0
        assert req.is_personalizable is False

    def test_defaults_to_none_when_not_passed(self):
        req = UpdateListingRequest(title="Updated")
        assert req.is_personalizable is None
        assert req.personalization_is_required is None
        assert req.personalization_char_count_max is None
        assert req.personalization_instructions is None


class TestUpdateListingTranslationRequest:
    def test_stores_fields(self):
        req = UpdateListingTranslationRequest(
            title="New title",
            description="New description",
            tags=["a", "b"],
        )
        assert req.title == "New title"
        assert req.description == "New description"
        assert req.tags == ["a", "b"]

    def test_missing_mandatory_raises(self):
        with pytest.raises(Exception):
            UpdateListingTranslationRequest()


class TestUpdateListingPersonalizationRequest:
    def test_stores_personalization_questions(self):
        questions = [{"personalization_question": "Name?"}]
        req = UpdateListingPersonalizationRequest(personalization_questions=questions)
        assert req.personalization_questions == questions

    def test_missing_mandatory_raises(self):
        with pytest.raises(Exception):
            UpdateListingPersonalizationRequest()

    def test_add_on_price_passes_through(self):
        # `add_on_price` was added to the updateListingPersonalization request
        # body in the 2026-07-27 spec. Questions are typed as
        # List[Dict[str, Any]], so new per-question fields reach the API without
        # an SDK change — this pins that pass-through behaviour.
        req = UpdateListingPersonalizationRequest(
            personalization_questions=[
                {
                    "question_text": "Name?",
                    "question_type": "text_input",
                    "required": False,
                    "add_on_price": 4.50,
                }
            ]
        )
        assert req.get_dict()["personalization_questions"][0]["add_on_price"] == 4.50


class TestUpdateListingVideoRequest:
    def test_sets_file_and_data(self):
        req = UpdateListingVideoRequest(
            video_id=42, video_bytes=b"fake-mp4-bytes", name="clip.mp4"
        )
        assert req.file == {"video": b"fake-mp4-bytes"}
        assert req.data == {"video_id": 42, "name": "clip.mp4"}

    def test_defaults_are_none(self):
        req = UpdateListingVideoRequest()
        assert req.file == {"video": None}
        assert req.data == {"video_id": None, "name": None}


class TestECGTFields:
    """EU commercial guarantee (ECGT/GPSR) fields on create and update."""

    @staticmethod
    def _create_kwargs():
        return {
            "quantity": 10,
            "title": "Test Mug",
            "description": "A test mug",
            "price": 25.00,
            "who_made": WhoMade.I_DID,
            "when_made": WhenMade.TWENTY_TWENTIES,
            "taxonomy_id": 30303,
        }

    def test_create_serializes_all_ecgt_fields(self):
        req = CreateDraftListingRequest(
            **self._create_kwargs(),
            ecgt_garan_brand="Acme",
            ecgt_garan_model="MUG-1",
            ecgt_garan_years=3,
            ecgt_garan_guarantee_details="Three year guarantee.",
            ecgt_other_commercial_guarantee_details="Extended cover available.",
            ecgt_after_sales_service_info="Contact support@example.com",
            ecgt_software_update_details="Not applicable.",
        )
        result = req.get_dict()
        assert result["ecgt_garan_brand"] == "Acme"
        assert result["ecgt_garan_model"] == "MUG-1"
        assert result["ecgt_garan_years"] == 3
        assert result["ecgt_garan_guarantee_details"] == "Three year guarantee."
        assert (
            result["ecgt_other_commercial_guarantee_details"]
            == "Extended cover available."
        )
        assert result["ecgt_after_sales_service_info"] == "Contact support@example.com"
        assert result["ecgt_software_update_details"] == "Not applicable."

    def test_update_serializes_all_ecgt_fields(self):
        req = UpdateListingRequest(
            ecgt_garan_brand="Acme",
            ecgt_garan_model="MUG-1",
            ecgt_garan_years=5,
            ecgt_garan_guarantee_details="Five year guarantee.",
            ecgt_other_commercial_guarantee_details="Extended cover available.",
            ecgt_after_sales_service_info="Contact support@example.com",
            ecgt_software_update_details="Not applicable.",
        )
        result = req.get_dict()
        assert result["ecgt_garan_years"] == 5
        assert result["ecgt_garan_brand"] == "Acme"
        assert result["ecgt_software_update_details"] == "Not applicable."

    def test_create_omits_unset_ecgt_fields(self):
        req = CreateDraftListingRequest(**self._create_kwargs())
        result = req.get_dict()
        for field in (
            "ecgt_garan_brand",
            "ecgt_garan_model",
            "ecgt_garan_years",
            "ecgt_garan_guarantee_details",
            "ecgt_other_commercial_guarantee_details",
            "ecgt_after_sales_service_info",
            "ecgt_software_update_details",
        ):
            assert field not in result

    def test_update_omits_unset_ecgt_fields(self):
        result = UpdateListingRequest(title="Just a title").get_dict()
        assert not any(key.startswith("ecgt_") for key in result)

    def test_ecgt_fields_are_nullable(self):
        """An explicitly empty ECGT string clears the value rather than being dropped."""
        req = UpdateListingRequest(ecgt_garan_brand="")
        assert req.get_dict()["ecgt_garan_brand"] is None

    def test_ecgt_does_not_warn(self):
        """ECGT fields are current, unlike the deprecated personalization ones."""
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            CreateDraftListingRequest(
                **self._create_kwargs(), ecgt_garan_brand="Acme"
            )
