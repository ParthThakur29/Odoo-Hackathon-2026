import json
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request

from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..auth import authenticate, authorize, get_user_id
from ..helpers import log_activity
from ..socket_manager import emit_notification

router = APIRouter(prefix="/api/allocations", tags=["allocations"], dependencies=[Depends(authenticate)])


@router.get("", response_model=list[schemas.AllocationOut])
def get_allocations(
    assetId: Optional[int] = None,
    employeeId: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(models.Allocation)
    if assetId:
        query = query.filter(models.Allocation.asset_id == assetId)
    if employeeId:
        query = query.filter(models.Allocation.employee_id == employeeId)
    if status:
        query = query.filter(models.Allocation.status == status)
    return query.order_by(models.Allocation.created_at.desc()).all()


@router.get("/overdue", response_model=list[schemas.AllocationOut])
def get_overdue_allocations(db: Session = Depends(get_db)):
    return (
        db.query(models.Allocation)
        .filter(
            models.Allocation.status == "Active",
            models.Allocation.expected_return_date < datetime.utcnow(),
        )
        .order_by(models.Allocation.expected_return_date.asc())
        .all()
    )


@router.post("", response_model=schemas.AllocationOut, status_code=201)
async def create_allocation(
    body: schemas.AllocationCreate,
    request: Request,
    db: Session = Depends(get_db),
    _=Depends(authorize("AssetManager", "DepartmentHead")),
):
    asset = db.query(models.Asset).filter(models.Asset.id == body.asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    if asset.status == "Allocated":
        raise HTTPException(
            status_code=409,
            detail={
                "error": "Asset already allocated",
                "heldBy": asset.allocated_to.name if asset.allocated_to else "unknown",
            },
        )
    if asset.status != "Available":
        raise HTTPException(status_code=409, detail="Asset not available for allocation")

    allocation = models.Allocation(
        asset_id=body.asset_id,
        employee_id=body.employee_id,
        department_id=body.department_id,
        expected_return_date=body.expected_return_date,
        status="Active",
    )
    db.add(allocation)
    asset.status = "Allocated"
    asset.allocated_to_id = body.employee_id
    db.commit()
    db.refresh(allocation)

    log_activity(
        db,
        get_user_id(request),
        "allocated",
        f"Asset {asset.tag} ({asset.name}) to Employee ID {body.employee_id}",
    )

    employee = db.query(models.Employee).filter(models.Employee.id == body.employee_id).first()
    db.add(
        models.Notification(
            employee_id=body.employee_id,
            message=f"Asset {asset.name} ({asset.tag}) has been allocated to you.",
            type="AssetAssigned",
            link=f"/assets/{asset.id}",
        )
    )
    db.commit()
    await emit_notification(body.employee_id, {"message": f"Asset {asset.name} allocated to you."})

    managers = db.query(models.Employee).filter(models.Employee.role == "AssetManager").all()
    for manager in managers:
        await emit_notification(
            manager.id, {"message": f"New allocation: {asset.tag} to {employee.name if employee else body.employee_id}"}
        )

    return allocation


@router.put("/{allocation_id}", response_model=schemas.AllocationOut)
def update_allocation(
    allocation_id: int,
    body: schemas.AllocationUpdate,
    db: Session = Depends(get_db),
    _=Depends(authorize("AssetManager", "DepartmentHead")),
):
    allocation = db.query(models.Allocation).filter(models.Allocation.id == allocation_id).first()
    if not allocation:
        raise HTTPException(status_code=404, detail="Allocation not found")

    if body.expected_return_date is not None:
        allocation.expected_return_date = body.expected_return_date
    if body.status is not None:
        allocation.status = body.status

    if body.status == "Returned":
        asset = db.query(models.Asset).filter(models.Asset.id == allocation.asset_id).first()
        asset.status = "Available"
        asset.allocated_to_id = None

    db.commit()
    db.refresh(allocation)
    return allocation


@router.post("/{allocation_id}/return", response_model=schemas.AllocationOut)
async def return_allocation(
    allocation_id: int,
    body: schemas.AllocationReturn,
    request: Request,
    db: Session = Depends(get_db),
    _=Depends(authorize("AssetManager")),
):
    allocation = db.query(models.Allocation).filter(models.Allocation.id == allocation_id).first()
    if not allocation:
        raise HTTPException(status_code=404, detail="Allocation not found")
    if allocation.status == "Returned":
        raise HTTPException(status_code=400, detail="Already returned")

    allocation.actual_return_date = datetime.utcnow()
    allocation.condition_check = body.condition_check
    allocation.status = "Returned"

    asset = db.query(models.Asset).filter(models.Asset.id == allocation.asset_id).first()
    asset.status = "Available"
    asset.allocated_to_id = None
    db.commit()
    db.refresh(allocation)

    log_activity(
        db,
        get_user_id(request),
        "returned",
        f"Asset {asset.tag} from {allocation.employee.name if allocation.employee else 'employee'}",
    )

    await emit_notification(allocation.employee_id, {"message": f"Asset {asset.name} has been returned."})

    return allocation


@router.post("/{allocation_id}/transfer")
async def transfer_request(
    allocation_id: int,
    body: schemas.AllocationTransferRequest,
    request: Request,
    db: Session = Depends(get_db),
    _=Depends(authorize("AssetManager", "DepartmentHead")),
):
    allocation = db.query(models.Allocation).filter(models.Allocation.id == allocation_id).first()
    if not allocation:
        raise HTTPException(status_code=404, detail="Allocation not found")
    if allocation.status != "Active":
        raise HTTPException(status_code=400, detail="Only active allocations can be transferred")

    allocation.status = "TransferRequested"
    allocation.condition_check = json.dumps(
        {
            "requestedBy": get_user_id(request),
            "newEmployeeId": body.new_employee_id,
            "newDepartmentId": body.new_department_id,
            "requestedAt": datetime.utcnow().isoformat(),
        }
    )
    db.commit()
    db.refresh(allocation)

    log_activity(
        db,
        get_user_id(request),
        "transfer_requested",
        f"Transfer of asset {allocation.asset.tag} to Employee {body.new_employee_id}",
    )

    managers = db.query(models.Employee).filter(models.Employee.role == "AssetManager").all()
    for manager in managers:
        db.add(
            models.Notification(
                employee_id=manager.id,
                message=f"Transfer request for asset {allocation.asset.tag} from {allocation.employee.name if allocation.employee else 'current holder'}",
                type="TransferRequested",
                link=f"/allocations/{allocation.id}",
            )
        )
        db.commit()
        await emit_notification(manager.id, {"message": f"Transfer request for {allocation.asset.tag}"})

    return {"message": "Transfer request submitted", "allocation": schemas.AllocationOut.model_validate(allocation)}


@router.post("/{allocation_id}/approve-transfer")
async def approve_transfer(
    allocation_id: int,
    request: Request,
    db: Session = Depends(get_db),
    _=Depends(authorize("AssetManager")),
):
    allocation = db.query(models.Allocation).filter(models.Allocation.id == allocation_id).first()
    if not allocation:
        raise HTTPException(status_code=404, detail="Allocation not found")
    if allocation.status != "TransferRequested":
        raise HTTPException(status_code=400, detail="No pending transfer request for this allocation")

    try:
        target = json.loads(allocation.condition_check)
    except (TypeError, json.JSONDecodeError):
        raise HTTPException(status_code=400, detail="Invalid transfer request data")
    if not target.get("newEmployeeId"):
        raise HTTPException(status_code=400, detail="Target employee not specified")

    allocation.status = "TransferApproved"
    allocation.actual_return_date = datetime.utcnow()
    allocation.condition_check = f"{allocation.condition_check} - approved at {datetime.utcnow().isoformat()}"

    new_alloc = models.Allocation(
        asset_id=allocation.asset_id,
        employee_id=target["newEmployeeId"],
        department_id=target.get("newDepartmentId") or allocation.department_id,
        expected_return_date=allocation.expected_return_date,
        status="Active",
    )
    db.add(new_alloc)

    asset = db.query(models.Asset).filter(models.Asset.id == allocation.asset_id).first()
    asset.allocated_to_id = target["newEmployeeId"]
    asset.status = "Allocated"

    db.commit()
    db.refresh(allocation)
    db.refresh(new_alloc)

    log_activity(
        db,
        get_user_id(request),
        "transfer_approved",
        f"Transferred asset {asset.tag} to Employee {target['newEmployeeId']}",
    )

    new_employee = db.query(models.Employee).filter(models.Employee.id == target["newEmployeeId"]).first()
    if new_employee:
        db.add(
            models.Notification(
                employee_id=target["newEmployeeId"],
                message=f"Asset {asset.name} ({asset.tag}) has been transferred to you.",
                type="AssetAssigned",
                link=f"/assets/{allocation.asset_id}",
            )
        )
        db.commit()
        await emit_notification(target["newEmployeeId"], {"message": f"Asset {asset.tag} transferred to you."})

    await emit_notification(allocation.employee_id, {"message": f"Asset {asset.tag} has been transferred away from you."})

    return {
        "message": "Transfer approved and executed",
        "result": {
            "oldAlloc": schemas.AllocationOut.model_validate(allocation),
            "newAlloc": schemas.AllocationOut.model_validate(new_alloc),
        },
    }