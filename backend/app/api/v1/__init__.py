"""API v1 router composition."""

from fastapi import APIRouter

from app.api.v1.account import router as account_router
from app.api.v1.admin import router as admin_router
from app.api.v1.auth import router as auth_router
from app.api.v1.cart import router as cart_router
from app.api.v1.catalogue import router as catalogue_router
from app.api.v1.orders import router as orders_router
from app.api.v1.payments import router as payments_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(catalogue_router)
api_v1_router.include_router(cart_router)
api_v1_router.include_router(auth_router)
api_v1_router.include_router(orders_router)
api_v1_router.include_router(payments_router)
api_v1_router.include_router(account_router)
api_v1_router.include_router(admin_router)
