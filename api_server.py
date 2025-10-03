# file: api_server.py

import asyncio
from fastapi import FastAPI
from typing import List, Dict
from pydantic import BaseModel

# BARU: Impor CORSMiddleware
from fastapi.middleware.cors import CORSMiddleware

# Impor kelas-kelas inti dari simulasi kita
from simulation_core import Environment, Agent

# --- (Definisi Pydantic Model tidak berubah) ---
class AgentState(BaseModel):
    name: str
    location: str
    status: str

class SimulationState(BaseModel):
    simulation_time: str
    agents: List[AgentState]

# 1. Inisialisasi Aplikasi FastAPI
app = FastAPI(
    title="Generative Agents Simulation API",
    description="API untuk mengontrol dan melihat status simulasi agen generatif.",
    version="1.0.0"
)

# --- KONFIGURASI CORS ---
# BARU: Tambahkan blok kode ini. Ini adalah bagian terpenting.
origins = [
    "*"  # Memperbolehkan semua origin. Untuk development ini tidak masalah.
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Memperbolehkan semua metode (GET, POST, dll)
    allow_headers=["*"], # Memperbolehkan semua header
)
# --- AKHIR DARI KONFIGURASI CORS ---


# 2. Setup Simulasi (Tidak ada perubahan)
print("--- MEMPERSIAPKAN SIMULASI ---")
sim_environment = Environment(start_time_str="08:00")
john = Agent(name="John", description="Seorang pandai besi yang rajin.", location="Rumah")
jane = Agent(name="Jane", description="Seorang seniman yang suka berjalan-jalan di taman.", location="Rumah")
sim_environment.add_agent(john)
sim_environment.add_agent(jane)
john.plan_day()
jane.plan_day()
print("--- SIMULASI SIAP ---")


# --- (Sisa file tidak ada perubahan) ---
async def run_simulation_background():
    """Tugas yang berjalan di latar belakang untuk menjalankan simulasi."""
    while True:
        sim_environment.run_step()
        await asyncio.sleep(1)

@app.on_event("startup")
async def startup_event():
    """Saat server FastAPI dimulai, jalankan simulasi di latar belakang."""
    print("Server startup: Memulai loop simulasi di background...")
    asyncio.create_task(run_simulation_background())

@app.get("/state", response_model=SimulationState)
async def get_simulation_state():
    """
    Endpoint untuk mendapatkan status terbaru dari semua agen dalam simulasi.
    """
    agent_states = []
    for agent in sim_environment.agents:
        agent_states.append({
            "name": agent.name,
            "location": agent.location,
            "status": agent.status
        })
    
    return {
        "simulation_time": sim_environment.current_time.strftime("%Y-%m-%d %H:%M"),
        "agents": agent_states
    }

@app.post("/event")
async def add_external_event(event_description: str):
    """Endpoint untuk menyuntikkan event dari luar ke dalam simulasi."""
    print(f"Event eksternal diterima: {event_description}")
    for agent in sim_environment.agents:
        agent.observe(f"Sebuah peristiwa tak terduga terjadi: {event_description}")
    return {"message": "Event successfully added to all agents' memory."}