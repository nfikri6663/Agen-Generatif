# file: simulation_core.py

from datetime import datetime, timedelta
from typing import List, Dict
import numpy as np
import time # BARU: Untuk jeda antar step simulasi
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# DIPERBARUI: Impor fungsi terakhir
from ollama_interface import get_importance_score, generate_reflection, generate_daily_plan, decide_next_action

# --- (Tidak ada perubahan pada bagian loading model, get_embedding, Memory, MemoryStream) ---
print("Memuat model embedding...")
embedding_model = SentenceTransformer('all-MiniLM-L6-v2'); print("Model embedding berhasil dimuat.")
def get_embedding(text: str) -> np.ndarray: return embedding_model.encode(text)

class Memory:
    # ... (Sama seperti sebelumnya)
    def __init__(self, timestamp: datetime, description: str, is_reflection: bool = False):
        self.timestamp = timestamp; self.description = description
        self.importance = get_importance_score(description)
        if is_reflection: self.importance = max(self.importance, 8)
        self.last_accessed = timestamp; self.embedding = get_embedding(description)
    def __repr__(self): return f"Memory(t='{self.timestamp.strftime('%H:%M')}', imp={self.importance}, desc='{self.description}')"

class MemoryStream:
    # ... (Sama seperti sebelumnya)
    def __init__(self): self.memories: List[Memory] = []
    def add_memory(self, description: str, is_reflection: bool = False):
        new_memory = Memory(datetime.now(), description, is_reflection)
        self.memories.append(new_memory)
        print(f"    -> {'REFLEKSI' if is_reflection else 'Memori'}: '{new_memory.description}' (imp: {new_memory.importance})")
        return sum(m.importance for m in self.memories[-100:])
    def retrieve_memories(self, current_time: datetime, query: str, top_k: int = 3) -> List[Memory]:
        # (Fungsi ini tidak berubah)
        query_embedding = get_embedding(query)
        all_memory_embeddings = [mem.embedding for mem in self.memories]
        if not all_memory_embeddings: return []
        relevance_scores = cosine_similarity([query_embedding], all_memory_embeddings)[0]
        scored_memories = [];
        for i, memory in enumerate(self.memories):
            recency = max(0, 1 - (current_time - memory.timestamp).total_seconds() / (3600*24))
            relevance = relevance_scores[i]
            combined_score = (1.5 * relevance) + (1.0 * (memory.importance / 10)) + (0.8 * recency)
            scored_memories.append((combined_score, memory))
        scored_memories.sort(key=lambda x: x[0], reverse=True)
        return [memory for score, memory in scored_memories[:top_k]]

