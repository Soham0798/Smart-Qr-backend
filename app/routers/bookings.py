from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import schemas, crud, models
from ..database import SessionLocal
from .auth import get_current_user
import qrcode
import os
from fastapi.responses import FileResponse

router = APIRouter(prefix="/bookings", tags=["Bookings"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def calculate_fare(source: str, destination: str, route: str) -> float:
    stops = route.split("-")
    try:
        i, j = stops.index(source), stops.index(destination)
        if i >= j:
            raise ValueError("Invalid route order")

        # Number of stops travelled (each ~2 km)
        stages = j - i

        # Fare chart mapped to distance stages (1 to 25)
        fare_chart = {
            1: 15, 2: 20, 3: 25, 4: 30, 5: 30,
            6: 35, 7: 35, 8: 40, 9: 40, 10: 40,
            11: 45, 12: 45, 13: 45, 14: 50, 15: 50,
            16: 50, 17: 55, 18: 55, 19: 55, 20: 60,
            21: 60, 22: 60, 23: 65, 24: 65, 25: 65
        }

        # Clamp stages so it doesn’t go beyond table
        stages = min(stages, max(fare_chart.keys()))

        return fare_chart[stages]

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid source/destination")




@router.post("/", response_model=schemas.BookingOut)
def create_booking(
    booking: schemas.BookingCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    # 1️⃣ Find the bus
    bus = db.query(models.Bus).filter(models.Bus.id == booking.bus_id).first()
    if not bus:
        raise HTTPException(status_code=404, detail="Bus not found")

    # 2️⃣ Calculate fare
    fare = calculate_fare(booking.source, booking.destination, bus.route)

    # 3️⃣ Create booking FIRST (no QR yet)
    db_booking = crud.create_booking(db, booking, user.id, fare)
    if bus:
        bus.booked_seats += 1
        db.commit()

    # 4️⃣ Generate QR with the REAL booking ID
    qr_folder = os.path.join(os.getcwd(), "app", "qrs")
    os.makedirs(qr_folder, exist_ok=True)

    frontend_domain = "https://smart-qr-frontend-i8cu-8e0rxo357-soham0798s-projects.vercel.app"
    qr_redirect_url = f"{frontend_domain}/tickets/{db_booking.id}"
    
    # Generate QR image
    qr_img = qrcode.make(qr_redirect_url)
    
    qr_filename = f"ticket_{db_booking.id}.png"
    qr_path = os.path.join(qr_folder, qr_filename)
    qr_img.save(qr_path)
    
    # This is the PNG image served from backend
    backend_domain = "https://smart-qr-backend-production.up.railway.app"
    qr_link = f"{backend_domain}/qrs/{qr_filename}"
    
    db_booking.qr_link = qr_link
    db.commit()
    db.refresh(db_booking)

    # 6️⃣ Return the updated record
    return {
        "id": db_booking.id,
        "bus_id": db_booking.bus_id,
        "source": db_booking.source,
        "destination": db_booking.destination,
        "fare": db_booking.fare,
        "qr_link": db_booking.qr_link
    }

@router.get("/{booking_id}", response_model=schemas.BookingOut)
def get_booking(booking_id: int, db: Session = Depends(get_db)):
    booking = db.query(models.Booking).filter(models.Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking

@router.get("/public/{booking_id}", response_model=schemas.BookingResponse)
def get_public_booking(booking_id: int, db: Session = Depends(get_db)):
    booking = db.query(models.Booking).filter(models.Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Ticket not found")

    return booking

@router.get("/", response_model=list[schemas.BookingOut])
def get_user_bookings(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(models.Booking).filter(models.Booking.user_id == user.id).all()







