import pytest

from etsy_python.v3.enums.ProcessingProfile import ProcessingTimeUnit, ReadinessState
from etsy_python.v3.models.ProcessingProfile import (
    CreateShopReadinessStateDefinitionRequest,
    UpdateShopReadinessStateDefinitionRequest,
)


class TestCreateShopReadinessStateDefinitionRequest:
    def test_stores_required_fields(self):
        req = CreateShopReadinessStateDefinitionRequest(
            readiness_state=ReadinessState.MADE_TO_ORDER,
            min_processing_time=1,
            max_processing_time=3,
            processing_time_unit=ProcessingTimeUnit.DAYS,
        )
        # Enum values get unwrapped to their string in __init__
        assert req.readiness_state == ReadinessState.MADE_TO_ORDER.value
        assert req.min_processing_time == 1
        assert req.max_processing_time == 3
        assert req.processing_time_unit == ProcessingTimeUnit.DAYS.value

    def test_optional_processing_time_unit_stays_none(self):
        req = CreateShopReadinessStateDefinitionRequest(
            readiness_state=ReadinessState.MADE_TO_ORDER,
            min_processing_time=2,
            max_processing_time=5,
        )
        assert req.processing_time_unit is None

    def test_missing_mandatory_raises(self):
        with pytest.raises(Exception):
            CreateShopReadinessStateDefinitionRequest()


class TestUpdateShopReadinessStateDefinitionRequest:
    def test_no_mandatory_fields(self):
        # All fields are optional on update.
        req = UpdateShopReadinessStateDefinitionRequest()
        assert req.readiness_state is None
        assert req.min_processing_time is None
        assert req.max_processing_time is None
        assert req.processing_time_unit is None

    def test_partial_update_unwraps_enums(self):
        req = UpdateShopReadinessStateDefinitionRequest(
            readiness_state=ReadinessState.MADE_TO_ORDER,
            processing_time_unit=ProcessingTimeUnit.WEEKS,
        )
        assert req.readiness_state == ReadinessState.MADE_TO_ORDER.value
        assert req.processing_time_unit == ProcessingTimeUnit.WEEKS.value
        assert req.min_processing_time is None
        assert req.max_processing_time is None
