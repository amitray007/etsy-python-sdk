from typing import List, Optional

from etsy_python.v3.enums.ProcessingProfile import ProcessingTimeUnit, ReadinessState
from etsy_python.v3.models.Request import Request


class CreateShopReadinessStateDefinitionRequest(Request):
    nullable: List[str] = [
        "processing_time_unit",
    ]
    mandatory: List[str] = [
        "readiness_state",
        "min_processing_time",
        "max_processing_time",
    ]

    def __init__(
        self,
        readiness_state: Optional[ReadinessState] = None,
        min_processing_time: Optional[int] = None,
        max_processing_time: Optional[int] = None,
        processing_time_unit: Optional[ProcessingTimeUnit] = None,
    ):
        self.readiness_state = readiness_state.value if readiness_state else None
        self.min_processing_time = min_processing_time
        self.max_processing_time = max_processing_time
        self.processing_time_unit = (
            processing_time_unit.value if processing_time_unit else None
        )
        super().__init__(
            nullable=CreateShopReadinessStateDefinitionRequest.nullable,
            mandatory=CreateShopReadinessStateDefinitionRequest.mandatory,
        )


class UpdateShopReadinessStateDefinitionRequest(Request):
    nullable: List[str] = [
        "readiness_state",
        "min_processing_time",
        "max_processing_time",
        "processing_time_unit",
    ]
    mandatory: List[str] = []

    def __init__(
        self,
        readiness_state: Optional[ReadinessState] = None,
        min_processing_time: Optional[int] = None,
        max_processing_time: Optional[int] = None,
        processing_time_unit: Optional[ProcessingTimeUnit] = None,
    ):
        self.readiness_state = readiness_state.value if readiness_state else None
        self.min_processing_time = min_processing_time
        self.max_processing_time = max_processing_time
        self.processing_time_unit = (
            processing_time_unit.value if processing_time_unit else None
        )
        super().__init__(
            nullable=UpdateShopReadinessStateDefinitionRequest.nullable,
            mandatory=UpdateShopReadinessStateDefinitionRequest.mandatory,
        )
