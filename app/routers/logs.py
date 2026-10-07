from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models import Log
from app.schemas.log_schema import LogCreate, LogResponse, LogListResponse

from typing import List

router = APIRouter(
    prefix="/logs",
    tags=["Logs"]
)


@router.post("/", response_model=LogResponse)
def create_log(log: LogCreate, db: Session = Depends(get_db)):
    new_log = Log(
        timestamp=log.timestamp,
        level=log.level,
        service=log.service,
        message=log.message
    )

    db.add(new_log)
    db.commit()
    db.refresh(new_log)

    return new_log


@router.post("/bulk", response_model=list[LogResponse])
def create_logs_bulk(
    logs: List[LogCreate],
    db: Session = Depends(get_db)
):
    new_logs = [
        Log(
            timestamp=log.timestamp,
            level=log.level,
            service=log.service,
            message=log.message
        )
        for log in logs
    ]

    db.add_all(new_logs)
    db.commit()

    for log in new_logs:
        db.refresh(log)

    return new_logs


@router.get("/", response_model=LogListResponse)
def get_logs(
    skip: int = 0,
    limit: int = 10,
    level: str | None = None,
    service: str | None = None,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
    db: Session = Depends(get_db)
):
    query = db.query(Log)

    if level:
        query = query.filter(Log.level == level)

    if service:
        query = query.filter(Log.service == service)

    if start_time:
        query = query.filter(Log.timestamp >= start_time)

    if end_time:
        query = query.filter(Log.timestamp <= end_time)

    total = query.count()

    logs = query.order_by(desc(Log.timestamp)).offset(skip).limit(limit).all()

    return {
        "total": total,
        "logs": logs
   }