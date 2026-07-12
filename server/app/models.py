from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, UniqueConstraint
)
from sqlalchemy.orm import relationship
from .database import Base


class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    parent_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    head_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    status = Column(String, default="Active")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    parent = relationship("Department", remote_side=[id], backref="children")
    head = relationship("Employee", foreign_keys=[head_id])
    employees = relationship("Employee", back_populates="department", foreign_keys="Employee.department_id")
    assets = relationship("Asset", back_populates="department", foreign_keys="Asset.department_id")


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text, nullable=True)
    extra_fields = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    assets = relationship("Asset", back_populates="category")


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    role = Column(String, default="Employee")
    status = Column(String, default="Active")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    department = relationship("Department", back_populates="employees", foreign_keys=[department_id])
    allocated_assets = relationship("Asset", back_populates="allocated_to", foreign_keys="Asset.allocated_to_id")
    bookings = relationship("Booking", back_populates="employee")
    maintenance_requests = relationship(
        "MaintenanceRequest", back_populates="requester", foreign_keys="MaintenanceRequest.requester_id"
    )
    audits_assigned = relationship("AuditAssignment", back_populates="auditor")


class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    tag = Column(String, unique=True, nullable=False)
    serial_number = Column(String, nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    acquisition_date = Column(DateTime, nullable=True)
    acquisition_cost = Column(Float, nullable=True)
    condition = Column(String, default="Good")
    location = Column(String, nullable=True)
    is_shared = Column(Boolean, default=False)
    status = Column(String, default="Available")
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    photo = Column(String, nullable=True)
    documents = Column(Text, nullable=True)
    allocated_to_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    category = relationship("Category", back_populates="assets")
    department = relationship("Department", back_populates="assets", foreign_keys=[department_id])
    allocated_to = relationship("Employee", back_populates="allocated_assets", foreign_keys=[allocated_to_id])
    allocations = relationship("Allocation", back_populates="asset")
    maintenance_requests = relationship("MaintenanceRequest", back_populates="asset")
    audit_items = relationship("AuditItem", back_populates="asset")


class Allocation(Base):
    __tablename__ = "allocations"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    expected_return_date = Column(DateTime, nullable=True)
    actual_return_date = Column(DateTime, nullable=True)
    status = Column(String, default="Active")
    condition_check = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    asset = relationship("Asset", back_populates="allocations")
    employee = relationship("Employee")
    department = relationship("Department")


class Booking(Base):
    __tablename__ = "bookings"
    __table_args__ = (UniqueConstraint("asset_id", "start_time", "end_time", name="uq_booking_slot"),)

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    status = Column(String, default="Upcoming")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    asset = relationship("Asset")
    employee = relationship("Employee", back_populates="bookings")


class MaintenanceRequest(Base):
    __tablename__ = "maintenance_requests"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    requester_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    description = Column(Text, nullable=False)
    priority = Column(String, default="Medium")
    photo = Column(String, nullable=True)
    status = Column(String, default="Pending")
    assigned_to_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    resolution_note = Column(Text, nullable=True)
    approved_at = Column(DateTime, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    asset = relationship("Asset", back_populates="maintenance_requests")
    requester = relationship("Employee", back_populates="maintenance_requests", foreign_keys=[requester_id])
    assigned_to = relationship("Employee", foreign_keys=[assigned_to_id])


class AuditCycle(Base):
    __tablename__ = "audit_cycles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    location = Column(String, nullable=True)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    status = Column(String, default="Open")
    discrepancy_report = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    department = relationship("Department")
    assignments = relationship("AuditAssignment", back_populates="audit_cycle")


class AuditAssignment(Base):
    __tablename__ = "audit_assignments"

    id = Column(Integer, primary_key=True, index=True)
    audit_cycle_id = Column(Integer, ForeignKey("audit_cycles.id"), nullable=False)
    auditor_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    audit_cycle = relationship("AuditCycle", back_populates="assignments")
    auditor = relationship("Employee", back_populates="audits_assigned")
    audit_items = relationship("AuditItem", back_populates="audit_assignment")


class AuditItem(Base):
    __tablename__ = "audit_items"

    id = Column(Integer, primary_key=True, index=True)
    audit_assignment_id = Column(Integer, ForeignKey("audit_assignments.id"), nullable=False)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    status = Column(String, nullable=False)
    note = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    audit_assignment = relationship("AuditAssignment", back_populates="audit_items")
    asset = relationship("Asset", back_populates="audit_items")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    message = Column(Text, nullable=False)
    type = Column(String, nullable=False)
    read = Column(Boolean, default=False)
    link = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    employee = relationship("Employee")


class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    action = Column(String, nullable=False)
    details = Column(Text, nullable=False)
    ip = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    employee = relationship("Employee")
