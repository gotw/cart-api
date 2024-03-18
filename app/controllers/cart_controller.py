from typing import List
from uuid import UUID

from fastapi import APIRouter, HTTPException
from injector import Injector

from app.app_module import AppModule
from app.schemas.models import Item, Cart
from app.services.cart_service import CartService

injector = Injector([AppModule()])
cart_service = injector.get(CartService)

router = APIRouter(
    prefix="/cart",
    tags=["Cart Controller"]
)


@router.delete("/clear", tags=["Delete"])
def clear() -> dict[str, str]:
    try:
        cart_service.clear_carts()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"result": "carts cleared"}


@router.get("", tags=["Read"])
def get_all() -> dict[str, List[Cart]]:
    carts = cart_service.get_carts()
    return {"carts": carts}


@router.get("/{cart_id}", tags=["Read"])
def get_cart(cart_id: UUID) -> Cart:
    cart = cart_service.get_cart(cart_id)
    if cart:
        return cart
    else:
        raise HTTPException(status_code=404, detail="Cart not found.")


@router.post("/{cart_id}/{item_name}/{quantity}", tags=["Create"])
def add_item(
        cart_id: UUID,
        item_name: str,
        quantity: int
) -> dict[str, Item]:
    if quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be greater than 0.")

    item = cart_service.add_item(cart_id, item_name, quantity)

    return {"item": item}


@router.get("/{cart_id}/{item_id}", tags=["Read"])
def get_item(
        cart_id: UUID,
        item_id: UUID
) -> dict[str, Item]:
    item = cart_service.get_item(cart_id=cart_id, item_id=item_id)
    if item:
        return {"item": item}
    else:
        raise HTTPException(status_code=404, detail="Item not found.")


@router.delete("/{cart_id}", tags=["Delete"])
def delete_cart(
        cart_id: UUID,
) -> dict[str, str]:
    if cart_service.delete_cart(cart_id):
        return {"result": "Cart deleted."}
    else:
        raise HTTPException(status_code=404, detail="Cart not found.")


@router.delete("/{cart_id}/{item_id}", tags=["Delete"])
def delete_item(
        cart_id: UUID,
        item_id: UUID
) -> dict[str, str]:
    if cart_service.delete_item(cart_id, item_id):
        return {"result": "Item deleted."}
    else:
        raise HTTPException(status_code=404, detail="Item not found.")


@router.delete("/{cart_id}/{item_id}/{quantity}", tags=["Delete"])
def remove_quantity(
        cart_id: UUID,
        item_id: UUID,
        quantity: int
) -> dict[str, str]:
    items_removed = cart_service.remove_quantity(
        cart_id=cart_id,
        item_id=item_id,
        quantity=quantity
    )

    if items_removed > 0:
        return {"result": f"{items_removed} items removed."}
    else:
        raise HTTPException(status_code=404, detail="Item not found.")
