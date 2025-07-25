from pydantic import field_validator, Field, BaseModel
from datetime import datetime
import re
from fastapi import UploadFile


def validate_image_file(file: UploadFile):
    if file.content_type not in ["image/jpeg", "image/png"]:
        raise ValueError("Only JPEG/PNG images allowed")
    if file.size > 5 * 1024 * 1024:  # 5MB
        raise ValueError("File size exceeds 5MB")
    return file

def validate_timeslot(start: datetime, end: datetime):
    if start >= end:
        raise ValueError("End time must be after start time")
    if start.hour < 9 or end.hour > 17:
        raise ValueError("Appointments only available between 9AM-5PM")
    return start, end

class AppointmentCreate(BaseModel):
    doctor_id: int
    date_time: datetime
    notes: str = Field(None, max_length=500)
    
    @field_validator('date_time')
    @classmethod
    def validate_future_datetime(cls, v: datetime) -> datetime:
        if v < datetime.now():
            raise ValueError("Appointment date cannot be in the past")
        return v