from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.medication import Medication
from app.models.user import User
from app.schemas.medication import MedicationCreate, MedicationOut, MedicationUpdate


router = APIRouter()


@router.get("/", response_model=list[MedicationOut])
def list_medications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Medication]:
    return db.query(Medication).filter(Medication.user_id == current_user.id).all()


@router.post("/", response_model=MedicationOut, status_code=status.HTTP_201_CREATED)
def create_medication(
    payload: MedicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Medication:
    medication = Medication(user_id=current_user.id, **payload.model_dump())
    db.add(medication)
    db.commit()
    db.refresh(medication)
    return medication


@router.put("/{medication_id}", response_model=MedicationOut)
def update_medication(
    medication_id: int,
    payload: MedicationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Medication:
    medication = (
        db.query(Medication)
        .filter(Medication.id == medication_id, Medication.user_id == current_user.id)
        .first()
    )
    if not medication:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Medication not found")

    for key, value in payload.model_dump().items():
        setattr(medication, key, value)

    db.commit()
    db.refresh(medication)
    return medication


@router.delete("/{medication_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_medication(
    medication_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    medication = (
        db.query(Medication)
        .filter(Medication.id == medication_id, Medication.user_id == current_user.id)
        .first()
    )
    if not medication:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Medication not found")

    db.delete(medication)
    db.commit()
