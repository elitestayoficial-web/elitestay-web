from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from datetime import datetime
import requests

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- CREDENCIALES ELITESTAY ---
API_TOKEN = "a6c889c03ac265b133e99a349a2f7dcb"
MY_MARKER = "498903"

class Hotel(BaseModel):
    id: str
    nombre: str
    marca: str
    precio: float
    estrellas: int
    co2: float
    eco_label: str
    link_reserva: str
    proveedor: str
    imagen: str

@app.get("/api/search", response_model=List[Hotel])
async def search(destino: str, cin: str, cout: str, lang: str = "es"):
    log_time = datetime.now().strftime('%H:%M:%S')
    
    try:
        # 1. BUSCADOR DE CIUDAD
        city_url = f"https://autocomplete.travelpayouts.com/jravia?q={destino}&locale={lang}"
        city_res = requests.get(city_url).json()
        
        if not city_res:
            return []
            
        city_id = city_res[0].get('id') or city_res[0].get('city_code')
        city_name = city_res[0].get('name', destino)

        # 2. INTENTO DE BÚSQUEDA REAL
        hotel_url = "http://engine.hotellook.com/api/v2/cache.json"
        params = {"locationId": city_id, "checkIn": cin, "checkOut": cout, "currency": "usd", "limit": 10, "token": API_TOKEN}
        
        response = requests.get(hotel_url, params=params, timeout=5)
        
        # SI LA API RESPONDE (200 OK)
        if response.status_code == 200 and response.json():
            data = response.json()
            print(f"[{log_time}] ÉXITO: Datos reales obtenidos para {city_name}")
            return [Hotel(
                id=str(h.get('hotelId')),
                nombre=h.get('hotelName', 'Elite Luxury Hotel'),
                marca="Elite Selection",
                precio=float(h.get('priceAvg', 150)),
                estrellas=int(h.get('stars', 5)),
                co2=round(4.5, 1),
                eco_label="Sostenible",
                link_reserva=f"https://search.hotellook.com/hotels?hotelId={h.get('hotelId')}&checkIn={cin}&checkOut={cout}&marker={MY_MARKER}",
                proveedor="Partner Oficial",
                imagen=f"https://photos.hotelstatic.com/hphotos/{h.get('hotelId')}/1.jpg"
            ) for h in data]

        # 3. SISTEMA DE RESPALDO (SI HAY 404 O TOKEN INACTIVO)
        print(f"[{log_time}] MODO DEMO: El Token aún se está activando. Mostrando hoteles exclusivos.")
        return [
            Hotel(
                id="demo1", nombre=f"Elite Eco Resort {city_name}", marca="Elite Selection",
                precio=299.0, estrellas=5, co2=1.8, eco_label="Gold Certified",
                link_reserva=f"https://search.hotellook.com/?locationId={city_id}&marker={MY_MARKER}", 
                proveedor="Elite Direct", imagen="https://images.unsplash.com/photo-1571003123894-1f0594d2b5d9?auto=format&fit=crop&w=800&q=80"
            ),
            Hotel(
                id="demo2", nombre=f"Sostenible Garden & Spa", marca="Elite Selection",
                precio=185.0, estrellas=4, co2=3.2, eco_label="Eco-Friendly",
                link_reserva=f"https://search.hotellook.com/?locationId={city_id}&marker={MY_MARKER}",
                proveedor="Elite Direct", imagen="https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?auto=format&fit=crop&w=800&q=80"
            )
        ]

    except Exception as e:
        print(f"[{log_time}] ERROR: {e}")
        return []

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)