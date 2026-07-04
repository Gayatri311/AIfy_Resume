from datetime import datetime, timezone
from typing import Literal, Optional

import stripe

from app.core.config import get_settings

settings = get_settings()


def stripe_configured() -> bool:
    return bool(settings.stripe_secret_key and settings.stripe_price_monthly)


def _init_stripe() -> None:
    if not settings.stripe_secret_key:
        raise RuntimeError("STRIPE_SECRET_KEY is not configured")
    stripe.api_key = settings.stripe_secret_key


def price_id_for_interval(interval: Literal["monthly", "yearly"]) -> str:
    price = settings.stripe_price_yearly if interval == "yearly" else settings.stripe_price_monthly
    if not price:
        raise RuntimeError(f"Stripe price not configured for {interval}")
    return price


def create_checkout_session(
    session_id: str,
    interval: Literal["monthly", "yearly"],
    *,
    customer_email: Optional[str] = None,
) -> str:
    _init_stripe()
    price_id = price_id_for_interval(interval)

    params: dict = {
        "mode": "subscription",
        "line_items": [{"price": price_id, "quantity": 1}],
        "success_url": f"{settings.frontend_url.rstrip('/')}/pricing/success?session_id={{CHECKOUT_SESSION_ID}}",
        "cancel_url": f"{settings.frontend_url.rstrip('/')}/pricing/cancel",
        "client_reference_id": session_id,
        "metadata": {"alfy_session_id": session_id},
        "subscription_data": {"metadata": {"alfy_session_id": session_id}},
        "allow_promotion_codes": True,
    }
    if customer_email:
        params["customer_email"] = customer_email

    checkout = stripe.checkout.Session.create(**params)
    if not checkout.url:
        raise RuntimeError("Stripe did not return a checkout URL")
    return checkout.url


def create_portal_session(stripe_customer_id: str) -> str:
    _init_stripe()
    portal = stripe.billing_portal.Session.create(
        customer=stripe_customer_id,
        return_url=f"{settings.frontend_url.rstrip('/')}/pricing",
    )
    return portal.url


def verify_webhook(payload: bytes, sig_header: str) -> stripe.Event:
    _init_stripe()
    if not settings.stripe_webhook_secret:
        raise RuntimeError("STRIPE_WEBHOOK_SECRET is not configured")
    return stripe.Webhook.construct_event(payload, sig_header, settings.stripe_webhook_secret)


def retrieve_checkout_session(session_id: str) -> stripe.checkout.Session:
    _init_stripe()
    return stripe.checkout.Session.retrieve(
        session_id,
        expand=["subscription", "customer"],
    )


def ts_to_datetime(ts: Optional[int]) -> Optional[datetime]:
    if not ts:
        return None
    return datetime.fromtimestamp(ts, tz=timezone.utc).replace(tzinfo=None)
