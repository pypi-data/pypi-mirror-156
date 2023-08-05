from typing import List

from bson import ObjectId
from pydantic import BaseModel, Field

from fastel.cart.datastructures import CartConfig, ItemConfig, Product


class ProductItem(BaseModel):
    name: str
    amount: int
    price: int
    sales_amount: int
    unit_sales: int
    product: Product

    config: ItemConfig


class Checkout(CartConfig):
    id: ObjectId = Field(alias="_id")
    total: int
    subtotal: int
    sales: int
    fee: int
    discount: int
    tax: int

    items: List[ProductItem]

    class Config:
        arbitrary_types_allowed = True


class Order(Checkout):
    pass
