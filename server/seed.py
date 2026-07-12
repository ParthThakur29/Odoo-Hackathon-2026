"""Seed the database with initial data. Equivalent to prisma/seed.js.

Usage: python seed.py
"""
from datetime import datetime

from app.database import SessionLocal, Base, engine
from app import models
from app.auth import hash_password

Base.metadata.create_all(bind=engine)


def main():
    db = SessionLocal()
    try:
        dept_it = models.Department(name="IT")
        dept_hr = models.Department(name="HR")
        db.add_all([dept_it, dept_hr])
        db.commit()
        db.refresh(dept_it)
        db.refresh(dept_hr)

        cat_electronics = models.Category(name="Electronics", extra_fields='{"warranty": true}')
        cat_furniture = models.Category(name="Furniture")
        db.add_all([cat_electronics, cat_furniture])
        db.commit()
        db.refresh(cat_electronics)

        hashed_password = hash_password("admin123")

        admin = models.Employee(
            name="Admin User", email="admin@company.com", password=hashed_password,
            role="Admin", department_id=dept_it.id,
        )
        manager = models.Employee(
            name="Asset Manager", email="manager@company.com", password=hashed_password,
            role="AssetManager", department_id=dept_it.id,
        )
        head = models.Employee(
            name="Head IT", email="headit@company.com", password=hashed_password,
            role="DepartmentHead", department_id=dept_it.id,
        )
        employee = models.Employee(
            name="John Doe", email="john@company.com", password=hashed_password,
            role="Employee", department_id=dept_it.id,
        )
        db.add_all([admin, manager, head, employee])
        db.commit()

        db.add(models.Asset(
            name="Laptop Dell XPS", tag="AF-0001", serial_number="SN123456",
            category_id=cat_electronics.id, acquisition_date=datetime(2023, 1, 1),
            acquisition_cost=1200, condition="Good", location="IT Office",
            is_shared=False, status="Available", department_id=dept_it.id,
        ))
        db.add(models.Asset(
            name="Projector Epson", tag="AF-0002", serial_number="SN789012",
            category_id=cat_electronics.id, acquisition_date=datetime(2022, 6, 15),
            acquisition_cost=800, condition="Good", location="Conference Room",
            is_shared=True, status="Available", department_id=dept_it.id,
        ))
        db.commit()

        print("Seed completed")
    finally:
        db.close()


if __name__ == "__main__":
    main()
