import uuid
from typing import List
from typing import Optional
from uuid import UUID

from injector import inject

from app.repositories.cart_repository import CartRepository
from app.schemas.models import Cart, Item


class CartService:
    @inject
    def __init__(self, cart_repo: CartRepository):
        self._cart_repo = cart_repo

    def get_carts(self) -> List[Cart]:
        return self._cart_repo.get_carts()

    def get_cart(self, cart_id: UUID) -> Cart:
        return self._cart_repo.get_cart(cart_id)

    def add_item(self, cart_id: UUID, item_name: str, quantity: int) -> Item:
        cart = self.get_cart(cart_id)
        if cart == None:
            cart = Cart(cart_id=cart_id, items=[])
        item = next((x for x in cart.items if x.item_name == item_name), None)
        if item:
            item.quantity += quantity
        else:
            item = Item(item_id=uuid.uuid4(), item_name=item_name, quantity=quantity)
            cart.items.append(item)

        self._cart_repo.save_cart(cart=cart)

        return item

    def get_item(self, cart_id: UUID, item_id: UUID) -> Optional[Item]:
        cart = self.get_cart(cart_id)
        item = None
        if cart:
            item = next((x for x in cart.items if x.item_id == item_id), None)

        return item

    def delete_cart(self, cart_id: UUID) -> bool:
        return self._cart_repo.delete_cart(cart_id)

    def delete_item(self, cart_id: UUID, item_id: UUID) -> bool:
        cart = self.get_cart(cart_id)
        if cart:
            items = [i for i in cart.items if i.item_id != item_id]
            if len(items) < len(cart.items):
                cart.items = items
                self._cart_repo.save_cart(cart=cart)
                return True
            else:
                return False
        else:
            return False

    def remove_quantity(self, cart_id: UUID, item_id: UUID, quantity) -> int:
        cart = self.get_cart(cart_id)
        items_removed = 0
        if cart:
            item = next((x for x in cart.items if x.item_id == item_id), None)
            if item:
                if item.quantity <= quantity:
                    items_removed = item.quantity
                    cart.items = [x for x in cart.items if x.item_id != item_id]
                else:
                    items_removed = quantity
                    item.quantity -= quantity

                self._cart_repo.save_cart(cart=cart)

        return items_removed

    def clear_carts(self):
        self._cart_repo.clear_carts()
