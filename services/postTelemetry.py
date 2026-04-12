from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.telemetry import Telemetry
from models.users import Users
from schemas.telemetry import TelemetryEntry
from datetime import datetime, timezone

async def postTelemetry(db: AsyncSession, user_id: str, entries: list[TelemetryEntry]):
    # Add user to users table if they don't already exist
    result = await db.execute(select(Users).where(Users.id == user_id))
    if result.scalars().first() is None:
        db.add(Users(id=user_id))

    for entry in entries:
        row = Telemetry(
            id=user_id,
            dateTime=datetime.fromtimestamp(entry.timestamp, tz=timezone.utc),
            battery_level=entry.battery_percent,
            cpu_temp=entry.cpu_temp,
            distance_traveled=entry.distance_m,
            net_power=entry.net_power_gain_w,
        )
        db.add(row)

    await db.commit()
