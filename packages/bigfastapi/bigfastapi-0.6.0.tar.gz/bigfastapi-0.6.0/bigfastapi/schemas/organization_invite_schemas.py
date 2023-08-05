from typing import Any, Optional

from .organization_schemas import _OrganizationBase
from .organization_user_schemas import organizationUserBase

from .email_schema import Email
from pydantic import BaseModel

class InviteBase(BaseModel):
    id: Optional[str]
    user_email: Optional[str]
    user_id: Optional[str]
    user_role: Optional[str]
    is_accepted: Optional[bool] = False
    is_revoked: Optional[bool] = False
    is_deleted: Optional[bool] = False

    class Config:
        orm_mode = True

class UserInvite(InviteBase):
    store: dict
    app_url: str
    email_details: Email

class Invite(InviteBase):
    store_id: str
    invite_code: str
    
    class Config:
        orm_mode = True


class organizationUser(InviteBase):
    organization_id: str
    user_id: str

class InviteResponse(BaseModel):
    message: str

org: dict = dict(
    id="string",
    mission="string",
    vision="string",
    name="string",
    country="string",
    state="string",
    address="string",
    currency_preference="string",
    phone_number="string",
    email="string",
    current_subscription="string",
    tagline="string",
    image="string",
    values="string",
    business_type="retail",
    image_full_path="string",
)
class SingleInviteResponse(BaseModel):
    invite: Any = dict(id="string", user_email="string", user_id="string", user_role="string", store=org)
    user: str

class AcceptInviteResponse(BaseModel):
    invited: organizationUserBase
    store: _OrganizationBase

class RevokedInviteResponse(InviteBase):
    is_revoked: bool = True
    is_deleted: bool = True

class DeclinedInviteResponse(InviteBase):
    is_deleted: bool = True