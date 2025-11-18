from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from .. import schemas, crud
from ..database import SessionLocal
from .auth import get_current_user


router = APIRouter(prefix="/buses", tags=["Buses"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

@router.get("/nearby")
def get_nearby_buses(
    lat: float = Query(..., description="User latitude"),
    lon: float = Query(..., description="User longitude"),
    radius: float = Query(5.0, description="Radius in km"),
    db: Session = Depends(get_db)
):
    nearby_buses = crud.get_nearby_buses(db, lat, lon, radius)
    return nearby_buses

@router.get("/", response_model=list[schemas.BusOut])
def get_all_buses(db: Session = Depends(get_db), user=Depends(get_current_user)):
    buses = crud.get_all_buses(db)
    if not buses:
        raise HTTPException(status_code=404, detail="No buses found")
    return buses


@router.post("/", response_model=schemas.BusOut)
def create_bus(bus: schemas.BusCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return crud.create_bus(db, bus)

@router.get("/{bus_number}", response_model=schemas.BusOut)
def get_bus(bus_number: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    db_bus = crud.get_bus_by_number(db, bus_number)
    if not db_bus:
        raise HTTPException(status_code=404, detail="Bus not found")
    return db_bus

@router.get("/id/{bus_id}", response_model=schemas.BusOut)
def get_bus_by_id(bus_id: int, db: Session = Depends(get_db)):
    bus = crud.get_bus_by_id(db, bus_id)
    if not bus:
        raise HTTPException(status_code=404, detail="Bus not found")
    return bus

