from sqlalchemy import Column, String
from core.database import Base

class Users(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True)