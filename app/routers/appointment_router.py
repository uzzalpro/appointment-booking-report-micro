# app/routers/appointments.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from datetime import datetime, timedelta
from app.db.session import get_db
from app.dependencies.auth import get_current_user, get_current_user_id
from app.db.models.models import Appointment, AppointmentStatus, UserModel, DoctorSpecialization
from app.data.schemas.appointment.appointmentschema import (
    AppointmentCreate, AppointmentResponse, DoctorResponse,
    AppointmentUpdate, AppointmentStatusUpdate,UserType
    )
from typing import Optional, List
from app.config import config
from datetime import datetime, timezone
from sqlalchemy import func  # Add this import at the top of your file
from pytz import timezone as pytz_timezone
from app.services.appointment_service import update_appointment_by_admin, update_appointment_status_by_doctor
from services.cache_user_service import get_user_info

appointment_router = APIRouter(
    prefix=f"{config.API_PREFIX}",
    tags=['Appointments']
)



def is_doctor_available(doctor_id: int, appointment_date: datetime) -> bool:
    # Convert to local timezone (Asia/Dhaka)
    tz = pytz_timezone("Asia/Dhaka")
    appointment_date_local = appointment_date.astimezone(tz)
    appointment_time = appointment_date_local.time()

    # ✅ Get doctor info from Redis
    doctor = get_user_info(doctor_id)
    if not doctor or doctor.get("user_type") != "doctor" or not doctor.get("available_timeslots"):
        return False

    available_slots = []
    for slot in doctor["available_timeslots"].split(','):
        try:
            start_str, end_str = slot.split('-')
            available_slots.append((start_str.strip(), end_str.strip()))
        except ValueError:
            continue

    for start, end in available_slots:
        try:
            start_time = datetime.strptime(start, "%H:%M").time()
            end_time = datetime.strptime(end, "%H:%M").time()
            if start_time <= appointment_time <= end_time:
                return True
        except ValueError:
            continue

    return False


@appointment_router.post("/book_appointment", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
async def book_appointment(
    appointment: AppointmentCreate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    current_time = datetime.now(timezone.utc)
    if appointment.appointment_date.astimezone(timezone.utc) < current_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Appointment time must be in the future"
        )

    doctor = get_user_info(appointment.doctor_id)
    if not doctor or doctor.get("user_type") != "doctor":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found"
        )

    if not is_doctor_available(db, appointment.doctor_id, appointment.appointment_date):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Doctor is not available at this time"
        )


    existing_appointment = db.query(Appointment).filter(
        Appointment.doctor_id == appointment.doctor_id,
        Appointment.appointment_date == appointment.appointment_date,
        Appointment.status != AppointmentStatus.CANCELLED
    ).first()

    if existing_appointment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Time slot already booked"
        )

    # ✅ Create new appointment
    db_appointment = Appointment(
        doctor_id=appointment.doctor_id,
        patient_id=current_user_id,
        appointment_date=appointment.appointment_date,
        notes=appointment.notes,
        status=AppointmentStatus.PENDING.value
    )

    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)

    return db_appointment




@appointment_router.get("/get_appointment_list", response_model=List[AppointmentResponse])
def get_appointments(
    doctor_id: Optional[int] = Query(None),
    status: Optional[AppointmentStatus] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
        # Only allow admin users
    
    if current_user.user_type != UserType.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users can access this resource"
        )
    
    query = db.query(Appointment)
    # Apply filters conditionally
    if doctor_id is not None:
        query = query.filter(Appointment.doctor_id == doctor_id)
    if status is not None:
        query = query.filter(Appointment.status == status)
    if start_date is not None:
        query = query.filter(Appointment.appointment_date >= start_date)
    if end_date is not None:
        query = query.filter(Appointment.appointment_date <= end_date)

    # Apply pagination
    appointments = query.order_by(Appointment.appointment_date).offset(skip).limit(limit).all()
    response = []
    for appointment in appointments:
        doctor_data = get_user_info(appointment.doctor_id)
        doctor_name = doctor_data["full_name"] if doctor_data else None
        patient_data = get_user_info(appointment.patient_id)
        patient_name = patient_data["full_name"] if patient_data else None

        response.append(AppointmentResponse(
            id=appointment.id,
            appointment_date=appointment.appointment_date,
            doctor_id=appointment.doctor_id,
            doctor_name=doctor_name,
            patient_id=appointment.patient_id,
            patient_name=patient_name,
            notes=appointment.notes,
            status=appointment.status,
        ))

    return response

    # return appointments


@appointment_router.get("/get_appointment_list_by_user", response_model=List[AppointmentResponse])
def get_appointments(
    doctor_id: Optional[int] = Query(None),
    status_filter: Optional[AppointmentStatus] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    # Only allow PATIENT users
    if current_user.user_type != UserType.PATIENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Patient users can access this resource"
        )

    # Start query
    query = db.query(Appointment).filter(Appointment.patient_id == current_user.id)

    if doctor_id:
        query = query.filter(Appointment.doctor_id == doctor_id)
    if status_filter:
        query = query.filter(Appointment.status == status_filter)
    if start_date:
        query = query.filter(Appointment.appointment_date >= start_date)
    if end_date:
        query = query.filter(Appointment.appointment_date <= end_date)

    # Apply ordering and pagination
    appointments = (
        query
        .options(joinedload(Appointment.doctor))  # or `joinedload(Appointment.patient)` if needed
        .order_by(Appointment.appointment_date)
        .offset(skip)
        .limit(limit)
        .all()
    )

    return appointments




@appointment_router.put("/update_appointment/{appointment_id}", response_model=AppointmentResponse)
def update_appointment(
    appointment_id: int,
    payload: AppointmentUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Admin-only endpoint to update an appointment.
    """
    # ✅ Restrict access to Admins only
    if current_user.user_type != UserType.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users can update appointments."
        )

    # ✅ Call service layer to update appointment
    updated_appointment = update_appointment_by_admin(db, appointment_id, payload)

    if not updated_appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Appointment with ID {appointment_id} not found."
        )

    return updated_appointment


@appointment_router.get("/doctor/appointments", response_model=List[AppointmentResponse])
def get_doctor_appointments(
    status_filter: Optional[AppointmentStatus] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Fetch appointments for the currently logged-in doctor,
    optionally filtered by status, start_date, and end_date.
    """
    if current_user.user_type != UserType.DOCTOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can access this endpoint."
        )

    query = db.query(Appointment).filter(Appointment.doctor_id == current_user.id)

    if status_filter:
        query = query.filter(Appointment.status == status_filter)
    if start_date:
        query = query.filter(Appointment.appointment_date >= start_date)
    if end_date:
        query = query.filter(Appointment.appointment_date <= end_date)

    appointments = (
        query.order_by(Appointment.appointment_date)
             .offset(skip)
             .limit(limit)
             .all()
    )

    return appointments



@appointment_router.put("/doctor/update_appointment_status/{appointment_id}", response_model=AppointmentResponse)
def doctor_update_appointment_status(
    appointment_id: int,
    payload: AppointmentStatusUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    if current_user.user_type != UserType.DOCTOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can update appointment status"
        )

    return update_appointment_status_by_doctor(
        db=db,
        doctor_id=current_user.id,
        appointment_id=appointment_id,
        new_status=payload.status
    )