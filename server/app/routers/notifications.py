from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..auth import authenticate, get_user_id

router = APIRouter(prefix="/api/notifications", tags=["notifications"], dependencies=[Depends(authenticate)])


@router.get("", response_model=list[schemas.NotificationOut])
def get_notifications(
    request: Request,
    limit: int = 20,
    unreadOnly: bool = False,
    db: Session = Depends(get_db),
):
    query = db.query(models.Notification).filter(models.Notification.employee_id == get_user_id(request))
    if unreadOnly:
        query = query.filter(models.Notification.read == False)  # noqa: E712
    return query.order_by(models.Notification.created_at.desc()).limit(limit).all()


@router.put("/{notification_id}/read")
def mark_as_read(notification_id: int, request: Request, db: Session = Depends(get_db)):
    db.query(models.Notification).filter(
        models.Notification.id == notification_id,
        models.Notification.employee_id == get_user_id(request),
    ).update({"read": True})
    db.commit()
    return {"message": "Notification marked as read"}


@router.put("/read-all")
def mark_all_read(request: Request, db: Session = Depends(get_db)):
    db.query(models.Notification).filter(
        models.Notification.employee_id == get_user_id(request),
        models.Notification.read == False,  # noqa: E712
    ).update({"read": True})
    db.commit()
    return {"message": "All notifications marked as read"}
