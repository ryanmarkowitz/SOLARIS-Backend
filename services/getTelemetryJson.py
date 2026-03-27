from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.telemetry import Telemetry
from datetime import datetime, timedelta, timezone

async def getTelemetryJson(db: AsyncSession, user_id: str):
    jsonDic = {}

    now = datetime.now(timezone.utc)

    # Query all telemetry for the user, most recent first
    result = await db.execute(
        select(Telemetry)
        .where(Telemetry.id == user_id)
        .order_by(Telemetry.dateTime.desc())
    )
    rows = result.scalars().all()

    jsonDic["cpuTemp"] = getCpuTemp(rows, now)
    jsonDic["batteryTemp"] = getBatteryTemp(rows, now)
    jsonDic["batteryLevel"] = getBatteryLevel(rows, now)
    jsonDic["distanceTraveled"] = getDistanceTraveled(rows, now)
    jsonDic["solarPower"] = getSolarPower(rows, now)
    jsonDic["powerConsumption"] = getPowerConsumption(rows, now)
    jsonDic["netPower"] = getNetPower(jsonDic["solarPower"], jsonDic["powerConsumption"])

    return jsonDic


def _bucket_average(rows, field: str, bucket_minutes: int):
    # Groups rows into time buckets and returns a list of averages per bucket
    if not rows:
        return []
    buckets = {}
    for row in rows:
        dt = row.dateTime
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        bucket_key = dt.replace(
            minute=(dt.minute // bucket_minutes) * bucket_minutes,
            second=0,
            microsecond=0
        )
        buckets.setdefault(bucket_key, []).append(getattr(row, field))
    return [
        {"dateTime": (bucket_key + timedelta(minutes=bucket_minutes)).isoformat(), "value": sum(vals) / len(vals)}
        for bucket_key, vals in sorted(buckets.items())
    ]


def getCpuTemp(rows: list, now: datetime):
    # Returns current temp, list of 5-min bucket averages for past hour,
    # and list of 1-hour bucket averages for past 24 hours
    cpuTempDic = {}

    one_hour_ago = now - timedelta(hours=1)
    one_day_ago = now - timedelta(hours=24)

    cpuTempDic["current"] = rows[0].cpu_temp if rows else None

    past_hour_rows = [r for r in rows if r.dateTime >= one_hour_ago]
    cpuTempDic["pastHour"] = _bucket_average(past_hour_rows, field="cpu_temp", bucket_minutes=5)

    past_day_rows = [r for r in rows if r.dateTime >= one_day_ago]
    cpuTempDic["pastDay"] = _bucket_average(past_day_rows, field="cpu_temp", bucket_minutes=60)

    return cpuTempDic


def getBatteryTemp(rows: list, now: datetime):
    # Returns current battery temp, list of 5-min bucket averages for past hour,
    # and list of 1-hour bucket averages for past 24 hours
    batteryTempDic = {}

    one_hour_ago = now - timedelta(hours=1)
    one_day_ago = now - timedelta(hours=24)

    batteryTempDic["current"] = rows[0].battery_temp if rows else None

    past_hour_rows = [r for r in rows if r.dateTime >= one_hour_ago]
    batteryTempDic["pastHour"] = _bucket_average(past_hour_rows, field="battery_temp", bucket_minutes=5)

    past_day_rows = [r for r in rows if r.dateTime >= one_day_ago]
    batteryTempDic["pastDay"] = _bucket_average(past_day_rows, field="battery_temp", bucket_minutes=60)

    return batteryTempDic


def getBatteryLevel(rows: list, now: datetime):
    # Returns current battery level and list of 1-hour bucket averages for past 24 hours
    batteryLevelDic = {}

    one_day_ago = now - timedelta(hours=24)

    batteryLevelDic["current"] = rows[0].battery_level if rows else None

    past_day_rows = [r for r in rows if r.dateTime >= one_day_ago]
    batteryLevelDic["pastDay"] = _bucket_average(past_day_rows, field="battery_level", bucket_minutes=60)

    return batteryLevelDic


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


def getSolarPower(rows: list, now: datetime):
    # Returns current solar power and bucketed averages for past hour, day, week, and an all-time average
    one_hour_ago = now - timedelta(hours=1)
    one_day_ago = now - timedelta(hours=24)
    one_week_ago = now - timedelta(weeks=1)

    past_hour_rows = [r for r in rows if r.dateTime >= one_hour_ago]
    past_day_rows = [r for r in rows if r.dateTime >= one_day_ago]
    past_week_rows = [r for r in rows if r.dateTime >= one_week_ago]

    all_time_avg = sum(r.solar_power for r in rows) / len(rows) if rows else None

    return {
        "current": rows[0].solar_power if rows else None,
        "pastHour": _bucket_average(past_hour_rows, field="solar_power", bucket_minutes=5),
        "pastDay": _bucket_average(past_day_rows, field="solar_power", bucket_minutes=60),
        "pastWeek": _bucket_average(past_week_rows, field="solar_power", bucket_minutes=1440),
        "allTime": all_time_avg,
    }


def getPowerConsumption(rows: list, now: datetime):
    # Returns current power consumption and bucketed averages for past hour, day, week, and an all-time average
    one_hour_ago = now - timedelta(hours=1)
    one_day_ago = now - timedelta(hours=24)
    one_week_ago = now - timedelta(weeks=1)

    past_hour_rows = [r for r in rows if r.dateTime >= one_hour_ago]
    past_day_rows = [r for r in rows if r.dateTime >= one_day_ago]
    past_week_rows = [r for r in rows if r.dateTime >= one_week_ago]

    all_time_avg = sum(r.power_consumption for r in rows) / len(rows) if rows else None

    return {
        "current": rows[0].power_consumption if rows else None,
        "pastHour": _bucket_average(past_hour_rows, field="power_consumption", bucket_minutes=5),
        "pastDay": _bucket_average(past_day_rows, field="power_consumption", bucket_minutes=60),
        "pastWeek": _bucket_average(past_week_rows, field="power_consumption", bucket_minutes=1440),
        "allTime": all_time_avg,
    }


def getNetPower(solar_dic: dict, consumption_dic: dict):
    # Returns solar_power - power_consumption by diffing the already-computed dicts
    def subtract_lists(solar_list, consumption_list):
        return [
            {"dateTime": s["dateTime"], "value": s["value"] - c["value"]}
            for s, c in zip(solar_list, consumption_list)
        ]

    current = (solar_dic["current"] - consumption_dic["current"]) if solar_dic["current"] is not None and consumption_dic["current"] is not None else None
    all_time = (solar_dic["allTime"] - consumption_dic["allTime"]) if solar_dic["allTime"] is not None and consumption_dic["allTime"] is not None else None

    return {
        "current": current,
        "pastHour": subtract_lists(solar_dic["pastHour"], consumption_dic["pastHour"]),
        "pastDay": subtract_lists(solar_dic["pastDay"], consumption_dic["pastDay"]),
        "pastWeek": subtract_lists(solar_dic["pastWeek"], consumption_dic["pastWeek"]),
        "allTime": all_time,
    }
