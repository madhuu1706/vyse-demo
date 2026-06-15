from fastapi import APIRouter, Depends, HTTPException

from ..auth import Ctx, current_ctx
from ..settings import get_settings

router = APIRouter(prefix="/v1/billing", tags=["billing"])
settings = get_settings()


@router.post("/checkout")
async def checkout(plan: str = "pro", ctx: Ctx = Depends(current_ctx)):
    if not settings.stripe_secret_key:
        raise HTTPException(501, "Stripe not configured (set STRIPE_SECRET_KEY)")
    import stripe

    stripe.api_key = settings.stripe_secret_key
    price = settings.stripe_price_pro if plan == "pro" else settings.stripe_price_agency
    session = stripe.checkout.Session.create(
        mode="subscription",
        line_items=[{"price": price, "quantity": 1}],
        client_reference_id=str(ctx.workspace.id),
        success_url="http://localhost:3000/settings?ok=1",
        cancel_url="http://localhost:3000/settings",
    )
    return {"url": session.url}


@router.post("/portal")
async def portal(ctx: Ctx = Depends(current_ctx)):
    if not settings.stripe_secret_key:
        raise HTTPException(501, "Stripe not configured")
    return {"url": "https://billing.stripe.com/p/session/stub"}
