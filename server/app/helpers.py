from datetime import datetime


def generate_asset_tag(sequence: int) -> str:
    return f"AF-{str(sequence).zfill(4)}"


def log_activity(db, employee_id: int, action: str, details: str, ip: str | None = None):
    from . import models

    log = models.ActivityLog(employee_id=employee_id, action=action, details=details, ip=ip)
    db.add(log)
    db.commit()
    db.refresh(log)
    return log
