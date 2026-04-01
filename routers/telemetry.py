from fastapi import APIRouter, Depends,HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from core.auth import get_current_user
from schemas.telemetry import TelemetryPayload
from services.postTelemetry import postTelemetry
from services.getTelemetryJson import getTelemetryJson
from services.testTelemetry import TEST_TELEMETRY

router = APIRouter()

# GET /telemetry
# Returns:
# {
#   "cpuTemp":          { "current": 72, "pastHour": [{"dateTime": "...", "value": 71.2}, ...], "pastDay": [...] },
#   "batteryTemp":      { "current": 35, "pastHour": [...], "pastDay": [...] },
#   "batteryLevel":     { "current": 88, "pastDay": [...] },
#   "distanceTraveled": { "pastHour": 12, "pastDay": 80, "pastWeek": 400, "pastMonth": 1200, "allTime": 9400 },
#   "solarPower":       { "current": 45, "pastHour": [...], "pastDay": [...], "pastWeek": [...], "allTime": 38.2 },
#   "powerConsumption": { "current": 30, "pastHour": [...], "pastDay": [...], "pastWeek": [...], "allTime": 27.1 },
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
# Expects:
# {
#   "battery_level":    88,
#   "cpu_temp":         72,
#   "battery_temp":     35,
#   "distance_traveled": 5,
#   "solar_power":      45,
#   "power_consumption": 30
# }
@router.post("", status_code=201)
async def post_telemetry(
    payload: TelemetryPayload,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    user_id = user["sub"]
    try:
        await postTelemetry(db, user_id, payload)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"message": "Telemetry recorded"}
