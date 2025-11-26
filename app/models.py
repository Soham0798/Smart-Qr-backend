from sqlalchemy import Column, Integer, String, ForeignKey, Float, Boolean
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)


class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    bus_id = Column(Integer, ForeignKey("buses.id"))
    source = Column(String)
    destination = Column(String)
    fare = Column(Float)
    qr_link = Column(String, nullable=True)
    active = Column(Boolean, default=True)

    user = relationship("User")
    bus = relationship("Bus")
    
class Bus(Base):
    __tablename__ = "buses"

    id = Column(Integer, primary_key=True, index=True)
    bus_number = Column(String, unique=True, index=True)
    route = Column(String)
    latitude = Column(Float)   # 🆕 Current latitude
    longitude = Column(Float)  # 🆕 Current longitude
    capacity = Column(Integer, default=40)
    booked_seats = Column(Integer, default=0) 

