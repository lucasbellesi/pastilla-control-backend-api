from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.medication import Medication
from app.models.schedule import Schedule
from app.models.user import User
from app.schemas.schedule import ScheduleCreate, ScheduleOut


router = APIRouter()


@router.get("/", response_model=list[ScheduleOut])
def list_schedules(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Schedule]:
    return (
        db.query(Schedule)
        .join(Medication, Medication.id == Schedule.medication_id)
        .filter(Medication.user_id == current_user.id)
        .all()
    )


@router.post("/", response_model=ScheduleOut, status_code=status.HTTP_201_CREATED)
def create_schedule(
    payload: ScheduleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Schedule:
    medication = (
        db.query(Medication)
        .filter(Medication.id == payload.medication_id, Medication.user_id == current_user.id)
        .first()
    )
    if not medication:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Medication not found")

    schedule = Schedule(**payload.model_dump())
    db.add(schedule)
    db.commit()
    db.refresh(schedule)
    return schedule
