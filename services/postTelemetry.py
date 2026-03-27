from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.telemetry import Telemetry
from models.users import Users
from schemas.telemetry import TelemetryPayload
from datetime import datetime, timezone

async def postTelemetry(db: AsyncSession, user_id: str, payload: TelemetryPayload):
    # Add user to users table if they don't already exist
    result = await db.execute(select(Users).where(Users.id == user_id))
    if result.scalars().first() is None:
        db.add(Users(id=user_id))

    row = Telemetry(
        id=user_id,
        dateTime=datetime.now(timezone.utc),
        battery_level=payload.battery_level,
        cpu_temp=payload.cpu_temp,
        battery_temp=payload.battery_temp,
        distance_traveled=payload.distance_traveled,
        solar_power=payload.solar_power,
        power_consumption=payload.power_consumption,
    )
    db.add(row)
    await db.commit()
