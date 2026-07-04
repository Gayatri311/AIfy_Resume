from typing import Literal, Optional

from pydantic import BaseModel, Field


class SubscriptionOut(BaseModel):
    plan: str = "free"
    status: str = "inactive"
    is_pro: bool = False
    current_period_end: Optional[str] = None
    email: Optional[str] = None


class CheckoutRequest(BaseModel):
    interval: Literal["monthly", "yearly"] = "monthly"
    email: Optional[str] = None


class CheckoutResponse(BaseModel):
    url: str


class PortalResponse(BaseModel):
    url: str


class VerifyCheckoutRequest(BaseModel):
    checkout_session_id: str


class VerifyCheckoutResponse(BaseModel):
    subscription: SubscriptionOut
    activated: bool = False
