from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    email: EmailStr
    full_name: str
    password: str
    role: str = "PATIENT"


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
