import json
from typing import Optional, List
from uuid import UUID

from injector import inject
from redis import Redis

from app.schemas.models import Cart


class CartRepository:

    @inject
    def __init__(self, redis_client: Redis):
        self._redis_client = redis_client

    def get_carts(self) -> List[Cart]:
        keys = self._redis_client.keys()
        if keys:
            return [self.get_cart(key) for key in keys]
        else:
            return []

    def get_cart(self, cart_id: UUID) -> Optional[Cart]:
        read = self._redis_client.get(str(cart_id))
        if read:
            return Cart(**json.loads(read))
        else:
            return None

    def save_cart(self, cart: Cart):
        self._redis_client.set(
            name=str(cart.cart_id),
            value=cart.model_dump_json()
        )

    def delete_cart(self, cart_id: UUID):
        key = str(cart_id)
        if self._redis_client.exists(key):
            self._redis_client.delete(key)

            return True
        else:
            return False

    def clear_carts(self):
        self._redis_client.flushdb()
