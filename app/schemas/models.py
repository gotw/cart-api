from typing import List
from uuid import UUID

from pydantic import BaseModel


class Item(BaseModel):
    item_id: UUID
    item_name: str
    quantity: int

    class Config:
        json_encoders = {
            UUID: lambda v: str(v)
        }

    def dict(self, **kwargs):
        base_dict = super().dict(**kwargs)
        base_dict["item_id"] = str(base_dict["item_id"])
        return base_dict


class Cart(BaseModel):
    cart_id: UUID
    items: List[Item]

    class Config:
        json_encoders = {
            UUID: lambda v: str(v)
        }

    def dict(self, **kwargs):
        base_dict = super().dict(**kwargs)
        base_dict["cart_id"] = str(base_dict["cart_id"])
        base_dict["items"] = [item.dict() for item in self.items]

        return base_dict
