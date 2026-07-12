from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..auth import authenticate

router = APIRouter(prefix="/api/activity", tags=["activity"], dependencies=[Depends(authenticate)])


def _fetch_recent(limit: int, db: Session):
    logs = (
        db.query(models.ActivityLog)
        .order_by(models.ActivityLog.created_at.desc())
        .limit(limit)
        .all()
    )
    activities = []
    for log in logs:
        name = log.employee.name if log.employee else "System"
        activities.append(
            {
                "id": log.id,
                "message": f"{name} {log.action} {log.details}",
                "time": log.created_at,
            }
        )
    return activities


@router.get("", response_model=list[schemas.ActivityOut])
def get_activity(limit: int = 10, db: Session = Depends(get_db)):
    return _fetch_recent(limit, db)


@router.get("/recent", response_model=list[schemas.ActivityOut])
def get_recent_activity(limit: int = 10, db: Session = Depends(get_db)):
    return _fetch_recent(limit, db)