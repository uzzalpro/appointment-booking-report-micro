from pydantic import BaseModel, EmailStr, field_validator, Field
from typing import Optional, Any
import re
import enum
from datetime import datetime



class PatientResponse(BaseModel):
    id: int
    full_name: str
    email: str
    mobile: str
    division: Optional[str]
    district: Optional[str]
    thana: Optional[str]

    class Config:
        from_attributes = True


class DoctorResponse(BaseModel):
    id: int
    full_name: str
    email: str
    mobile: str
    division: Optional[str]
    district: Optional[str]
    thana: Optional[str]
    license_number: Optional[str]
    experience_years: Optional[int]
    consultation_fee: Optional[int]
    available_timeslots: Optional[str]

    class Config:
        from_attributes = True  # Enables ORM mode (same as orm_mode = True)