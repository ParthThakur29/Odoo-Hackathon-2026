from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, ConfigDict, Field, EmailStr


def to_camel(s: str) -> str:
    parts = s.split("_")
    return parts[0] + "".join(w.capitalize() for w in parts[1:])


class CamelModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, from_attributes=True)


# ---------- Department ----------
class DepartmentBase(CamelModel):
    name: str
    parent_id: Optional[int] = None
    head_id: Optional[int] = None
    status: Optional[str] = "Active"


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentUpdate(CamelModel):
    name: Optional[str] = None
    parent_id: Optional[int] = None
    head_id: Optional[int] = None
    status: Optional[str] = None


class DepartmentOut(DepartmentBase):
    id: int
    created_at: datetime
    updated_at: datetime
    head: Optional["EmployeeOut"] = None
    parent: Optional["DepartmentOut"] = None
    children: Optional[List["DepartmentOut"]] = None


# ---------- Category ----------
class CategoryBase(CamelModel):
    name: str
    description: Optional[str] = None
    extra_fields: Optional[str] = None


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(CamelModel):
    name: Optional[str] = None
    description: Optional[str] = None
    extra_fields: Optional[str] = None


class CategoryOut(CategoryBase):
    id: int
    created_at: datetime
    updated_at: datetime


# ---------- Employee ----------
class EmployeeBase(CamelModel):
    name: str
    email: EmailStr
    department_id: Optional[int] = None
    role: Optional[str] = "Employee"
    status: Optional[str] = "Active"


class EmployeeUpdate(CamelModel):
    name: Optional[str] = None
    email: Optional[str] = None
    department_id: Optional[int] = None
    role: Optional[str] = None
    status: Optional[str] = None


class EmployeeOut(EmployeeBase):
    id: int
    created_at: datetime
    updated_at: datetime
    department: Optional[DepartmentOut] = None


DepartmentOut.model_rebuild()


# ---------- Auth ----------
class SignupRequest(CamelModel):
    name: str
    email: EmailStr
    password: str


class LoginRequest(CamelModel):
    email: EmailStr
    password: str


class LoginResponse(CamelModel):
    id: int
    name: str
    email: str
    role: str


# ---------- Asset ----------
class AssetBase(CamelModel):
    name: str
    category_id: int
    serial_number: Optional[str] = None
    acquisition_date: Optional[datetime] = None
    acquisition_cost: Optional[float] = None
    condition: Optional[str] = "Good"
    location: Optional[str] = None
    is_shared: Optional[bool] = False
    department_id: Optional[int] = None


class AssetCreate(AssetBase):
    pass


class AssetUpdate(CamelModel):
    name: Optional[str] = None
    category_id: Optional[int] = None
    serial_number: Optional[str] = None
    acquisition_date: Optional[datetime] = None
    acquisition_cost: Optional[float] = None
    condition: Optional[str] = None
    location: Optional[str] = None
    is_shared: Optional[bool] = None
    status: Optional[str] = None
    department_id: Optional[int] = None


class AllocationBrief(CamelModel):
    id: int
    asset_id: int
    employee_id: int
    department_id: Optional[int] = None
    expected_return_date: Optional[datetime] = None
    actual_return_date: Optional[datetime] = None
    status: str
    condition_check: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class MaintenanceBrief(CamelModel):
    id: int
    asset_id: int
    requester_id: int
    description: str
    priority: str
    photo: Optional[str] = None
    status: str
    assigned_to_id: Optional[int] = None
    resolution_note: Optional[str] = None
    approved_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class AssetOut(CamelModel):
    id: int
    name: str
    tag: str
    serial_number: Optional[str] = None
    category_id: int
    acquisition_date: Optional[datetime] = None
    acquisition_cost: Optional[float] = None
    condition: str
    location: Optional[str] = None
    is_shared: bool
    status: str
    department_id: Optional[int] = None
    photo: Optional[str] = None
    documents: Optional[str] = None
    allocated_to_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    category: Optional[CategoryOut] = None
    department: Optional[DepartmentOut] = None
    allocated_to: Optional[EmployeeOut] = None
    allocations: Optional[List[AllocationBrief]] = None
    maintenance_requests: Optional[List[MaintenanceBrief]] = None


