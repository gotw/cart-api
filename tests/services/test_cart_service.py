import uuid
from unittest.mock import Mock

from app.services.cart_service import CartService
from tests.utils import stubbed_cart, random_int, random_string, stubbed_item


class TestCartService:
    def setup_method(self):
        self.mock_cart_repo = Mock()
        self.test_object = CartService(self.mock_cart_repo)

    def test_get_carts_returns_carts(self):
        carts = [stubbed_cart(), stubbed_cart()]
        self.mock_cart_repo.get_carts.return_value = carts

        assert self.test_object.get_carts() == carts

    def test_get_cart_returns_cart(self):
        cart = stubbed_cart()

        self.mock_cart_repo.get_cart.return_value = cart

        assert self.test_object.get_cart(cart_id=cart.cart_id) == cart

    def test_get_cart_returns_none_when_cart_not_found(self):
        cart_id = uuid.uuid4()

        self.mock_cart_repo.get_cart.return_value = None

        assert self.test_object.get_cart(cart_id=cart_id) is None

    def test_add_item_adds_quantity_to_existing_item(self):
        cart = stubbed_cart()

        self.mock_cart_repo.get_cart.return_value = cart

        expected = cart.items[0]
        quantity = random_int()
        expected.quantity += quantity
        actual = self.test_object.add_item(
            cart_id=cart.cart_id,
            item_name=cart.items[0].item_name,
            quantity=quantity
        )

        assert actual == expected
        cart.items[0] = expected
        self.mock_cart_repo.save_cart.assert_called_once_with(cart=cart)

    def test_add_item_creates_new_item_when_cart_does_not_exist(self):
        self.mock_cart_repo.get_cart.return_value = None

        item_name = random_string()
        quantity = random_int()
        actual = self.test_object.add_item(
            cart_id=uuid.uuid4(),
            item_name=item_name,
            quantity=quantity
        )

        assert actual.quantity == quantity
        assert actual.item_name == item_name
        self.mock_cart_repo.save_cart.assert_called_once()

    def test_add_item_creates_new_item_when_item_does_not_exist(self):
        cart = stubbed_cart()
        self.mock_cart_repo.get_cart.return_value = cart

        item_name = random_string()
        quantity = random_int()
        actual = self.test_object.add_item(
            cart_id=cart.cart_id,
            item_name=item_name,
            quantity=quantity
        )

        assert actual.quantity == quantity
        assert actual.item_name == item_name
        self.mock_cart_repo.save_cart.assert_called_once()

    def test_get_item_returns_item(self):
        cart = stubbed_cart()
        self.mock_cart_repo.get_cart.return_value = cart

        actual = self.test_object.get_item(cart_id=cart.cart_id, item_id=cart.items[0].item_id)

        assert actual == cart.items[0]

    def test_get_item_returns_none_when_cart_does_not_exist(self):
        self.mock_cart_repo.get_cart.return_value = None

        actual = self.test_object.get_item(
            cart_id=uuid.uuid4(),
            item_id=uuid.uuid4()
        )

        assert actual is None

    def test_get_item_returns_none_when_item_does_not_exist(self):
        self.mock_cart_repo.get_cart.return_value = stubbed_cart()

        actual = self.test_object.get_item(
            cart_id=uuid.uuid4(),
            item_id=uuid.uuid4()
        )

        assert actual is None

    def test_delete_cart_returns_result_from_repo(self):
        self.mock_cart_repo.delete_cart.return_value = True
        assert CartService(self.mock_cart_repo).delete_cart(cart_id=uuid.uuid4())
        self.mock_cart_repo.delete_cart.assert_called_once()

    def test_delete_item_returns_true_when_item_exists(self):
        cart = stubbed_cart()
        self.mock_cart_repo.get_cart.return_value = cart
        actual = self.test_object.delete_item(
            cart_id=cart.cart_id,
            item_id=cart.items[0].item_id
        )

        assert actual
        cart.items = []
        self.mock_cart_repo.save_cart.assert_called_once_with(cart=cart)

    def test_delete_item_returns_false_when_item_does_not_exist(self):
        cart = stubbed_cart()
        self.mock_cart_repo.get_cart.return_value = cart
        actual = self.test_object.delete_item(
            cart_id=cart.cart_id,
            item_id=uuid.uuid4()
        )

        assert not actual
        self.mock_cart_repo.save_cart.assert_not_called()

    def test_delete_item_returns_false_when_cart_does_not_exist(self):
        self.mock_cart_repo.get_cart.return_value = None
        actual = self.test_object.delete_item(
            cart_id=uuid.uuid4(),
            item_id=uuid.uuid4()
        )

        assert not actual
        self.mock_cart_repo.save_cart.assert_not_called()

    def test_remove_quantity_returns_0_when_cart_does_not_exist(self):
        self.mock_cart_repo.get_cart.return_value = None
        actual = self.test_object.remove_quantity(
            cart_id=uuid.uuid4(),
            item_id=uuid.uuid4(),
            quantity=random_int(low=1)
        )

        assert actual == 0

    def test_remove_quantity_returns_0_when_item_does_not_exist(self):
        cart = stubbed_cart()
        self.mock_cart_repo.get_cart.return_value = cart
        actual = self.test_object.remove_quantity(
            cart_id=cart.cart_id,
            item_id=uuid.uuid4(),
            quantity=random_int(low=1)
        )

        assert actual == 0

    def test_remove_quantity_returns_quantity_requested_when_quantity_is_greater_or_equal_than_requested(self):
        cart = stubbed_cart(items=[stubbed_item(quantity=random_int(low=10))])
        quantity_to_remove = random_int(high=9)
        self.mock_cart_repo.get_cart.return_value = cart
        actual = self.test_object.remove_quantity(
            cart_id=cart.cart_id,
            item_id=cart.items[0].item_id,
            quantity=quantity_to_remove
        )

        assert actual == quantity_to_remove
        cart.items[0].quantity -= quantity_to_remove
        self.mock_cart_repo.save_cart.assert_called_with(cart=cart)

    def test_remove_quantity_returns_item_quantity_when_requested_is_more_than_quantity(self):
        quantity = random_int(high=9)
        cart = stubbed_cart(items=[stubbed_item(quantity=quantity)])
        quantity_to_remove = random_int(low=10)
        self.mock_cart_repo.get_cart.return_value = cart
        actual = self.test_object.remove_quantity(
            cart_id=cart.cart_id,
            item_id=cart.items[0].item_id,
            quantity=quantity_to_remove
        )

        assert actual == quantity
        cart.items = []
        self.mock_cart_repo.save_cart.assert_called_with(cart=cart)

    def test_clear_carts_calls_repo_clear_carts(self):
        self.test_object.clear_carts()
        self.mock_cart_repo.clear_carts.assert_called_once()
