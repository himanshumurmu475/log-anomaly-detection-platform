from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models import Log

from app.services.anomaly_detector import detect_threshold_anomaly

from app.services.anomaly_detector import (
    detect_moving_average_anomaly,
    detect_threshold_anomaly,
)

from app.services.anomaly_detector import (
    analyze_log_buckets,
    detect_moving_average_anomaly,
    detect_threshold_anomaly,
)

from app.schemas.log_schema import BucketAnomalyResponse
from app.schemas.log_schema import LogSummaryResponse
from app.schemas.log_schema import ServiceLogSummaryResponse


router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"]
)


@router.get("/summary", response_model=list[LogSummaryResponse])
def get_summary(
    start_time: datetime | None = None,
    end_time: datetime | None = None,
    db: Session = Depends(get_db)
):
    query = db.query(Log)

    if start_time:
        query = query.filter(Log.timestamp >= start_time)

    if end_time:
        query = query.filter(Log.timestamp <= end_time)

    result = (
        query.with_entities(Log.level, func.count(Log.id))
        .group_by(Log.level)
        .all()
   )

    return [
        {
            "level": level,
            "count": count
        }
        for level, count in result
    ]


@router.get(
    "/by-service",
    response_model=list[ServiceLogSummaryResponse]
)
def get_logs_by_service(db: Session = Depends(get_db)):
    result = (
        db.query(
            Log.service,
            Log.level,
            func.count(Log.id)
        )
        .group_by(Log.service, Log.level)
        .all()
    )

    return [
        {
            "service": service,
            "level": level,
            "count": count
        }
        for service, level, count in result
    ]



@router.get("/anomaly-check")
def anomaly_check(
    threshold: int = 5,
    service: str | None = None,
    level: str = "ERROR",
    start_time: datetime | None = None,
    end_time: datetime | None = None,
    db: Session = Depends(get_db)
):
    query = db.query(func.count(Log.id)).filter(Log.level == level)

    if service:
        query = query.filter(Log.service == service)

    if start_time:
        query = query.filter(Log.timestamp >= start_time)

    if end_time:
         query = query.filter(Log.timestamp <= end_time) 

    log_count = query.scalar()

    is_anomaly = detect_threshold_anomaly(log_count, threshold)

    return {
        "log_count": log_count,
        "level": level,
        "threshold": threshold,
        "anomaly": is_anomaly,
        "message": (
            f"{level} log count exceeded the threshold"
            if is_anomaly
            else f"{level} log count is within the threshold"
        )
    }


@router.post("/moving-average-test")
def moving_average_test(
    current_value: int,
    historical_values: list[int],
    multiplier: float = 2.0
):

    is_anomaly = detect_moving_average_anomaly(
        current_value,
        historical_values,
        multiplier
    )

    return {
        "current_value": current_value,
        "historical_values": historical_values,
        "multiplier": multiplier,
        "anomaly": is_anomaly
    }


@router.get("/bucket-anomaly", response_model=BucketAnomalyResponse)
def bucket_anomaly(
    level: str = "ERROR",
    service: str | None = None,
    interval_minutes: int = 5,
    multiplier: float = 2.0,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
    db: Session = Depends(get_db)
):
    return analyze_log_buckets(
        db=db,
        level=level,
        service=service,
        interval_minutes=interval_minutes,
        multiplier=multiplier,
        start_time=start_time,
        end_time=end_time
    )


@router.get("/overview")
def anomaly_overview(
    db: Session = Depends(get_db)
):
    total_logs = db.query(func.count(Log.id)).scalar()

    error_count = (
        db.query(func.count(Log.id))
        .filter(Log.level == "ERROR")
        .scalar()
    )

    warning_count = (
        db.query(func.count(Log.id))
        .filter(Log.level == "WARNING")
        .scalar()
    )

    info_count = (
        db.query(func.count(Log.id))
        .filter(Log.level == "INFO")
        .scalar()
    )

    return {
        "total_logs": total_logs,
        "error_count": error_count,
        "warning_count": warning_count,
        "info_count": info_count,
        "error_rate": (
            error_count / total_logs
            if total_logs > 0
            else 0
        )
    }