from unittest.mock import MagicMock

from etsy_python.v3.models.ProcessingProfile import (
    CreateShopReadinessStateDefinitionRequest,
    UpdateShopReadinessStateDefinitionRequest,
)
from etsy_python.v3.resources.ProcessingProfile import ProcessingProfileResource
from etsy_python.v3.resources.Response import Response
from etsy_python.v3.resources.enums.Request import Method

from tests.conftest import MOCK_SHOP_ID

MOCK_DEFINITION_ID = 313131


class TestProcessingProfileResource:
    def test_create_shop_readiness_state_definition(self, mock_session):
        mock_session.make_request.return_value = Response(201, {})
        resource = ProcessingProfileResource(session=mock_session)
        payload = MagicMock(spec=CreateShopReadinessStateDefinitionRequest)

        resource.create_shop_readiness_state_definition(MOCK_SHOP_ID, payload)

        mock_session.make_request.assert_called_once_with(
            f"/shops/{MOCK_SHOP_ID}/readiness-state-definitions",
            method=Method.POST,
            payload=payload,
        )

    def test_get_shop_readiness_state_definitions_uses_default_pagination(
        self, mock_session
    ):
        mock_session.make_request.return_value = Response(200, {"results": []})
        resource = ProcessingProfileResource(session=mock_session)

        resource.get_shop_readiness_state_definitions(MOCK_SHOP_ID)

        mock_session.make_request.assert_called_once_with(
            f"/shops/{MOCK_SHOP_ID}/readiness-state-definitions",
            query_params={"limit": 25, "offset": 0},
        )

    def test_get_shop_readiness_state_definitions_custom_pagination(
        self, mock_session
    ):
        mock_session.make_request.return_value = Response(200, {"results": []})
        resource = ProcessingProfileResource(session=mock_session)

        resource.get_shop_readiness_state_definitions(
            MOCK_SHOP_ID, limit=50, offset=100
        )

        qp = mock_session.make_request.call_args[1]["query_params"]
        assert qp == {"limit": 50, "offset": 100}

    def test_get_shop_readiness_state_definition(self, mock_session):
        mock_session.make_request.return_value = Response(200, {})
        resource = ProcessingProfileResource(session=mock_session)

        resource.get_shop_readiness_state_definition(MOCK_SHOP_ID, MOCK_DEFINITION_ID)

        mock_session.make_request.assert_called_once_with(
            f"/shops/{MOCK_SHOP_ID}/readiness-state-definitions/{MOCK_DEFINITION_ID}"
        )

    def test_update_shop_readiness_state_definition(self, mock_session):
        mock_session.make_request.return_value = Response(200, {})
        resource = ProcessingProfileResource(session=mock_session)
        payload = MagicMock(spec=UpdateShopReadinessStateDefinitionRequest)

        resource.update_shop_readiness_state_definition(
            MOCK_SHOP_ID, MOCK_DEFINITION_ID, payload
        )

        mock_session.make_request.assert_called_once_with(
            f"/shops/{MOCK_SHOP_ID}/readiness-state-definitions/{MOCK_DEFINITION_ID}",
            method=Method.PUT,
            payload=payload,
        )

    def test_delete_shop_readiness_state_definition(self, mock_session):
        mock_session.make_request.return_value = Response(204, "")
        resource = ProcessingProfileResource(session=mock_session)

        resource.delete_shop_readiness_state_definition(
            MOCK_SHOP_ID, MOCK_DEFINITION_ID
        )

        mock_session.make_request.assert_called_once_with(
            f"/shops/{MOCK_SHOP_ID}/readiness-state-definitions/{MOCK_DEFINITION_ID}",
            method=Method.DELETE,
        )
