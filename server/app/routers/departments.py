from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..auth import authenticate, authorize

router = APIRouter(prefix="/api/departments", tags=["departments"], dependencies=[Depends(authenticate)])


@router.get("", response_model=list[schemas.DepartmentOut])
def get_departments(db: Session = Depends(get_db)):
    return db.query(models.Department).all()


@router.post("", response_model=schemas.DepartmentOut, status_code=201, dependencies=[Depends(authorize("Admin"))])
def create_department(body: schemas.DepartmentCreate, db: Session = Depends(get_db)):
    department = models.Department(
        name=body.name,
        parent_id=body.parent_id,
        head_id=body.head_id,
        status=body.status or "Active",
    )
    db.add(department)
    db.commit()
    db.refresh(department)
    return department


@router.put("/{department_id}", response_model=schemas.DepartmentOut, dependencies=[Depends(authorize("Admin"))])
def update_department(department_id: int, body: schemas.DepartmentUpdate, db: Session = Depends(get_db)):
    department = db.query(models.Department).filter(models.Department.id == department_id).first()
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    data = body.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(department, field, value)
    db.commit()
    db.refresh(department)
    return department


@router.delete("/{department_id}", dependencies=[Depends(authorize("Admin"))])
def delete_department(department_id: int, db: Session = Depends(get_db)):
    department = db.query(models.Department).filter(models.Department.id == department_id).first()
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    db.delete(department)
    db.commit()
    return {"message": "Department deleted"}
