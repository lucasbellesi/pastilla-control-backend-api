from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.security import (
    create_access_token,
    get_password_hash,
    is_legacy_password_hash,
    verify_password,
)
from app.models.user import User
from app.schemas.auth import RegisterRequest, TokenResponse


router = APIRouter()


@router.post("/register", response_model=TokenResponse)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> TokenResponse:
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        if verify_password(payload.password, existing.hashed_password):
            token = create_access_token(subject=str(existing.id))
            return TokenResponse(access_token=token)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")

    user = User(
        email=payload.email,
        full_name=payload.full_name,
        hashed_password=get_password_hash(payload.password),
        role=payload.role,
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        existing_after_race = db.query(User).filter(User.email == payload.email).first()
        if existing_after_race and verify_password(payload.password, existing_after_race.hashed_password):
            token = create_access_token(subject=str(existing_after_race.id))
            return TokenResponse(access_token=token)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")

    db.refresh(user)

    token = create_access_token(subject=str(user.id))
    return TokenResponse(access_token=token)


@router.post("/login", response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> TokenResponse:
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    if is_legacy_password_hash(user.hashed_password):
        user.hashed_password = get_password_hash(form_data.password)
        db.commit()

    token = create_access_token(subject=str(user.id))
    return TokenResponse(access_token=token)
