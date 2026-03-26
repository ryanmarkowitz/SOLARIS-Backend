from fastapi import APIRouter

router = APIRouter()

@router.get("")
async def get_telemetry():
    return {"message": "Hello World"}