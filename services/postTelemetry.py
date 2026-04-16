from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from models.telemetry import Telemetry
from models.users import Users
from schemas.telemetry import TelemetryEntry
from datetime import datetime

async def postTelemetry(db: AsyncSession, user_id: str, entries: list[TelemetryEntry]):
    result = await db.execute(select(Users).where(Users.id == user_id))
    if result.scalars().first() is None:
        db.add(Users(id=user_id))

    rows = [
        {
            "id": user_id,
            "dateTime": datetime.utcfromtimestamp(entry.timestamp),
            "battery_level": entry.battery_percent,
            "cpu_temp": entry.cpu_temp,
            "distance_traveled": entry.distance_m,
            "net_power": entry.net_power_gain_w,
        }
        for entry in entries
    ]

    stmt = insert(Telemetry).values(rows).on_conflict_do_nothing()
    await db.execute(stmt)
    await db.commit()

