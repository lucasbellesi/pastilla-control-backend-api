from fastapi import APIRouter

from app.api.routes import auth, health, medications, schedules


api_router = APIRouter()
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(medications.router, prefix="/medications", tags=["medications"])
api_router.include_router(schedules.router, prefix="/schedules", tags=["schedules"])
