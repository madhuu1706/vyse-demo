from fastapi import APIRouter, Request
from sqlalchemy import select

from ..db import SessionLocal
from ..models import Membership, User, Workspace
from ..settings import get_settings

router = APIRouter(prefix="/webhooks", tags=["webhooks"])
settings = get_settings()


@router.post("/clerk")
async def clerk(request: Request):
    """Sync Clerk orgs/users into our tenancy tables. Verify svix signature in prod."""
    evt = await request.json()
    etype = evt.get("type", "")
    data = evt.get("data", {})
    async with SessionLocal() as db:
        if etype == "organization.created":
            db.add(Workspace(clerk_org_id=data["id"], name=data.get("name", "Workspace")))
        elif etype == "user.created":
            email = (data.get("email_addresses") or [{}])[0].get("email_address", "")
            db.add(User(clerk_user_id=data["id"], email=email))
        elif etype == "organizationMembership.created":
            org = (await db.execute(select(Workspace).where(Workspace.clerk_org_id == data["organization"]["id"]))).scalar_one_or_none()
            usr = (await db.execute(select(User).where(User.clerk_user_id == data["public_user_data"]["user_id"]))).scalar_one_or_none()
            if org and usr:
                db.add(Membership(workspace_id=org.id, user_id=usr.id, role=data.get("role", "member")))
        await db.commit()
    return {"ok": True}


@router.post("/stripe")
async def stripe_webhook(request: Request):
    """Update workspace.plan on subscription events. Verify signature in prod."""
    evt = await request.json()
    if evt.get("type") == "checkout.session.completed":
        ws_id = evt["data"]["object"].get("client_reference_id")
        async with SessionLocal() as db:
            ws = await db.get(Workspace, ws_id)
            if ws:
                ws.plan = "pro"
                await db.commit()
    return {"ok": True}
