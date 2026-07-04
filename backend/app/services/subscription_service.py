from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Subscription
from app.services.feature_gate import is_pro


async def get_or_create_subscription(db: AsyncSession, session_id: str) -> Subscription:
    result = await db.execute(select(Subscription).where(Subscription.session_id == session_id))
    sub = result.scalar_one_or_none()
    if sub:
        return sub
    sub = Subscription(session_id=session_id, plan="free", status="inactive")
    db.add(sub)
    await db.flush()
    return sub


async def get_subscription(db: AsyncSession, session_id: str) -> Optional[Subscription]:
    result = await db.execute(select(Subscription).where(Subscription.session_id == session_id))
    return result.scalar_one_or_none()


def subscription_to_dict(sub: Optional[Subscription]) -> dict:
    if not sub:
        return {
            "plan": "free",
            "status": "inactive",
            "is_pro": False,
            "current_period_end": None,
            "email": None,
        }
    return {
        "plan": sub.plan,
        "status": sub.status,
        "is_pro": is_pro(sub.plan, sub.status),
        "current_period_end": sub.current_period_end.isoformat() if sub.current_period_end else None,
        "email": sub.email,
    }


async def activate_pro(
    db: AsyncSession,
    session_id: str,
    *,
    email: Optional[str],
    stripe_customer_id: str,
    stripe_subscription_id: str,
    current_period_end: Optional[datetime],
    status: str = "active",
) -> Subscription:
    sub = await get_or_create_subscription(db, session_id)
    sub.plan = "pro"
    sub.status = status
    sub.email = email or sub.email
    sub.stripe_customer_id = stripe_customer_id
    sub.stripe_subscription_id = stripe_subscription_id
    sub.current_period_end = current_period_end
    sub.updated_at = datetime.utcnow()
    await db.flush()
    return sub


async def update_subscription_status(
    db: AsyncSession,
    stripe_subscription_id: str,
    *,
    status: str,
    current_period_end: Optional[datetime] = None,
) -> Optional[Subscription]:
    result = await db.execute(
        select(Subscription).where(Subscription.stripe_subscription_id == stripe_subscription_id)
    )
    sub = result.scalar_one_or_none()
    if not sub:
        return None

    sub.status = status
    if current_period_end:
        sub.current_period_end = current_period_end

    if status in ("active", "trialing"):
        sub.plan = "pro"
    elif status in ("canceled", "unpaid", "incomplete_expired"):
        sub.plan = "free"

    sub.updated_at = datetime.utcnow()
    await db.flush()
    return sub


async def downgrade_to_free(db: AsyncSession, stripe_subscription_id: str) -> Optional[Subscription]:
    return await update_subscription_status(
        db, stripe_subscription_id, status="canceled"
    )
