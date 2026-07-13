from pydantic import BaseModel

class TelemetryEntry(BaseModel):
    timestamp: int
    battery_percent: int
    cpu_temp: int
    distance_m: float
    net_power_gain_w: int
