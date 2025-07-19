# app/routers/reports.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional
from ..core.database import get_db
from ..models.report import DoctorReport
from ..schemas.report import DoctorReport as DoctorReportSchema

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.get("/monthly", response_model=list[DoctorReportSchema])
def get_monthly_reports(
    year: Optional[int] = None,
    month: Optional[int] = None,
    doctor_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get monthly reports with optional filters"""
    query = db.query(DoctorReport)
    
    if year:
        query = query.filter(DoctorReport.year == year)
    if month:
        query = query.filter(DoctorReport.month == month)
    if doctor_id:
        query = query.filter(DoctorReport.doctor_id == doctor_id)
    
    return query.order_by(DoctorReport.year.desc(), DoctorReport.month.desc()).all()

@router.get("/monthly/summary")
def get_monthly_summary(
    year: Optional[int] = None,
    month: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get summary of all monthly reports"""
    query = db.query(
        func.sum(DoctorReport.total_patient_visits).label("total_patients"),
        func.sum(DoctorReport.total_appointments).label("total_appointments"),
        func.sum(DoctorReport.total_earnings).label("total_earnings")
    )
    
    if year:
        query = query.filter(DoctorReport.year == year)
    if month:
        query = query.filter(DoctorReport.month == month)
    
    result = query.first()
    return {
        "total_patients": result[0] or 0,
        "total_appointments": result[1] or 0,
        "total_earnings": result[2] or 0
    }