# --- PERUBAHAN BESAR PADA KELAS AGENT DAN PENAMBAHAN KELAS ENVIRONMENT ---
class Agent:
    def __init__(self, name: str, description: str, location: str):
        self.name = name
        self.description = description
        self.memory_stream = MemoryStream()
        
        # Atribut Status
        self.location = location
        self.status = "Idle"

        # Atribut Kognisi
        self.daily_plan: Dict[str, str] = {}
        self.cumulative_importance_since_reflection = 0
        self.reflection_threshold = 50

    def observe(self, description: str):
        self.cumulative_importance_since_reflection = self.memory_stream.add_memory(description)
        if self.cumulative_importance_since_reflection >= self.reflection_threshold: self.reflect()

    def reflect(self):
        # ... (Sama seperti sebelumnya)
        print(f"\n[KOGNISI] {self.name} memulai refleksi...")
        self.cumulative_importance_since_reflection = 0
        recent_memories = self.memory_stream.memories[-50:]
        memories_text = "\n".join([f"- {m.description}" for m in recent_memories])
        reflection = generate_reflection(memories_text)
        if reflection and "gagal" not in reflection.lower():
            self.memory_stream.add_memory(reflection, is_reflection=True)

    def plan_day(self):
        # ... (Sama seperti sebelumnya)
        print(f"\n[KOGNISI] {self.name} memulai perencanaan harian...")
        relevant_memories = self.memory_stream.retrieve_memories(datetime.now(), query=f"tujuan hidup {self.name}", top_k=5)
        agent_summary = f"Nama: {self.name}\nDeskripsi: {self.description}\n\nWawasan Penting:\n" + "\n".join([f"- {m.description}" for m in relevant_memories])
        plan_text = generate_daily_plan(agent_summary)
        self.daily_plan = {}
        for line in plan_text.split('\n'):
            if '-' in line:
                try: time_str, activity = line.split('-', 1); self.daily_plan[time_str.strip()] = activity.strip()
                except ValueError: continue
        print(f"  -> Rencana untuk {self.name} dibuat.")

    # BARU: Metode act() untuk menjalankan siklus aksi
    def act(self, env: 'Environment'):
        # 1. Dapatkan konteks waktu dan rencana
        current_time_str = env.current_time.strftime("%H:%M")
        plan_activity = "Tidak ada dalam rencana"
        for plan_time, activity in self.daily_plan.items():
            if plan_time <= current_time_str:
                plan_activity = activity

        # 2. Amati lingkungan
        observation = env.get_observations_for(self)
        self.observe(observation)

        # 3. Ambil memori yang relevan
        query = f"Waktu sekarang {current_time_str}. Rencana: {plan_activity}. Pengamatan: {observation}"
        relevant_memories = self.memory_stream.retrieve_memories(env.current_time, query, top_k=3)
        memories_str = "\n".join([f"- {m.description}" for m in relevant_memories])

        # 4. Bangun prompt konteks penuh untuk LLM
        context = f"""Anda adalah {self.name}. Identitas Anda: {self.description}.
        Lokasi saat ini: {self.location}.
        Waktu: {current_time_str}.
        Status saat ini: {self.status}.
        Rencana Anda untuk saat ini adalah: "{plan_activity}".
        Anda baru saja mengamati: "{observation}".
        Memori yang relevan dengan situasi ini:
        {memories_str}
        """
        # 5. Putuskan tindakan
        action_str = decide_next_action(context)

        # 6. Parse dan eksekusi tindakan
        try:
            new_location, new_status = action_str.split('::', 1)
            self.location = new_location.strip()
            self.status = new_status.strip()
        except ValueError:
            # Jika format salah, jangan pindah lokasi
            self.status = action_str.strip()
        
        print(f"[{current_time_str}] {self.name} @ {self.location} -> {self.status}")

# BARU: Kelas Environment untuk mengelola simulasi
class Environment:
    def __init__(self, start_time_str="08:00"):
        self.start_time = datetime.now().replace(hour=int(start_time_str.split(':')[0]), minute=int(start_time_str.split(':')[1]), second=0)
        self.current_time = self.start_time
        self.agents: List[Agent] = []

    def add_agent(self, agent: Agent):
        self.agents.append(agent)

    def get_observations_for(self, agent: Agent) -> str:
        """Menghasilkan observasi sederhana berdasarkan lokasi."""
        other_agents = [a for a in self.agents if a != agent and a.location == agent.location]
        if not other_agents:
            return f"sendirian di {agent.location}."
        else:
            names = ", ".join([f"{a.name} (status: {a.status})" for a in other_agents])
            return f"melihat {names} di {agent.location}."

    def run_step(self):
        """Menjalankan satu langkah simulasi untuk semua agen."""
        for agent in self.agents:
            agent.act(self)
        self.current_time += timedelta(minutes=1)

# --- CONTOH SIMULASI LENGKAP ---
if __name__ == "__main__":
    # 1. Inisialisasi Lingkungan
    sim_environment = Environment(start_time_str="08:00")

    # 2. Buat Agen
    john = Agent(name="John", description="Seorang pandai besi yang rajin.", location="Rumah")
    jane = Agent(name="Jane", description="Seorang seniman yang suka berjalan-jalan di taman.", location="Rumah")
    
    sim_environment.add_agent(john)
    sim_environment.add_agent(jane)

    # 3. Agen membuat rencana awal hari
    john.plan_day()
    jane.plan_day()
    
    # 4. Jalankan simulasi
    print("\n--- MEMULAI SIMULASI ---")
    # Jalankan selama 2 jam (120 menit)
    for i in range(120):
        sim_environment.run_step()
        time.sleep(1) # Beri jeda 1 detik agar output bisa dibaca

    print("\n--- SIMULASI SELESAI ---")