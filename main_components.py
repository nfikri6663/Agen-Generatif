from datetime import datetime, timedelta
from typing import List, Dict

# Forward declaration untuk type hinting
class Agent:
    pass

class Memory:
    def __init__(self, timestamp: datetime, description: str, importance_score: int):
        self.timestamp = timestamp
        self.description = description
        self.importance = importance_score
        self.recency = 1.0 # Akan di-update setiap saat
        # Embedding akan ditambahkan nanti untuk skor relevansi

    def __repr__(self):
        return f"Memory(t={self.timestamp.strftime('%H:%M')}, importance={self.importance}, desc='{self.description}')"


class MemoryStream:
    """Mengelola semua memori untuk satu agen."""
    def __init__(self, agent: Agent):
        self.agent = agent
        self.memories: List[Memory] = []

    def add_memory(self, description: str):
        """Menambahkan observasi baru ke dalam aliran memori."""
        # Panggil LLM untuk menilai 'importance'
        importance_score = self._rate_importance(description)
        new_memory = Memory(datetime.now(), description, importance_score)
        self.memories.append(new_memory)
        print(f"Agen {self.agent.name} menambahkan memori: {new_memory}")

    def _rate_importance(self, description: str) -> int:
        """Meminta LLM untuk menilai pentingnya sebuah memori."""
        # Implementasi akan dibahas di bagian selanjutnya
        # Untuk sekarang, kita bisa gunakan nilai default
        return 5 # Placeholder

    def retrieve_memories(self, query: str, top_k: int = 3) -> List[Memory]:
        """Mengambil memori paling relevan berdasarkan query."""
        # Implementasi akan menggunakan skor recency, importance, dan relevance
        # Untuk sekarang, kita kembalikan memori terbaru
        return sorted(self.memories, key=lambda m: m.timestamp, reverse=True)[:top_k]


class Agent:
    """Agen otonom dalam simulasi."""
    def __init__(self, name: str, description: str, location: str):
        self.name = name
        self.description = description # "John Doe adalah seorang pandai besi yang ramah"
        self.location = location
        self.status = "Idle" # "Sedang membaca buku", "Memasak sarapan"
        self.memory_stream = MemoryStream(self)
        self.plan: Dict[str, str] = {} # Rencana harian

    def observe(self, observation: str):
        """Agen mengamati sesuatu dan menyimpannya ke memori."""
        self.memory_stream.add_memory(observation)

    def plan_day(self):
        """Membuat rencana harian menggunakan LLM."""
        pass # Akan diimplementasikan

    def reflect(self):
        """Melakukan refleksi untuk menghasilkan wawasan baru."""
        pass # Akan diimplementasikan

    def act(self):
        """Memutuskan dan melakukan tindakan selanjutnya."""
        pass # Akan diimplementasikan

class Environment:
    """Dunia simulasi."""
    def __init__(self):
        self.current_time = datetime.now().replace(hour=7, minute=0, second=0)
        self.agents: List[Agent] = []

    def add_agent(self, agent: Agent):
        self.agents.append(agent)

    def get_observations_for(self, agent: Agent) -> str:
        """Menghasilkan string observasi untuk agen tertentu."""
        # Logika untuk menentukan apa yang bisa dilihat/didengar agen
        # Contoh sederhana:
        other_agents = [a for a in self.agents if a != agent and a.location == agent.location]
        if not other_agents:
            return f"{agent.name} tidak melihat siapa-siapa di {agent.location}."
        else:
            names = ", ".join([a.name for a in other_agents])
            return f"{agent.name} melihat {names} di {agent.location}."

    def run_simulation_step(self):
        """Menjalankan satu langkah waktu dalam simulasi."""
        for agent in self.agents:
            # 1. Agen Mengamati
            observation = self.get_observations_for(agent)
            agent.observe(observation)

            # 2. Agen Bertindak (akan diimplementasikan)
            # agent.act()

        self.current_time += timedelta(minutes=1)
        print(f"--- Waktu sekarang: {self.current_time.strftime('%H:%M')} ---")