from pydantic import BaseModel

class TelemetryPayload(BaseModel):
    battery_level: int
    cpu_temp: int
    battery_temp: int
    distance_traveled: int
    solar_power: int
    power_consumption: int
