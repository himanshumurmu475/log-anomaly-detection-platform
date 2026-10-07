from datetime import datetime

from sqlalchemy.orm import Session

from app.models import Log

def detect_threshold_anomaly(value: int, threshold: int) -> bool:
    """
    Returns True if the value exceeds the configured threshold.
    """
    return value > threshold


def calculate_moving_average(values: list[int]) -> float:
    """
    Calculates the average of the provided values.
    """
    if not values:
        return 0.0

    return sum(values) / len(values)


def detect_moving_average_anomaly(
    current_value: int,
    historical_values: list[int],
    multiplier: float = 2.0
) -> bool:
    """
    Detects an anomaly when the current value is
    greater than the historical average multiplied by the multiplier.
    """
    average = calculate_moving_average(historical_values)

    if average == 0:
        return current_value > 0

    return current_value > average * multiplier


def get_time_bucket(timestamp: datetime, interval_minutes: int = 5) -> datetime:
    """
    Converts a timestamp into the beginning of its time interval.
    """

    minute = (timestamp.minute // interval_minutes) * interval_minutes

    return timestamp.replace(
        minute=minute,
        second=0,
        microsecond=0
    )


def count_logs_by_bucket(logs, interval_minutes: int = 5):
    """
    Groups logs into time buckets and counts the logs in each bucket.
    """

    bucket_counts = {}

    for log in logs:
        bucket = get_time_bucket(
            log.timestamp,
            interval_minutes
        )

        bucket_counts[bucket] = bucket_counts.get(bucket, 0) + 1

    return bucket_counts



def get_logs_for_analysis(
    db: Session,
    level: str = "ERROR",
    service: str | None = None,
    start_time: datetime | None = None,
    end_time: datetime | None = None
):
    """
    Retrieves logs from the database for anomaly analysis.
    """

    query = db.query(Log).filter(Log.level == level)

    if service:
        query = query.filter(Log.service == service)

    if start_time:
        query = query.filter(Log.timestamp >= start_time)

    if end_time:
        query = query.filter(Log.timestamp <= end_time)

    return query.order_by(Log.timestamp).all()



def get_log_counts_by_bucket(
    db: Session,
    level: str = "ERROR",
    service: str | None = None,
    interval_minutes: int = 5,
    start_time: datetime | None = None,
    end_time: datetime | None = None
):
    """
    Retrieves logs from the database and groups them
    into time buckets.
    """

    logs = get_logs_for_analysis(
        db=db,
        level=level,
        service=service,
        start_time=start_time,
        end_time=end_time
    )
    

    return count_logs_by_bucket(
        logs,
        interval_minutes
    )


def calculate_bucket_average(bucket_counts) -> float:
    """
    Calculates the average number of logs per time bucket.
    """

    if not bucket_counts:
        return 0.0

    return sum(bucket_counts.values()) / len(bucket_counts)


def detect_bucket_anomaly(
    current_count: int,
    bucket_counts,
    multiplier: float = 2.0
) -> bool:
    """
    Detects an anomaly when the current bucket count
    exceeds the historical average multiplied by the multiplier.
    """

    average = calculate_bucket_average(bucket_counts)

    if average == 0:
        return current_count > 0

    return current_count > average * multiplier




def analyze_log_buckets(
    db: Session,
    level: str = "ERROR",
    service: str | None = None,
    interval_minutes: int = 5,
    multiplier: float = 2.0,
    start_time: datetime | None = None,
    end_time: datetime | None = None
):
    """
    Retrieves logs, groups them into time buckets,
    calculates the historical average, and detects
    whether the latest bucket is anomalous.
    """

    bucket_counts = get_log_counts_by_bucket(
        db=db,
        level=level,
        service=service,
        interval_minutes=interval_minutes,
        start_time=start_time,
        end_time=end_time
    )

    if not bucket_counts:
        return {
            "bucket_counts": {},
            "average": 0.0,
            "current_count": 0,
            "anomaly": False,
            "message": "No log data available"
        }

    sorted_buckets = sorted(bucket_counts.keys())

    current_bucket = sorted_buckets[-1]
    current_count = bucket_counts[current_bucket]

    if len(sorted_buckets) == 1:
        return {
            "current_bucket": current_bucket,
            "current_count": current_count,
            "historical_bucket_counts": {},
            "average": 0.0,
            "multiplier": multiplier,
            "anomaly": False,
            "message": "Not enough historical data to detect an anomaly"
        }

    historical_counts = {
        bucket: count
        for bucket, count in bucket_counts.items()
        if bucket != current_bucket
    }

    average = calculate_bucket_average(historical_counts)

    anomaly = detect_bucket_anomaly(
        current_count=current_count,
        bucket_counts=historical_counts,
        multiplier=multiplier
    )

    return {
        "current_bucket": current_bucket,
        "current_count": current_count,
        "historical_bucket_counts": historical_counts,
        "average": average,
        "multiplier": multiplier,
        "anomaly": anomaly,
        "message": (
            "Anomaly detected: current log count is significantly higher than historical average"
            if anomaly
            else "No anomaly detected"
        )
    }

if __name__ == "__main__":
    from app.database.connection import SessionLocal

    db = SessionLocal()

    result = analyze_log_buckets(db)

    print(result)

    db.close()


