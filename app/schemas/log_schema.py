from datetime import datetime

from pydantic import BaseModel


class LogCreate(BaseModel):
    timestamp: datetime
    level: str
    service: str
    message: str


class LogResponse(BaseModel):
    id: int
    timestamp: datetime
    level: str
    service: str
    message: str

    class Config:
        from_attributes = True


class LogListResponse(BaseModel):
    total: int
    logs: list[LogResponse]


class BucketAnomalyResponse(BaseModel):
    current_bucket: datetime | None = None
    current_count: int
    historical_bucket_counts: dict[datetime, int]
    average: float
    multiplier: float
    anomaly: bool
    message: str | None = None


class LogSummaryResponse(BaseModel):
    level: str
    count: int

class ServiceLogSummaryResponse(BaseModel):
    service: str
    level: str
    count: int