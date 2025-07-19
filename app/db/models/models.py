from datetime import datetime
from sqlalchemy import Table, Column, Integer, Text, String, Boolean,Enum, DateTime, ForeignKey, JSON, func, TIMESTAMP, DECIMAL,Float,Date
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import MetaData
from app.config import config
from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum
import enum
SQLALCHEMY_DATABASE_SCHEMA = config.POSTGRES_SCHEMA

metadata = MetaData(schema=SQLALCHEMY_DATABASE_SCHEMA)  # Define the schema

Base = declarative_base(metadata=metadata)


class AppointmentStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"

class Appointment(Base):
    __tablename__ = "appointments"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer)
    doctor_id = Column(Integer)
    appointment_date = Column(DateTime, nullable=False)
    notes = Column(String, nullable=True)
    status = Column(SQLEnum(AppointmentStatus, name="appointment_status_enum"), default=AppointmentStatus.PENDING)
    created_at = Column(DateTime, server_default="now()")



# class PeriodicTaskModel(Base):
#     __tablename__ = 'periodic_task'

#     id = Column(Integer, primary_key=True)
#     task_id = Column(String(200), unique=True)
#     task_path = Column(String(200))
#     cron_syntax = Column(String(100))  # Interval in seconds
#     args = Column(String(500))
#     user_id = Column(Integer, ForeignKey('users.id',ondelete="CASCADE"), nullable=False)
#     created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class DoctorReport(Base):
    __tablename__ = "doctor_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer)
    month = Column(Integer, nullable=False)  # 1-12
    year = Column(Integer, nullable=False)
    total_patient_visits = Column(Integer, default=0)
    total_appointments = Column(Integer, default=0)
    total_earnings = Column(Float, default=0.0)
    generated_at = Column(Date, server_default=func.now())