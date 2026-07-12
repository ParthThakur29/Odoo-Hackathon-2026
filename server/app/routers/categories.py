from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..auth import authenticate, authorize

router = APIRouter(prefix="/api/categories", tags=["categories"], dependencies=[Depends(authenticate)])


@router.get("", response_model=list[schemas.CategoryOut])
def get_categories(db: Session = Depends(get_db)):
    return db.query(models.Category).all()


@router.post("", response_model=schemas.CategoryOut, status_code=201, dependencies=[Depends(authorize("Admin"))])
def create_category(body: schemas.CategoryCreate, db: Session = Depends(get_db)):
    category = models.Category(name=body.name, description=body.description, extra_fields=body.extra_fields)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.put("/{category_id}", response_model=schemas.CategoryOut, dependencies=[Depends(authorize("Admin"))])
def update_category(category_id: int, body: schemas.CategoryUpdate, db: Session = Depends(get_db)):
    category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    data = body.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(category, field, value)
    db.commit()
    db.refresh(category)
    return category


@router.delete("/{category_id}", dependencies=[Depends(authorize("Admin"))])
def delete_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    db.delete(category)
    db.commit()
    return {"message": "Category deleted"}
