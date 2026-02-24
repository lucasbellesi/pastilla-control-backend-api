from pydantic import BaseModel, ConfigDict


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
    model_config = ConfigDict(from_attributes=True)
