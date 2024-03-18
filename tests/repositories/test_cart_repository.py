import uuid
from unittest.mock import Mock

from app.repositories.cart_repository import CartRepository
from tests.utils import stubbed_cart


class TestCartRepository:

    def setup_method(self):
        self.mock_redis_client = Mock()
        self.test_object = CartRepository(self.mock_redis_client)

    def test_get_carts_returns_carts(self):
        keys = [uuid.uuid4(), uuid.uuid4()]
        self.mock_redis_client.keys.return_value = keys
        carts = [stubbed_cart(cart_id=keys[0]), stubbed_cart(cart_id=keys[1])]
        self.mock_redis_client.get.side_effect = lambda key: next(
            (cart.model_dump_json() for cart in carts if str(cart.cart_id) == key),
            None
        )

        assert self.test_object.get_carts() == carts

    def test_get_carts_returns_empty_list(self):
        self.mock_redis_client.keys.return_value = []
        assert self.test_object.get_carts() == []

    def test_get_cart_returns_cart(self):
        cart = stubbed_cart()
        self.mock_redis_client.get.return_value = cart.model_dump_json()
        assert self.test_object.get_cart(cart.cart_id) == cart

    def test_get_cart_returns_none(self):
        self.mock_redis_client.get.return_value = None
        assert self.test_object.get_cart(cart_id=uuid.uuid4()) is None

    def test_save_cart_saves_cart(self):
        cart = stubbed_cart()
        self.test_object.save_cart(cart)
        self.mock_redis_client.set.assert_called_once_with(
            name=str(cart.cart_id),
            value=cart.model_dump_json()
        )

    def test_delete_cart_returns_true_when_deleting_cart(self):
        key = uuid.uuid4()
        self.mock_redis_client.exists.return_value = True
        assert self.test_object.delete_cart(key) is True
        self.mock_redis_client.delete.assert_called_once_with(str(key))

    def test_delete_cart_returns_false_when_key_is_missing(self):
        self.mock_redis_client.exists.return_value = False
        assert self.test_object.delete_cart(uuid.uuid4()) is False
        self.mock_redis_client.delete.assert_not_called()

    def test_clear_carts_flushes_db(self):
        self.test_object.clear_carts()
        self.mock_redis_client.flushdb.assert_called_once()
