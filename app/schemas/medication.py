from pydantic import BaseModel


class MedicationBase(BaseModel):
    name: str
    dosage_amount: str
    dosage_unit: str
    notes: str | None = None
    is_active: bool = True


class MedicationCreate(MedicationBase):
    pass


class MedicationUpdate(MedicationBase):
    pass


class MedicationOut(MedicationBase):
    id: int

    class Config:
        from_attributes = True
