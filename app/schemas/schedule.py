from typing import Literal
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


ScheduleType = Literal["DAILY", "WEEKLY", "INTERVAL"]


class ScheduleBase(BaseModel):
    medication_id: int
    type: ScheduleType
    time_of_day: str = "08:00"
    days_of_week_mask: int = Field(default=0, ge=0, le=127)
    interval_hours: int | None = Field(default=None, ge=1, le=168)
    timezone_id: str = "UTC"
    grace_minutes: int = Field(default=30, ge=0, le=1440)
    is_active: bool = True

    @field_validator("time_of_day")
    @classmethod
    def validate_time_of_day(cls, value: str) -> str:
        parts = value.split(":")
        if len(parts) != 2 or not all(part.isdigit() for part in parts):
            raise ValueError("time_of_day must use HH:MM format")

        hours, minutes = int(parts[0]), int(parts[1])
        if not (0 <= hours <= 23 and 0 <= minutes <= 59):
            raise ValueError("time_of_day must be a valid 24-hour time")

        return f"{hours:02d}:{minutes:02d}"

    @field_validator("timezone_id")
    @classmethod
    def validate_timezone_id(cls, value: str) -> str:
        try:
            ZoneInfo(value)
        except ZoneInfoNotFoundError as exc:
            raise ValueError("timezone_id must be a valid IANA timezone") from exc
        return value


class ScheduleCreate(ScheduleBase):
    @model_validator(mode="after")
    def validate_schedule_rules(self) -> "ScheduleCreate":
        if self.type == "WEEKLY" and self.days_of_week_mask == 0:
            raise ValueError("days_of_week_mask must be > 0 when type is WEEKLY")

        if self.type == "INTERVAL" and self.interval_hours is None:
            raise ValueError("interval_hours is required when type is INTERVAL")

        if self.type in {"DAILY", "WEEKLY"} and self.interval_hours is not None:
            raise ValueError("interval_hours must be null unless type is INTERVAL")

        return self


class ScheduleOut(ScheduleBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
