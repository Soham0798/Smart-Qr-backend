from sqlalchemy.orm import Session
from passlib.hash import bcrypt
from . import models, schemas
import math

# 🔍 Get user by username
def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

# ➕ Create user
def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = bcrypt.hash(user.password)
    db_user = models.User(username=user.username, password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# 🔍 Get all buses
def get_all_buses(db: Session):
    return db.query(models.Bus).all()


# 🔍 Get bus by number
def get_bus_by_number(db: Session, number: str):
    return db.query(models.Bus).filter(models.Bus.bus_number == number).first()

# ➕ Create bus
def create_bus(db: Session, bus: schemas.BusCreate):
    db_bus = models.Bus(bus_number=bus.bus_number, route=bus.route)
    db.add(db_bus)
    db.commit()
    db.refresh(db_bus)
    return db_bus

def get_bus_by_id(db: Session, bus_id: int):
    return db.query(models.Bus).filter(models.Bus.id == bus_id).first()


# ➕ Create booking
def create_booking(
    db: Session,
    booking: schemas.BookingCreate,
    user_id: int,
    fare: float,
    qr_link: str = None
):
    db_booking = models.Booking(
        user_id=user_id,
        bus_id=booking.bus_id,
        source=booking.source,
        destination=booking.destination,
        fare=fare,
        qr_link=qr_link
    )
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    return db_booking



def get_nearby_buses(db, lat: float, lon: float, radius_km: float = 6.0):
    """Return buses within a given radius (in km) from a given lat/lon"""
    def haversine(lat1, lon1, lat2, lon2):
        R = 6371  # Earth radius in km
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)
        a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    all_buses = get_all_buses(db)
    nearby = []
    for bus in all_buses:
        # match these to your actual DB column names
        bus_lat = bus.latitude
        bus_lon = bus.longitude

        if bus_lat is not None and bus_lon is not None:
            if haversine(lat, lon, bus_lat, bus_lon) <= radius_km:
                nearby.append({
                    "id": bus.id,
                    "bus_number": bus.bus_number,
                    "latitude": bus_lat,
                    "longitude": bus_lon,
                })
    return nearby