# ---------- Allocation ----------
class AllocationCreate(CamelModel):
    asset_id: int
    employee_id: int
    department_id: Optional[int] = None
    expected_return_date: Optional[datetime] = None


class AllocationUpdate(CamelModel):
    expected_return_date: Optional[datetime] = None
    status: Optional[str] = None


class AllocationReturn(CamelModel):
    condition_check: Optional[str] = None


class AllocationTransferRequest(CamelModel):
    new_employee_id: int
    new_department_id: Optional[int] = None


class AllocationOut(CamelModel):
    id: int
    asset_id: int
    employee_id: int
    department_id: Optional[int] = None
    expected_return_date: Optional[datetime] = None
    actual_return_date: Optional[datetime] = None
    status: str
    condition_check: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    asset: Optional[AssetOut] = None
    employee: Optional[EmployeeOut] = None
    department: Optional[DepartmentOut] = None


# ---------- Booking ----------
class BookingCreate(CamelModel):
    asset_id: int
    start_time: datetime
    end_time: datetime


class BookingUpdate(CamelModel):
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: Optional[str] = None


class BookingOut(CamelModel):
    id: int
    asset_id: int
    employee_id: int
    start_time: datetime
    end_time: datetime
    status: str
    created_at: datetime
    updated_at: datetime
    asset: Optional[AssetOut] = None
    employee: Optional[EmployeeOut] = None


# ---------- Maintenance ----------
class MaintenanceCreate(CamelModel):
    asset_id: int
    description: str
    priority: Optional[str] = "Medium"
    photo: Optional[str] = None


class MaintenanceUpdate(CamelModel):
    description: Optional[str] = None
    priority: Optional[str] = None
    photo: Optional[str] = None


class MaintenanceAssign(CamelModel):
    technician_id: int


class MaintenanceResolve(CamelModel):
    resolution_note: Optional[str] = None


class MaintenanceOut(CamelModel):
    id: int
    asset_id: int
    requester_id: int
    description: str
    priority: str
    photo: Optional[str] = None
    status: str
    assigned_to_id: Optional[int] = None
    resolution_note: Optional[str] = None
    approved_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    asset: Optional[AssetOut] = None
    requester: Optional[EmployeeOut] = None
    assigned_to: Optional[EmployeeOut] = None


# ---------- Audit ----------
class AuditCycleCreate(CamelModel):
    name: str
    department_id: Optional[int] = None
    location: Optional[str] = None
    start_date: datetime
    end_date: datetime


class AuditAssignAuditor(CamelModel):
    auditor_id: int


class AuditItemCreate(CamelModel):
    asset_id: int
    status: str
    note: Optional[str] = None


class AuditItemOut(CamelModel):
    id: int
    audit_assignment_id: int
    asset_id: int
    status: str
    note: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    asset: Optional[AssetOut] = None


class AuditAssignmentOut(CamelModel):
    id: int
    audit_cycle_id: int
    auditor_id: int
    created_at: datetime
    updated_at: datetime
    auditor: Optional[EmployeeOut] = None
    audit_items: Optional[List[AuditItemOut]] = None


class AuditCycleOut(CamelModel):
    id: int
    name: str
    department_id: Optional[int] = None
    location: Optional[str] = None
    start_date: datetime
    end_date: datetime
    status: str
    discrepancy_report: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    department: Optional[DepartmentOut] = None
    assignments: Optional[List[AuditAssignmentOut]] = None


# ---------- Notification ----------
class NotificationOut(CamelModel):
    id: int
    employee_id: int
    message: str
    type: str
    read: bool
    link: Optional[str] = None
    created_at: datetime


# ---------- Activity ----------
class ActivityOut(CamelModel):
    id: int
    message: str
    time: datetime
