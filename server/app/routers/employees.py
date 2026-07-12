from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..auth import authenticate, authorize, get_user_id

router = APIRouter(prefix="/api/employees", tags=["employees"])


@router.get("", response_model=list[schemas.EmployeeOut], dependencies=[Depends(authorize("Admin"))])
def get_employees(
    department: Optional[int] = None,
    role: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(models.Employee)
    if department:
        query = query.filter(models.Employee.department_id == department)
    if role:
        query = query.filter(models.Employee.role == role)
    if status:
        query = query.filter(models.Employee.status == status)
    return query.all()


@router.get("/me", response_model=schemas.EmployeeOut, dependencies=[Depends(authenticate)])
def get_me(request: Request, db: Session = Depends(get_db)):
    employee = db.query(models.Employee).filter(models.Employee.id == get_user_id(request)).first()
    if not employee:
        raise HTTPException(status_code=404, detail="User not found")
    return employee


@router.put("/{employee_id}", response_model=schemas.EmployeeOut, dependencies=[Depends(authorize("Admin"))])
def update_employee(employee_id: int, body: schemas.EmployeeUpdate, db: Session = Depends(get_db)):
    employee = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    data = body.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(employee, field, value)
    db.commit()
    db.refresh(employee)
    return employee
