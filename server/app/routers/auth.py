import os

from fastapi import APIRouter, Depends, HTTPException, Response, Request
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..auth import authenticate, create_access_token, hash_password, verify_password, get_user_id

router = APIRouter(prefix="/api/auth", tags=["auth"])

COOKIE_SECURE = os.getenv("NODE_ENV") == "production"


@router.post("/signup", status_code=201)
def signup(body: schemas.SignupRequest, db: Session = Depends(get_db)):
    existing = db.query(models.Employee).filter(models.Employee.email == body.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")

    employee = models.Employee(
        name=body.name,
        email=body.email,
        password=hash_password(body.password),
        role="Employee",
    )
    db.add(employee)
    db.commit()
    return {"message": "Account created"}


@router.post("/login", response_model=schemas.LoginResponse)
def login(body: schemas.LoginRequest, response: Response, db: Session = Depends(get_db)):
    employee = db.query(models.Employee).filter(models.Employee.email == body.email).first()
    if not employee:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if employee.status != "Active":
        raise HTTPException(status_code=401, detail="Account inactive")
    if not verify_password(body.password, employee.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(employee.id, employee.role)
    response.set_cookie(
        key="token",
        value=token,
        httponly=True,
        secure=COOKIE_SECURE,
        max_age=7 * 24 * 60 * 60,
    )
    return employee


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("token")
    return {"message": "Logged out"}


@router.get("/me", response_model=schemas.EmployeeOut)
def me(request: Request, db: Session = Depends(get_db), _=Depends(authenticate)):
    employee = (
        db.query(models.Employee)
        .filter(models.Employee.id == get_user_id(request))
        .first()
    )
    if not employee:
        raise HTTPException(status_code=404, detail="User not found")
    return employee


@router.post("/forgot-password")
def forgot_password():
    # Placeholder - in a real system send reset email
    return {"message": "Password reset link sent"}
