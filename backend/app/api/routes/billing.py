import logging

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import get_db
from app.core.deps import require_session_id
from app.schemas.billing import (
    CheckoutRequest,
    CheckoutResponse,
    PortalResponse,
    SubscriptionOut,
    VerifyCheckoutRequest,
    VerifyCheckoutResponse,
)
from app.services import stripe_billing
from app.services.subscription_service import (
    activate_pro,
    downgrade_to_free,
    get_or_create_subscription,
    get_subscription,
    subscription_to_dict,
    update_subscription_status,
)
from app.services.stripe_billing import ts_to_datetime

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/billing", tags=["billing"])
settings = get_settings()


@router.get("/subscription", response_model=SubscriptionOut)
async def get_subscription_status(
    session_id: str = Depends(require_session_id),
    db: AsyncSession = Depends(get_db),
):
    sub = await get_or_create_subscription(db, session_id)
    await db.commit()
    data = subscription_to_dict(sub)
    return SubscriptionOut(**data)


@router.post("/checkout", response_model=CheckoutResponse)
async def create_checkout(
    body: CheckoutRequest,
    session_id: str = Depends(require_session_id),
    db: AsyncSession = Depends(get_db),
):
    if not stripe_billing.stripe_configured():
        raise HTTPException(
            503,
            "Billing is not configured. Set STRIPE_SECRET_KEY and STRIPE_PRICE_MONTHLY in backend .env",
        )
    await get_or_create_subscription(db, session_id)
    await db.commit()

    try:
        url = stripe_billing.create_checkout_session(
            session_id,
            body.interval,
            customer_email=body.email,
        )
    except Exception as e:
        logger.exception("Stripe checkout failed")
        raise HTTPException(502, f"Could not start checkout: {e}") from e

    return CheckoutResponse(url=url)


@router.post("/portal", response_model=PortalResponse)
async def customer_portal(
    session_id: str = Depends(require_session_id),
    db: AsyncSession = Depends(get_db),
):
    sub = await get_subscription(db, session_id)
    if not sub or not sub.stripe_customer_id:
        raise HTTPException(404, "No active billing account found for this session")

    try:
        url = stripe_billing.create_portal_session(sub.stripe_customer_id)
    except Exception as e:
        logger.exception("Stripe portal failed")
        raise HTTPException(502, f"Could not open billing portal: {e}") from e

    return PortalResponse(url=url)


@router.post("/verify-checkout", response_model=VerifyCheckoutResponse)
async def verify_checkout(
    body: VerifyCheckoutRequest,
    session_id: str = Depends(require_session_id),
    db: AsyncSession = Depends(get_db),
):
    """Called from success page — activates Pro if webhook hasn't fired yet."""
    checkout_session_id = body.checkout_session_id
    if not stripe_billing.stripe_configured():
        raise HTTPException(503, "Billing not configured")

    try:
        checkout = stripe_billing.retrieve_checkout_session(checkout_session_id)
    except Exception as e:
        raise HTTPException(400, f"Invalid checkout session: {e}") from e

    meta_session = (checkout.metadata or {}).get("alfy_session_id") or checkout.client_reference_id
    if meta_session != session_id:
        raise HTTPException(403, "Checkout session does not belong to this browser session")

    activated = False
    if checkout.payment_status == "paid" and checkout.subscription:
        subscription = checkout.subscription
        if isinstance(subscription, str):
            import stripe as stripe_lib
            stripe_lib.api_key = settings.stripe_secret_key
            subscription = stripe_lib.Subscription.retrieve(subscription)

        customer_id = checkout.customer if isinstance(checkout.customer, str) else checkout.customer.id
        sub_id = subscription.id if hasattr(subscription, "id") else str(subscription)
        period_end = ts_to_datetime(getattr(subscription, "current_period_end", None))
        status = getattr(subscription, "status", "active")

        await activate_pro(
            db,
            session_id,
            email=checkout.customer_details.email if checkout.customer_details else None,
            stripe_customer_id=customer_id,
            stripe_subscription_id=sub_id,
            current_period_end=period_end,
            status=status,
        )
        activated = True
        await db.commit()

    sub = await get_subscription(db, session_id)
    return VerifyCheckoutResponse(
        subscription=SubscriptionOut(**subscription_to_dict(sub)),
        activated=activated,
    )


@router.post("/webhook")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    payload = await request.body()
    sig = request.headers.get("stripe-signature", "")

    try:
        event = stripe_billing.verify_webhook(payload, sig)
    except Exception as e:
        logger.warning("Webhook verification failed: %s", e)
        raise HTTPException(400, "Invalid webhook signature") from e

    event_type = event["type"]
    data = event["data"]["object"]

    try:
        if event_type == "checkout.session.completed":
            session_id = (data.get("metadata") or {}).get("alfy_session_id") or data.get("client_reference_id")
            if session_id and data.get("subscription"):
                await activate_pro(
                    db,
                    session_id,
                    email=(data.get("customer_details") or {}).get("email"),
                    stripe_customer_id=data.get("customer"),
                    stripe_subscription_id=data.get("subscription"),
                    current_period_end=None,
                    status="active",
                )

        elif event_type in ("customer.subscription.updated", "customer.subscription.created"):
            meta_session = (data.get("metadata") or {}).get("alfy_session_id")
            sub_id = data.get("id")
            status = data.get("status", "active")
            period_end = ts_to_datetime(data.get("current_period_end"))

            if meta_session:
                await activate_pro(
                    db,
                    meta_session,
                    email=None,
                    stripe_customer_id=data.get("customer"),
                    stripe_subscription_id=sub_id,
                    current_period_end=period_end,
                    status=status,
                )
            else:
                await update_subscription_status(
                    db, sub_id, status=status, current_period_end=period_end
                )

        elif event_type == "customer.subscription.deleted":
            await downgrade_to_free(db, data.get("id"))

        elif event_type == "invoice.payment_failed":
            sub_id = data.get("subscription")
            if sub_id:
                await update_subscription_status(db, sub_id, status="past_due")

        await db.commit()
    except Exception:
        logger.exception("Webhook handler error for %s", event_type)
        raise HTTPException(500, "Webhook handler failed")

    return {"received": True}
