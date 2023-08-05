

import datetime as _dt
from locale import currency

import pydantic as _pydantic
from pydantic import Field
from uuid import UUID
from typing import List, Optional


class _OrganizationBase(_pydantic.BaseModel):
    id: Optional[str]
    mission: Optional[str]
    vision: Optional[str]
    name: str
    country: str
    state: str
    address: str
    currency_preference: str
    phone_number: str = None
    email: str = None
    current_subscription: Optional[str]
    tagline: Optional[str]
    image: Optional[str]
    values: Optional[str]
    business_type: str = "retail"
    credit_balance: Optional[int]
    image_full_path: str = None
    add_template: Optional[bool]

    class Config:
        orm_mode = True


class OrganizationCreate(_OrganizationBase):
    pass


class OrganizationUpdate(_OrganizationBase):
    pass


class Organization(_OrganizationBase):
    id: str
    creator: str

    date_created: _dt.datetime
    last_updated: _dt.datetime

    class Config:
        orm_mode = True


class BusinessSwitch(_pydantic.BaseModel):
    id: str
    business_type: str

    class Config:
        orm_mode = True


class PinOrUnpin(BusinessSwitch):
    menu_item: str
    action: str

    class Config:
        orm_mode = True
