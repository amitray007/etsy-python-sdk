import pytest

from etsy_python.v3.enums.Listing import (
    WhoMade,
    WhenMade,
    State,
    Includes,
)
from etsy_python.v3.models.Listing import (
    CreateDraftListingRequest,
    UpdateListingRequest,
)
from etsy_python.v3.resources.Listing import ListingResource
from etsy_python.v3.resources.Response import Response


@pytest.mark.readonly
class TestListingRead:
    def test_find_all_listings_active(self, etsy_client):
        resource = ListingResource(session=etsy_client)
        response = resource.find_all_listings_active(limit=5)
        assert isinstance(response, Response)
        assert response.code == 200

    def test_get_listings_by_shop(self, etsy_client, shop_id):
        resource = ListingResource(session=etsy_client)
        response = resource.get_listings_by_shop(shop_id, limit=5)
        assert isinstance(response, Response)
        assert response.code == 200


@pytest.mark.write
class TestListingCRUD:
    """Full lifecycle test: create -> read -> update -> delete."""

    @pytest.fixture
    def listing_resource(self, etsy_client):
        return ListingResource(session=etsy_client)

    @pytest.fixture
    def taxonomy_id(self, etsy_client):
        """Get a valid taxonomy ID from the API."""
        from etsy_python.v3.resources.Taxonomy import SellerTaxonomyResource

        resource = SellerTaxonomyResource(session=etsy_client)
        response = resource.get_seller_taxonomy_nodes()
        nodes = response.message.get("results", [])
        # Pick first leaf node or first node
        for node in nodes:
            if node.get("children_ids") == []:
                return node["id"]
        return nodes[0]["id"] if nodes else 1

    def test_listing_lifecycle(self, listing_resource, shop_id, taxonomy_id):
        # CREATE
        create_request = CreateDraftListingRequest(
            quantity=1,
            title="SDK Integration Test Listing - DO NOT BUY",
            description="Automated test listing created by etsy-python-sdk integration tests. This will be deleted.",
            price=9.99,
            who_made=WhoMade.I_DID,
            when_made=WhenMade.TWENTY_TWENTIES,
            taxonomy_id=taxonomy_id,
        )
        create_response = listing_resource.create_draft_listing(
            shop_id, create_request
        )
        assert isinstance(create_response, Response)
        assert create_response.code == 201
        listing_id = create_response.message["listing_id"]

        try:
            # READ
            get_response = listing_resource.get_listing(listing_id)
            assert isinstance(get_response, Response)
            assert get_response.code == 200
            assert get_response.message["title"] == "SDK Integration Test Listing - DO NOT BUY"

            # UPDATE
            update_request = UpdateListingRequest(
                title="SDK Integration Test Listing UPDATED",
            )
            update_response = listing_resource.update_listing(
                shop_id, listing_id, update_request
            )
            assert isinstance(update_response, Response)
            assert update_response.code == 200
            assert update_response.message["title"] == "SDK Integration Test Listing UPDATED"

        finally:
            # DELETE (always cleanup)
            delete_response = listing_resource.delete_listing(listing_id)
            assert isinstance(delete_response, Response)
