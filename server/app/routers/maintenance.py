from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..auth import authenticate, authorize, get_user_id
from ..socket_manager import emit_notification

router = APIRouter(prefix="/api/maintenance", tags=["maintenance"], dependencies=[Depends(authenticate)])


@router.get("", response_model=list[schemas.MaintenanceOut])
def get_requests(db: Session = Depends(get_db)):
    return db.query(models.MaintenanceRequest).all()


@router.post("", response_model=schemas.MaintenanceOut, status_code=201)
def create_request(body: schemas.MaintenanceCreate, request: Request, db: Session = Depends(get_db)):
    req = models.MaintenanceRequest(
        asset_id=body.asset_id,
        requester_id=get_user_id(request),
        description=body.description,
        priority=body.priority,
        photo=body.photo,
        status="Pending",
    )
    db.add(req)
    db.commit()
    db.refresh(req)
    return req


@router.put("/{request_id}", response_model=schemas.MaintenanceOut, dependencies=[Depends(authorize("AssetManager"))])
def update_request(request_id: int, body: schemas.MaintenanceUpdate, db: Session = Depends(get_db)):
    req = db.query(models.MaintenanceRequest).filter(models.MaintenanceRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    data = body.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(req, field, value)
    db.commit()
    db.refresh(req)
    return req


@router.post("/{request_id}/approve", response_model=schemas.MaintenanceOut, dependencies=[Depends(authorize("AssetManager"))])
async def approve_request(request_id: int, db: Session = Depends(get_db)):
    req = db.query(models.MaintenanceRequest).filter(models.MaintenanceRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    req.status = "Approved"
    req.approved_at = datetime.utcnow()

    asset = db.query(models.Asset).filter(models.Asset.id == req.asset_id).first()
    asset.status = "UnderMaintenance"
    db.commit()
    db.refresh(req)

    await emit_notification(req.requester_id, {"message": "Maintenance request approved"})
    return req


@router.post("/{request_id}/assign", response_model=schemas.MaintenanceOut, dependencies=[Depends(authorize("AssetManager"))])
def assign_technician(request_id: int, body: schemas.MaintenanceAssign, db: Session = Depends(get_db)):
    req = db.query(models.MaintenanceRequest).filter(models.MaintenanceRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    req.assigned_to_id = body.technician_id
    req.status = "Assigned"
    db.commit()
    db.refresh(req)
    return req


@router.post("/{request_id}/resolve", response_model=schemas.MaintenanceOut, dependencies=[Depends(authorize("AssetManager"))])
async def resolve_request(request_id: int, body: schemas.MaintenanceResolve, db: Session = Depends(get_db)):
    req = db.query(models.MaintenanceRequest).filter(models.MaintenanceRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    req.status = "Resolved"
    req.resolved_at = datetime.utcnow()
    req.resolution_note = body.resolution_note

    asset = db.query(models.Asset).filter(models.Asset.id == req.asset_id).first()
    asset.status = "Available"
    db.commit()
    db.refresh(req)

    await emit_notification(req.requester_id, {"message": "Maintenance resolved"})
    return req
