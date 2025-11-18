from pydantic import BaseModel
from typing import Optional

# --- User ---
class UserCreate(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    class Config:
        orm_mode = True

# --- Bus ---
class BusCreate(BaseModel):
    bus_number: str   # ✅ match model field name
    route: str

class BusOut(BaseModel):
    id: int
    bus_number: str
    route: str
    class Config:
        orm_mode = True

# --- Booking ---
class BookingCreate(BaseModel):
    bus_id: int
    source: str
    destination: str

class BookingOut(BaseModel):
    id: int
    bus_id: int
    source: str
    destination: str
    fare: float
    qr_link: Optional[str] = None
    
    class Config:
        orm_mode = True

