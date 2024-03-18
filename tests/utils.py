import random
import string
import uuid
from typing import List, Optional

from pydantic import UUID4

from app.schemas.models import Cart, Item


def random_string(size: int = 10) -> str:
    return ''.join(random.choices(string.ascii_letters, k=size))


def random_int(low: int = 0, high: int = 100) -> int:
    return random.randint(a=low, b=high)


def stubbed_item(
        item_id: Optional[UUID4] = None,
        item_name: Optional[str] = None,
        quantity: Optional[int] = None
) -> Item:
    item_id = uuid.uuid4() if item_id is None else item_id
    item_name = random_string() if item_name is None else item_name
    quantity = random_int() if quantity is None else quantity
    return Item(item_id=item_id, item_name=item_name, quantity=quantity)


def stubbed_cart(
        cart_id: Optional[UUID4] = None,
        items: Optional[List[Item]] = None) -> Cart:
    cart_id = uuid.uuid4() if cart_id is None else cart_id
    items = [stubbed_item()] if items is None else items

    return Cart(cart_id=cart_id, items=items)
