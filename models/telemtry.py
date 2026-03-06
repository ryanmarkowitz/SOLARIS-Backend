from sqlalchemy import Column, DateTime,String, SmallInteger, ForeignKey
from core.database import Base

class Telemetry(Base):
    __tablename__ = "telemetry"

    id = Column(String, ForeignKey("users.clerk_id", ondelete="CASCADE"), primary_key=True)
    dateTime = Column(DateTime, primary_key=True)
    battery_level = Column(SmallInteger)
    cpu_temp = Column(SmallInteger)
    battery_temp = Column(SmallInteger)
    distance_traveled = Column(SmallInteger)
    solar_power = Column(SmallInteger)
    power_consumption = Column(SmallInteger)

