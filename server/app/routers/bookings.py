from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..auth import authenticate, get_user_id
from ..socket_manager import emit_notification

router = APIRouter(prefix="/api/bookings", tags=["bookings"], dependencies=[Depends(authenticate)])


@router.get("", response_model=list[schemas.BookingOut])
def get_bookings(assetId: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(models.Booking)
    if assetId:
        query = query.filter(models.Booking.asset_id == assetId)
    return query.all()


@router.post("", response_model=schemas.BookingOut, status_code=201)
async def create_booking(body: schemas.BookingCreate, request: Request, db: Session = Depends(get_db)):
    employee_id = get_user_id(request)

    overlapping = (
        db.query(models.Booking)
        .filter(
            models.Booking.asset_id == body.asset_id,
            models.Booking.status != "Cancelled",
            or_(
                and_(models.Booking.start_time < body.end_time, models.Booking.start_time >= body.start_time),
                and_(models.Booking.end_time > body.start_time, models.Booking.end_time <= body.end_time),
                and_(models.Booking.start_time <= body.start_time, models.Booking.end_time >= body.end_time),
            ),
        )
        .first()
    )
    if overlapping:
        raise HTTPException(status_code=409, detail="Time slot overlaps with existing booking")

    booking = models.Booking(
        asset_id=body.asset_id,
        employee_id=employee_id,
        start_time=body.start_time,
        end_time=body.end_time,
        status="Upcoming",
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)

    await emit_notification(employee_id, {"message": "Booking confirmed"})

    return booking


@router.put("/{booking_id}", response_model=schemas.BookingOut)
def update_booking(booking_id: int, body: schemas.BookingUpdate, db: Session = Depends(get_db)):
    booking = db.query(models.Booking).filter(models.Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    data = body.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(booking, field, value)
    db.commit()
    db.refresh(booking)
    return booking


@router.delete("/{booking_id}", response_model=schemas.BookingOut)
def cancel_booking(booking_id: int, db: Session = Depends(get_db)):
    booking = db.query(models.Booking).filter(models.Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    booking.status = "Cancelled"
    db.commit()
    db.refresh(booking)
    return booking
