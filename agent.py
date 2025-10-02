import datetime
import time 
import re 
from langchain_community.llms import Ollama
from config import MAP, LOCATIONS 

class Agent:
    def __init__(self, name, location):
        self.name = name
        self.location = location
        self.memory_stream = []
        self.llm = Ollama(model="gemma3:4b")

    def __repr__(self):
        return f"Agent(name='{self.name}', location='{self.location}')"

    def add_memory(self, event):
        """Menambahkan kejadian baru ke aliran memori agen."""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        memory_entry = f"[{timestamp}] {self.name} {event}"
        self.memory_stream.append(memory_entry)
        print(f"[{self.name}] mengingat: '{event}'")
    
    def reflect_on_memories(self):
        """Menganalisis memori dan menghasilkan refleksi menggunakan LLM."""
        if not self.memory_stream:
            return f"[{self.name}] Tidak ada memori untuk direfleksikan."

        prompt = (
            f"Anda adalah seorang agen AI yang menganalisis tindakan {self.name}. "
            f"Berdasarkan memori-memori berikut, tuliskan satu atau dua kalimat "
            f"kesimpulan atau refleksi yang paling penting dari hari itu.\n\n"
            f"Memori:\n" + "\n".join(self.memory_stream) + "\n\n"
            f"Refleksi:"
        )
        try:
            reflection = self.llm.invoke(prompt)
            return reflection.strip()
        except Exception as e:
            return f"Terjadi kesalahan saat merefleksi: {e}"

    def create_plan(self, reflection):
        """Membuat rencana harian berdasarkan refleksi terbaru."""
        date_today = datetime.date.today().strftime("%Y-%m-%d")
        
        available_locations = ", ".join(LOCATIONS)

        prompt = (
            f"Anda adalah {self.name}, seorang manusia biasa yang memiliki kegiatan sehari-hari. Hari ini adalah {date_today}. "
            f"Lokasi yang tersedia adalah: {available_locations}. "
            f"Berdasarkan refleksi harian Anda: '{reflection}', susunlah rencana harian. "
            f"Daftarkan 3-5 tugas yang harus Anda lakukan hari ini, termasuk di mana Anda akan melakukannya. "
            f"Contoh: 'Pergi ke Dapur untuk membuat kopi (08:00 - 09:00)'. Gunakan nama lokasi dan format waktu yang persis sama.\n"
            f"Gunakan format daftar bernomor.\n\n"
            f"Rencana:"
        )
        try:
            plan = self.llm.invoke(prompt)
            return plan.strip()
        except Exception as e:
            return f"Terjadi kesalahan saat membuat rencana: {e}"

    def move_to_location(self, destination):
        """Mengubah lokasi agen dan mencatatnya sebagai memori."""
        if destination in MAP.keys():
            print(f"[{self.name}] pindah dari {self.location} ke {destination}.")
            self.location = destination
            self.add_memory(f"berpindah ke lokasi {destination}.")
        else:
            print(f"[{self.name}] tidak tahu cara pergi ke {destination}.")

    def execute_plan(self, plan):
        """Mengeksekusi rencana harian yang dibuat."""
        print(f"\n[{self.name}] memulai rencana hariannya...")
        
        lines = plan.split('\n')
        tasks = []
        for line in lines:
            match_bold = re.search(r'^\s*\d+\.\s*\*\*(.*?)\*\*', line)
            if match_bold:
                tasks.append(match_bold.group(1).split(':')[0].strip())
            else:
                match_plain = re.search(r'^\s*\d+\.\s*(.*)', line)
                if match_plain:
                    tasks.append(match_plain.group(1).split(':')[0].strip())
        
        for task in tasks:
            # --- Logika Akal Sehat yang Anda Sarankan ---
            # Periksa jika tugas membutuhkan langkah tambahan
            if "kopi" in task.lower() or "teh" in task.lower() or "memasak" in task.lower():
                if self.location.lower() != "dapur":
                    self.move_to_location("Dapur")
            elif "belanja" in task.lower():
                if self.location.lower() != "toko":
                    self.move_to_location("Toko")

            # Cari lokasi utama dari tugas
            found_location = None
            for location in MAP.keys():
                if location.lower() in task.lower():
                    found_location = location
                    break

            # Jika lokasi ditemukan dan berbeda, pindah
            if found_location and self.location.lower() != found_location.lower():
                self.move_to_location(found_location)

            clean_task = task.split('(')[0].strip()
            event_description = f"melakukan '{clean_task.lower()}' di {self.location}"
            self.add_memory(event_description)
            time.sleep(1)

        print(f"\n[{self.name}] selesai menjalankan rencananya. Berada di lokasi: {self.location}")


if __name__ == "__main__":
    toni = Agent(name="Toni", location="Rumah")

    initial_events = [
        "sedang tidur siang.",
        "bangun dan pergi ke dapur.",
        "membuat secangkir kopi.",
        "duduk di teras belakang dan menikmati kopi."
    ]
    for event in initial_events:
        toni.add_memory(event)

    print("\n--- Refleksi Harian ---")
    reflection = toni.reflect_on_memories()
    print(reflection)

    print("\n--- Membuat Rencana ---")
    daily_plan = toni.create_plan(reflection)
    print(daily_plan)

    print("\n--- Eksekusi Rencana ---")
    toni.execute_plan(daily_plan)
    
    print("\n--- Memori Akhir Toni ---")
    for memory in toni.memory_stream:
        print(memory)