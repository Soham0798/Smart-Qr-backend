from fastapi import FastAPI
from . import models
from app.routers import users
from .database import engine
from .routers import auth, buses, bookings
from app.database import SessionLocal
from fastapi.staticfiles import StaticFiles
import os
from fastapi.middleware.cors import CORSMiddleware



app = FastAPI()

# Create tables
models.Base.metadata.create_all(bind=engine)


def seed_data():
    db = SessionLocal()
    if db.query(models.Bus).count() == 0:  # only insert if empty
        buses = [
            models.Bus(bus_number="500D", route="Hebbal Bridge-Kempapura-Lumbini Gardens-Veeranapalya-Manyata Embassy Tech Park-Nagawara Junction-HBR Layout-Kalyan Nagar-Babusapalya-Horamavu Petrol Bunk-Ramurthy Nagar-Tin Factory-Kasturi Nagar Junction-Mahadevapura Cross-EMC2-Dodda Nekkundi-Marathahalli Bridge-Kadubisanahalli-Devarabisanahalli-Ecospace-Bellandur / Bellanduru-Bellandur Petrol Bunk-Junction of Sarjapur Road-Ibbalur-Agara Junction-Depot-25 Gate-HSR BDA Complex-HSR Apartment-Central Silk Board", latitude= 12.9321,
  longitude= 77.7378),
             models.Bus(
                bus_number="KIA-8",
                route="Electronic City-Silk Board-Agara-Marathahalli-KR Puram-Hebbal-Kempegowda International Airport",
                latitude=12.8718,
                longitude=77.6545
            ),
            models.Bus(
                bus_number="KIA-5",
                route="Whitefield-ITPL-Marathahalli-KR Puram-Hebbal-Kempegowda International Airport",
                latitude=12.9717,
                longitude=77.7500
            ),
             models.Bus(
                bus_number="KIA-9",
                route="Banashankari-Jayanagar-Shantinagar-Hebbal-Kempegowda International Airport",
                latitude=12.9279,
                longitude=77.5836
            ),
            models.Bus(
                bus_number="KIA-4",
                route="Hebbal-Mekhri Circle-Majestic-Shivajinagar-Domlur-Marathahalli-Airport",
                latitude=13.0322,
                longitude=77.5901
            ),
            models.Bus(
                bus_number="KIA-7",
                route="BTM Layout-Koramangala-Domlur-Hebbal-Airport",
                latitude=12.9154,
                longitude=77.6096
            ),
            models.Bus(
                bus_number="500C",
                route="Banashankari TTMC-JP Nagar 15th Cross-East End Circle-BTM Layout-Silk Board-HSR Layout BDA Complex-HSR Layout 27th Main-Agara-Marathahalli-Kundalahalli Gate-AECS Layout-Brookefield-Graphite India-ITPL-Hope Farm-Kadugodi",
                latitude=12.9056,
                longitude=77.5946
            ),

            models.Bus(
                bus_number="500K",
                route="Kengeri TTMC-Kengeri Satellite Town-Nayandahalli-Deepanjali Nagar-Banashankari TTMC-JP Nagar-BTM Layout-Silk Board-HSR Layout-Bellandur-Ecospace-Marathahalli-Kundalahalli-Brookefield-ITPL-Hope Farm-Whitefield",
                latitude=12.9549,
                longitude=77.5348
            ),
            models.Bus(
                bus_number="500E",
                route="Banashankari TTMC–Jayanagar 9th Block–East End Circle–BTM Layout–Silk Board Junction–HSR Layout–Agara–Bellandur–Ecospace–Kadubeesanahalli–Marathahalli–Kundalahalli Gate–AECS Layout–Brookefield–Graphite India–ITPL–Hope Farm–Kadugodi",
                latitude=12.9184,
                longitude=77.5731
            ),
        ]
        db.add_all(buses)
        db.commit()
    db.close()

seed_data()

@app.get("/")
def home():
    return {"message": "Bus Booking API is running 🚍"}


app.include_router(auth.router)
app.include_router(buses.router)
app.include_router(bookings.router)
app.include_router(users.router)
qr_dir = os.path.join(os.path.dirname(__file__), "qrs")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)
app.mount("/qrs", StaticFiles(directory="app/qrs"), name="qrs")
print("QR folder mounted at:", os.path.abspath(qr_dir))
