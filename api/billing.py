"""
Stripe billing scaffold for AchillesOracle.

HOW TO ACTIVATE THE PAYWALL:
1. Run: pip install stripe
2. Add to requirements.in: stripe
3. Set these env vars (or add to .env):
       STRIPE_SECRET_KEY=sk_live_...
       STRIPE_PUBLISHABLE_KEY=pk_live_...
       STRIPE_WEBHOOK_SECRET=whsec_...
       STRIPE_PRICE_ID=price_...     <- your subscription Price ID from the Stripe dashboard
4. Uncomment the blocks below marked  ── UNCOMMENT ──
5. Remove the `raise HTTPException(503...)` lines in each route.
6. Update success_url / cancel_url / return_url to your real domain.
"""

from fastapi import APIRouter, Header, HTTPException, Request
from pydantic import BaseModel

# ── UNCOMMENT ──────────────────────────────────────────────────────────────────
# import stripe
# from achillesoracle.settings import settings
# stripe.api_key = settings.STRIPE_SECRET_KEY
# ──────────────────────────────────────────────────────────────────────────────

router = APIRouter(prefix="/billing", tags=["billing"])


class CheckoutRequest(BaseModel):
    email: str  # switch to EmailStr (pip install pydantic[email]) when billing goes live


@router.post("/checkout")
async def create_checkout_session(body: CheckoutRequest):
    """Create a Stripe Checkout session; redirect user to the returned URL."""
    raise HTTPException(status_code=503, detail="Billing not yet enabled")

    # ── UNCOMMENT ──────────────────────────────────────────────────────────────
    # session = stripe.checkout.Session.create(
    #     payment_method_types=["card"],
    #     mode="subscription",
    #     line_items=[{"price": settings.STRIPE_PRICE_ID, "quantity": 1}],
    #     customer_email=body.email,
    #     success_url="https://yourdomain.com/billing/success",
    #     cancel_url="https://yourdomain.com/billing/cancel",
    # )
    # return {"checkout_url": session.url}
    # ──────────────────────────────────────────────────────────────────────────


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None, alias="stripe-signature"),
):
    """
    Stripe sends events here for payment success, cancellation, renewals, etc.
    Register this URL in your Stripe dashboard → Developers → Webhooks.
    """
    raise HTTPException(status_code=503, detail="Billing not yet enabled")

    # ── UNCOMMENT ──────────────────────────────────────────────────────────────
    # payload = await request.body()
    # try:
    #     event = stripe.Webhook.construct_event(
    #         payload, stripe_signature, settings.STRIPE_WEBHOOK_SECRET
    #     )
    # except stripe.error.SignatureVerificationError:
    #     raise HTTPException(status_code=400, detail="Invalid Stripe signature")
    #
    # match event["type"]:
    #     case "checkout.session.completed":
    #         session = event["data"]["object"]
    #         customer_email = session.get("customer_email")
    #         # TODO: grant access / create user account for customer_email
    #     case "customer.subscription.deleted":
    #         customer_id = event["data"]["object"]["customer"]
    #         # TODO: revoke access for customer_id
    #     case "invoice.payment_failed":
    #         customer_id = event["data"]["object"]["customer"]
    #         # TODO: notify user, grace-period logic
    #
    # return {"received": True}
    # ──────────────────────────────────────────────────────────────────────────


@router.get("/portal")
async def customer_portal(customer_id: str):
    """Redirect a logged-in customer to Stripe's self-service billing portal."""
    raise HTTPException(status_code=503, detail="Billing not yet enabled")

    # ── UNCOMMENT ──────────────────────────────────────────────────────────────
    # portal = stripe.billing_portal.Session.create(
    #     customer=customer_id,
    #     return_url="https://yourdomain.com/account",
    # )
    # return {"portal_url": portal.url}
    # ──────────────────────────────────────────────────────────────────────────


@router.get("/config")
async def billing_config():
    """Return the publishable key so the frontend can initialise Stripe.js."""
    raise HTTPException(status_code=503, detail="Billing not yet enabled")

    # ── UNCOMMENT ──────────────────────────────────────────────────────────────
    # return {"publishable_key": settings.STRIPE_PUBLISHABLE_KEY}
    # ──────────────────────────────────────────────────────────────────────────
