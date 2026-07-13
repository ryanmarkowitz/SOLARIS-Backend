from fastapi import APIRouter, Depends,HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from core.auth import get_current_user
from schemas.telemetry import TelemetryEntry
from services.postTelemetry import postTelemetry
from services.getTelemetryJson import getTelemetryJson
from services.testTelemetry import TEST_TELEMETRY

router = APIRouter()

# GET /telemetry
# Returns:
# {
#   "batteryLevel":     { "current": 88, "pastDay": [...] },
#   "cpuTemp":          { "current": 72, "pastHour": [...], "pastDay": [...] },
#   "distanceTraveled": { "pastHour": 12, "pastDay": 80, "pastWeek": 400, "pastMonth": 1200, "allTime": 9400 },
#   "netPower":         { "current": 15, "pastHour": [...], "pastDay": [...], "pastWeek": [...], "allTime": 11.1 }
# }
@router.get("/test")
async def get_test_telemetry():
    print("\nSuccess\n")
    return TEST_TELEMETRY


@router.get("")
async def get_telemetry(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    user_id = user["sub"]
    try:
        return await getTelemetryJson(db, user_id)
    except Exception as e:
        print("getTelemetryJson error:", e)
        raise HTTPException(status_code=500, detail=str(e))


# POST /telemetry
# Expects a list:
# [
#   { "timestamp": 1743811200, "battery_percent": 85, "cpu_temp": 72, "distance_m": 142.3, "net_power_gain_w": 12 },
#   ...
# ]
@router.post("", status_code=201)
async def post_telemetry(
    payload: list[TelemetryEntry],
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    user_id = user["sub"]
    try:
        await postTelemetry(db, user_id, payload)
    except Exception as e:
        print("POST /telemetry error:", repr(e))
        raise HTTPException(status_code=500, detail=str(e))
    return {"message": "Telemetry recorded"}
