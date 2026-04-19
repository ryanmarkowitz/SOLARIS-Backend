from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.telemetry import Telemetry
from datetime import datetime, timedelta
_EPOCH = datetime(2000, 1, 1)

async def getTelemetryJson(db: AsyncSession, user_id: str):
    jsonDic = {}

    now = datetime.utcnow()

    # Query all telemetry for the user, most recent first
    result = await db.execute(
        select(Telemetry)
        .where(Telemetry.id == user_id)
        .order_by(Telemetry.dateTime.desc())
    )
    rows = result.scalars().all()

    jsonDic["batteryLevel"] = getBatteryLevel(rows, now)
    jsonDic["cpuTemp"] = getCpuTemp(rows, now)
    jsonDic["distanceTraveled"] = getDistanceTraveled(rows, now)
    jsonDic["netPower"] = getNetPower(rows, now)

    return jsonDic


def _bucket_average(rows, field: str, bucket_minutes: int):
    # Groups rows into time buckets and returns a list of averages per bucket
    if not rows:
        return []
    buckets = {}
    bucket_seconds = bucket_minutes * 60
    for row in rows:
        dt = row.dateTime
        elapsed = (dt - _EPOCH).total_seconds()
        bucket_key = _EPOCH + timedelta(seconds=(elapsed // bucket_seconds) * bucket_seconds)
        buckets.setdefault(bucket_key, []).append(getattr(row, field))
    return [
        {"dateTime": (bucket_key + timedelta(minutes=bucket_minutes)).isoformat() + "Z", "value": sum(vals) / len(vals)}
        for bucket_key, vals in sorted(buckets.items())
    ]


def getBatteryLevel(rows: list, now: datetime):
    # Returns current battery level and list of 1-hour bucket averages for past 24 hours
    one_day_ago = now - timedelta(hours=24)

    past_day_rows = [r for r in rows if r.dateTime >= one_day_ago]

    return {
        "current": rows[0].battery_level if rows else None,
        "pastDay": _bucket_average(past_day_rows, field="battery_level", bucket_minutes=60),
    }


def getCpuTemp(rows: list, now: datetime):
    # Returns current temp, list of 5-min bucket averages for past hour,
    # and list of 1-hour bucket averages for past 24 hours
    one_hour_ago = now - timedelta(hours=1)
    one_day_ago = now - timedelta(hours=24)

    past_hour_rows = [r for r in rows if r.dateTime >= one_hour_ago]
    past_day_rows = [r for r in rows if r.dateTime >= one_day_ago]

    return {
        "current": rows[0].cpu_temp if rows else None,
        "pastHour": _bucket_average(past_hour_rows, field="cpu_temp", bucket_minutes=5),
        "pastDay": _bucket_average(past_day_rows, field="cpu_temp", bucket_minutes=60),
    }


def getDistanceTraveled(rows: list, now: datetime):
    # Returns summed distance_traveled for past hour, day, week, month, and all time
    one_hour_ago = now - timedelta(hours=1)
    one_day_ago = now - timedelta(hours=24)
    one_week_ago = now - timedelta(weeks=1)
    one_month_ago = now - timedelta(days=30)

    return {
        "pastHour": sum(r.distance_traveled for r in rows if r.dateTime >= one_hour_ago),
        "pastDay": sum(r.distance_traveled for r in rows if r.dateTime >= one_day_ago),
        "pastWeek": sum(r.distance_traveled for r in rows if r.dateTime >= one_week_ago),
        "pastMonth": sum(r.distance_traveled for r in rows if r.dateTime >= one_month_ago),
        "allTime": sum(r.distance_traveled for r in rows),
    }


def getNetPower(rows: list, now: datetime):
    # Returns current net power and bucketed averages for past hour, day, week, and an all-time average
    one_hour_ago = now - timedelta(hours=1)
    one_day_ago = now - timedelta(hours=24)
    one_week_ago = now - timedelta(weeks=1)

    past_hour_rows = [r for r in rows if r.dateTime >= one_hour_ago]
    past_day_rows = [r for r in rows if r.dateTime >= one_day_ago]
    past_week_rows = [r for r in rows if r.dateTime >= one_week_ago]

    all_time_avg = sum(r.net_power for r in rows) / len(rows) if rows else None

    return {
        "current": rows[0].net_power if rows else None,
        "pastHour": _bucket_average(past_hour_rows, field="net_power", bucket_minutes=5),
        "pastDay": _bucket_average(past_day_rows, field="net_power", bucket_minutes=60),
        "pastWeek": _bucket_average(past_week_rows, field="net_power", bucket_minutes=1440),
        "allTime": all_time_avg,
    }
