import os
import shutil
import time
import random
from datetime import datetime, time as dtime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File
from sqlalchemy import or_
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..auth import authenticate, authorize

router = APIRouter(prefix="/api/assets", tags=["assets"], dependencies=[Depends(authenticate)])

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "uploads")
UPLOAD_DIR = os.path.abspath(UPLOAD_DIR)
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.get("", response_model=list[schemas.AssetOut])
def get_assets(
    category: Optional[int] = None,
    status: Optional[str] = None,
    department: Optional[int] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(models.Asset)
    if category:
        query = query.filter(models.Asset.category_id == category)
    if status:
        query = query.filter(models.Asset.status == status)
    if department:
        query = query.filter(models.Asset.department_id == department)
    if search:
        like = f"%{search}%"
        query = query.filter(
            or_(
                models.Asset.tag.like(like),
                models.Asset.serial_number.like(like),
                models.Asset.name.like(like),
            )
        )
    return query.all()


@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    available = db.query(models.Asset).filter(models.Asset.status == "Available").count()
    allocated = db.query(models.Asset).filter(models.Asset.status == "Allocated").count()
    now = datetime.utcnow()
    active_bookings = (
        db.query(models.Booking)
        .filter(
            models.Booking.status.in_(["Upcoming", "Ongoing"]),
            models.Booking.start_time <= now,
            models.Booking.end_time >= now,
        )
        .count()
    )
    today_start = datetime.combine(now.date(), dtime.min)
    maintenance_today = (
        db.query(models.MaintenanceRequest)
        .filter(
            models.MaintenanceRequest.status == "Pending",
            models.MaintenanceRequest.created_at >= today_start,
        )
        .count()
    )
    return {
        "available": available,
        "allocated": allocated,
        "activeBookings": active_bookings,
        "maintenanceToday": maintenance_today,
    }


@router.get("/overdue")
def get_overdue_returns(db: Session = Depends(get_db)):
    now = datetime.utcnow()
    allocations = (
        db.query(models.Allocation)
        .filter(models.Allocation.status == "Active", models.Allocation.expected_return_date < now)
        .all()
    )
    result = []
    for a in allocations:
        days = (now - a.expected_return_date).days
        result.append(
            {
                "id": a.id,
                "asset": schemas.AssetOut.model_validate(a.asset),
                "employee": schemas.EmployeeOut.model_validate(a.employee),
                "days": days,
            }
        )
    return result


@router.get("/{asset_id}", response_model=schemas.AssetOut)
def get_asset(asset_id: int, db: Session = Depends(get_db)):
    asset = db.query(models.Asset).filter(models.Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset


@router.post("", response_model=schemas.AssetOut, status_code=201, dependencies=[Depends(authorize("Admin", "AssetManager"))])
def create_asset(body: schemas.AssetCreate, db: Session = Depends(get_db)):
    count = db.query(models.Asset).count()
    tag = f"AF-{str(count + 1).zfill(4)}"
    asset = models.Asset(
        name=body.name,
        tag=tag,
        serial_number=body.serial_number,
        category_id=body.category_id,
        acquisition_date=body.acquisition_date,
        acquisition_cost=body.acquisition_cost,
        condition=body.condition,
        location=body.location,
        is_shared=bool(body.is_shared),
        department_id=body.department_id,
        status="Available",
    )
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return asset


@router.put("/{asset_id}", response_model=schemas.AssetOut, dependencies=[Depends(authorize("Admin", "AssetManager"))])
def update_asset(asset_id: int, body: schemas.AssetUpdate, db: Session = Depends(get_db)):
    asset = db.query(models.Asset).filter(models.Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    data = body.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(asset, field, value)
    db.commit()
    db.refresh(asset)
    return asset


@router.delete("/{asset_id}", dependencies=[Depends(authorize("Admin"))])
def delete_asset(asset_id: int, db: Session = Depends(get_db)):
    asset = db.query(models.Asset).filter(models.Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    db.delete(asset)
    db.commit()
    return {"message": "Asset deleted"}


@router.post("/{asset_id}/photo", dependencies=[Depends(authorize("Admin", "AssetManager"))])
def upload_asset_photo(asset_id: int, photo: UploadFile = File(...), db: Session = Depends(get_db)):
    asset = db.query(models.Asset).filter(models.Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    unique = f"{int(time.time() * 1000)}-{random.randint(0, 10**9)}"
    filename = f"{unique}-{photo.filename}"
    dest_path = os.path.join(UPLOAD_DIR, filename)
    with open(dest_path, "wb") as buffer:
        shutil.copyfileobj(photo.file, buffer)

    rel_path = os.path.join("uploads", filename)
    asset.photo = rel_path
    db.commit()
    return {"photo": rel_path}
