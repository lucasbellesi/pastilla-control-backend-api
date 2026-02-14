from pydantic import BaseModel


class ScheduleBase(BaseModel):
    medication_id: int
    type: str
    time_of_day: str = "08:00"
    days_of_week_mask: int = 0
    interval_hours: int | None = None
    timezone_id: str = "UTC"
    grace_minutes: int = 30
    is_active: bool = True


class ScheduleCreate(ScheduleBase):
    pass


class ScheduleOut(ScheduleBase):
    id: int

    class Config:
        from_attributes = True
