import json

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..auth import authenticate, authorize, get_user_id

router = APIRouter(prefix="/api/audits", tags=["audits"], dependencies=[Depends(authenticate)])


@router.get("", response_model=list[schemas.AuditCycleOut])
def get_audit_cycles(db: Session = Depends(get_db)):
    return db.query(models.AuditCycle).all()


@router.post("", response_model=schemas.AuditCycleOut, status_code=201, dependencies=[Depends(authorize("Admin"))])
def create_audit_cycle(body: schemas.AuditCycleCreate, db: Session = Depends(get_db)):
    cycle = models.AuditCycle(
        name=body.name,
        department_id=body.department_id,
        location=body.location,
        start_date=body.start_date,
        end_date=body.end_date,
        status="Open",
    )
    db.add(cycle)
    db.commit()
    db.refresh(cycle)
    return cycle


@router.post("/{cycle_id}/assign", response_model=schemas.AuditAssignmentOut, status_code=201, dependencies=[Depends(authorize("Admin"))])
def assign_auditor(cycle_id: int, body: schemas.AuditAssignAuditor, db: Session = Depends(get_db)):
    assignment = models.AuditAssignment(audit_cycle_id=cycle_id, auditor_id=body.auditor_id)
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    return assignment


@router.post("/{cycle_id}/item", response_model=schemas.AuditItemOut)
def mark_audit_item(cycle_id: int, body: schemas.AuditItemCreate, request: Request, db: Session = Depends(get_db)):
    assignment = (
        db.query(models.AuditAssignment)
        .filter(models.AuditAssignment.audit_cycle_id == cycle_id, models.AuditAssignment.auditor_id == get_user_id(request))
        .first()
    )
    if not assignment:
        raise HTTPException(status_code=403, detail="Not assigned to this audit")

    item = models.AuditItem(
        audit_assignment_id=assignment.id,
        asset_id=body.asset_id,
        status=body.status,
        note=body.note,
    )
    db.add(item)

    if body.status == "Missing":
        asset = db.query(models.Asset).filter(models.Asset.id == body.asset_id).first()
        if asset:
            asset.status = "Lost"

    db.commit()
    db.refresh(item)
    return item


@router.post("/{cycle_id}/close", dependencies=[Depends(authorize("Admin"))])
def close_audit_cycle(cycle_id: int, db: Session = Depends(get_db)):
    cycle = db.query(models.AuditCycle).filter(models.AuditCycle.id == cycle_id).first()
    if not cycle:
        raise HTTPException(status_code=404, detail="Audit cycle not found")
    cycle.status = "Closed"
    db.commit()

    items = (
        db.query(models.AuditItem)
        .join(models.AuditAssignment)
        .filter(
            models.AuditAssignment.audit_cycle_id == cycle.id,
            models.AuditItem.status.in_(["Missing", "Damaged"]),
        )
        .all()
    )
    report = [
        {"asset": item.asset.name, "tag": item.asset.tag, "status": item.status, "note": item.note}
        for item in items
    ]
    cycle.discrepancy_report = json.dumps(report)
    db.commit()

    return {"message": "Audit closed", "report": report}
