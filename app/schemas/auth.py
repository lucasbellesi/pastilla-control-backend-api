from pydantic import BaseModel, EmailStr

from app.models.enums import UserRole


class RegisterRequest(BaseModel):
    email: EmailStr
    full_name: str
    password: str
    role: UserRole = UserRole.PATIENT


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
