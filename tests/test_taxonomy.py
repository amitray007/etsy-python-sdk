import pytest

from etsy_python.v3.resources.Taxonomy import (
    BuyerTaxonomyResource,
    SellerTaxonomyResource,
)
from etsy_python.v3.resources.Response import Response


@pytest.mark.readonly
class TestBuyerTaxonomy:
    def test_get_buyer_taxonomy_nodes(self, etsy_client):
        resource = BuyerTaxonomyResource(session=etsy_client)
        response = resource.get_buyer_taxonomy_nodes()
        assert isinstance(response, Response)
        assert response.code == 200
        assert "results" in response.message

    def test_get_properties_by_buyer_taxonomy_id(self, etsy_client):
        resource = BuyerTaxonomyResource(session=etsy_client)
        # Taxonomy ID 1 is a root node that should always exist
        response = resource.get_properties_by_buyer_taxonomy_id(taxonomy_id=1)
        assert isinstance(response, Response)
        assert response.code == 200


@pytest.mark.readonly
class TestSellerTaxonomy:
    def test_get_seller_taxonomy_nodes(self, etsy_client):
        resource = SellerTaxonomyResource(session=etsy_client)
        response = resource.get_seller_taxonomy_nodes()
        assert isinstance(response, Response)
        assert response.code == 200
        assert "results" in response.message
