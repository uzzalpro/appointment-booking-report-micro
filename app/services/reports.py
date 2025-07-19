from app.db.session import get_db
from app.db.models.models import Appointment, UserModel
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.worker import celery_app
import pytz

@celery_app.task
def generate_monthly_report():
    print("Generating monthly doctor report...")

    db: Session = next(get_db())
    now = datetime.now(pytz.timezone("Asia/Dhaka"))
    first_day = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last_day = now

    doctors = db.query(UserModel).filter(UserModel.user_type == "DOCTOR").all()
    print("\n--- Monthly Doctor Report ---")

    for doctor in doctors:
        appointments = db.query(Appointment).filter(
            Appointment.doctor_id == doctor.id,
            Appointment.appointment_date >= first_day,
            Appointment.appointment_date <= last_day,
            Appointment.status == "COMPLETED"
        ).all()

        total_appointments = len(appointments)
        earnings = total_appointments * (doctor.consultation_fee or 0)

        print(f"Doctor: {doctor.full_name}")
        print(f"  Total Visits: {total_appointments}")
        print(f"  Total Earnings: {earnings} BDT")
        print("")

    db.close()