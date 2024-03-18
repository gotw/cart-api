from injector import Module

from app.repositories.cart_repository import CartRepository
from app.services.cart_service import CartService
from redis import StrictRedis


class AppModule(Module):
    def configure(self, binder):
        redis_client = StrictRedis(host='0.0.0.0', port=6379, db=0, decode_responses=True)
        binder.bind(CartRepository, to=CartRepository(redis_client))
        binder.bind(CartService, to=CartService(CartRepository(redis_client)))
