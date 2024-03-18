import json
import unittest
import uuid
from unittest.mock import Mock

from fastapi.testclient import TestClient

from app.main import app
from tests.utils import stubbed_cart, stubbed_item, random_int, random_string

client = TestClient(app=app)


def test_clear_responds_with_200():
    response = client.delete("/cart/clear")
    assert response.status_code == 200
    assert response.json() == {"result": "carts cleared"}


def test_clear_throws_http_exception():
    mock_cart_service = Mock()
    mock_cart_service.clear_carts.side_effect = Exception("Test Exception")
    with unittest.mock.patch(
            "app.services.cart_service.CartService.clear_carts",
            new=mock_cart_service.clear_carts
    ):
        response = client.delete("/cart/clear")
        assert response.status_code == 500
        assert response.json() == {"detail": "Test Exception"}


def test_get_all_returns_carts():
    mock_cart_service = Mock()
    carts = [stubbed_cart(), stubbed_cart()]
    mock_cart_service.get_all.return_value = carts
    with unittest.mock.patch(
            "app.services.cart_service.CartService.get_carts",
            new=mock_cart_service.get_all
    ):
        response = client.get("/cart")
        assert response.status_code == 200
        expected = {"carts": [cart.dict() for cart in carts]}
        assert response.json() == expected


def test_get_cart_returns_cart():
    mock_cart_service = Mock()
    cart = stubbed_cart()
    mock_cart_service.get_cart.return_value = cart
    with unittest.mock.patch(
            "app.services.cart_service.CartService.get_cart",
            new=mock_cart_service.get_cart
    ):
        response = client.get(f"/cart/{cart.cart_id}")
        assert response.status_code == 200
        assert response.json() == json.loads(cart.model_dump_json())


def test_add_item_returns_item():
    mock_cart_service = Mock()
    quantity = random_int()
    item = stubbed_item(quantity=quantity + random_int())
    mock_cart_service.add_item.return_value = item
    with unittest.mock.patch(
            "app.services.cart_service.CartService.add_item",
            new=mock_cart_service.add_item
    ):
        response = client.post(f"/cart/{uuid.uuid4()}/{item.item_name}/{quantity}")
        assert response.status_code == 200
        expected = {"item": item.dict()}
        assert response.json() == expected


def test_add_item_throws_exception_when_quantity_is_zero_or_less():
    quantity = random_int(low=-100, high=0)
    response = client.post(f"/cart/{uuid.uuid4()}/{random_string()}/{quantity}")
    assert response.status_code == 400
    assert response.json() == {"detail": "Quantity must be greater than 0."}


def test_get_item_returns_item():
    item = stubbed_item()
    mock_cart_service = Mock()
    mock_cart_service.get_item.return_value = item
    with unittest.mock.patch(
            "app.services.cart_service.CartService.get_item",
            new=mock_cart_service.get_item
    ):
        response = client.get(f"/cart/{uuid.uuid4()}/{item.item_id}")
        assert response.status_code == 200
        expected = {"item": item.dict()}
        assert response.json() == expected


def test_get_item_returns_404_when_item_not_found():
    mock_cart_service = Mock()
    mock_cart_service.get_item.return_value = None
    with unittest.mock.patch(
            "app.services.cart_service.CartService.get_item",
            new=mock_cart_service.get_item
    ):
        response = client.get(f"/cart/{uuid.uuid4()}/{uuid.uuid4()}")
        assert response.status_code == 404
        assert response.json() == {"detail": "Item not found."}


def test_delete_cart_returns_200():
    mock_cart_service = Mock()
    mock_cart_service.delete_cart.return_value = True
    with unittest.mock.patch(
            "app.services.cart_service.CartService.delete_cart",
            new=mock_cart_service.delete_cart
    ):
        response = client.delete(f"/cart/{uuid.uuid4()}")
        assert response.status_code == 200
        assert response.json() == {"result": "Cart deleted."}


def test_delete_cart_returns_404_when_item_not_deleted():
    mock_cart_service = Mock()
    mock_cart_service.delete_cart.return_value = False
    with unittest.mock.patch(
            "app.services.cart_service.CartService.delete_cart",
            new=mock_cart_service.delete_cart
    ):
        response = client.delete(f"/cart/{uuid.uuid4()}")
        assert response.status_code == 404
        assert response.json() == {"detail": "Cart not found."}


def test_delete_item_returns_200():
    mock_cart_service = Mock()
    mock_cart_service.delete_item.return_value = True
    with unittest.mock.patch(
            "app.services.cart_service.CartService.delete_item",
            new=mock_cart_service.delete_item
    ):
        response = client.delete(f"/cart/{uuid.uuid4()}/{uuid.uuid4()}")
        assert response.status_code == 200
        assert response.json() == {"result": "Item deleted."}


def test_delete_item_returns_404_when_item_not_deleted():
    mock_cart_service = Mock()
    mock_cart_service.delete_item.return_value = False
    with unittest.mock.patch(
            "app.services.cart_service.CartService.delete_item",
            new=mock_cart_service.delete_item
    ):
        response = client.delete(f"/cart/{uuid.uuid4()}/{uuid.uuid4()}")
        assert response.status_code == 404
        assert response.json() == {"detail": "Item not found."}


def test_remove_quantity_returns_200_if_quantity_removed_greater_than_0():
    mock_cart_service = Mock()
    quantity = random_int(low=1)
    mock_cart_service.remove_quantity.return_value = quantity
    with unittest.mock.patch(
            "app.services.cart_service.CartService.remove_quantity",
            new=mock_cart_service.remove_quantity
    ):
        response = client.delete(f"/cart/{uuid.uuid4()}/{uuid.uuid4()}/{quantity}")
        assert response.status_code == 200
        assert response.json() == {"result": f"{quantity} items removed."}


def test_remove_quantity_returns_404_if_quantity_removed_is_0_or_less():
    mock_cart_service = Mock()
    quantity = random_int(low=-100, high=0)
    mock_cart_service.remove_quantity.return_value = quantity
    with unittest.mock.patch(
            "app.services.cart_service.CartService.remove_quantity",
            new=mock_cart_service.remove_quantity
    ):
        response = client.delete(f"/cart/{uuid.uuid4()}/{uuid.uuid4()}/{random_int(low=-100, high=0)}")
        assert response.status_code == 404
        assert response.json() == {"detail": "Item not found."}
