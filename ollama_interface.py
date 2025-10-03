import ollama
import re
from typing import List

def get_importance_score(observation_text: str) -> int:
    """
    Menggunakan Ollama dengan model gemma3:4b untuk menilai pentingnya observasi.
    """
    prompt = f"""Anda adalah sebuah AI yang bertugas menilai seberapa penting sebuah peristiwa bagi seseorang dalam skala 1 hingga 10.
    Skala 1 - 10, contohnya:
    1: Peristiwa yang sangat biasa dan mudah dilupakan
    5: Peristiwa yang cukup menarik tapi rutin
    10: Peristiwa yang sangat signifikan dan mengubah hidup

    Tugas: Berikan skor untuk peristiwa di bawah ini. Jawab HANYA dengan SATU ANGKA antara 1 dan 10.

    Peristiwa: "{observation_text}"

    Skor Kepentingan:"""

    try:
        # Memastikan server Ollama berjalan
        response = ollama.generate(
            model='gemma3:4b',
            prompt=prompt,
            options={'temperature': 0.0},
            stream=False
        )
        
        text_response = response['response']
        match = re.search(r'\d+', text_response)
        
        if match:
            score = int(match.group(0))
            return max(1, min(10, score))
        else:
            print(f"Warning: Tidak dapat menemukan angka pada respons LLM. Respons: '{text_response}'. Menggunakan skor default 3.")
            return 3

    except Exception as e:
        print(f"Error saat menghubungi Ollama: {e}. Pastikan server Ollama sedang berjalan. Menggunakan skor default 3.")
        return 3
    
def generate_reflection(memories_text: str) -> str:
    """Menghasilkan wawasan tingkat tinggi dari sekumpulan memori."""
    prompt = f"""Anda adalah sebuah AI yang membantu seseorang merangkum pemikirannya.
    Di bawah ini adalah daftar pengamatan terkini dari seseorang.
    Tugas Anda adalah membuat satu kesimpulan atau wawasan umum tingkat tinggi dari daftar ini dalam satu kalimat singkat.
    Jangan mengulang pengamatan, sintesiskan ide baru.

    Pengamatan Terkini:
    {memories_text}

    Wawasan Tingat Tinggi (satu kalimat):"""

    try:
        response = ollama.generate(
            model='gemma3:4b',
            prompt=prompt,
            options={'temperature': 0.7}, # Sedikit lebih kreatif untuk refleksi
            stream=False
        )
        return response['response'].strip()
    except Exception as e:
        print(f"Error saat menghasilkan refleksi: {e}")
        return "Gagal melakukan refleksi."

def generate_daily_plan(agent_summary: str) -> str:
    """Membuat rencana harian untuk agen berdasarkan identitas dan wawasannya."""
    prompt = f"""{agent_summary}

    Tugas: Buatlah rencana kegiatan yang ringkas untuk hari ini, mulai dari jam 8 pagi hingga 10 malam.
    Buatlah rencana yang masuk akal berdasarkan siapa diri Anda.
    Gunakan format yang sangat ketat: `HH:MM - Aktivitas`. Jangan tambahkan teks lain.

    Contoh:
    08:00 - Memasak dan sarapan.
    09:00 - Bekerja di bengkel menempa pedang.
    12:00 - Makan siang.
    18:00 - Pergi ke kedai untuk makan malam.
    22:00 - Tidur.

    Rencana Anda untuk hari ini:
    """
    try:
        response = ollama.generate(
            model='gemma3:4b',
            prompt=prompt,
            options={'temperature': 0.5},
            stream=False
        )
        return response['response'].strip()
    except Exception as e:
        print(f"Error saat menghasilkan rencana: {e}")
        return "08:00 - Gagal membuat rencana."
    
def decide_next_action(context: str) -> str:
    """Memutuskan tindakan spesifik berikutnya untuk agen."""
    prompt = f"""{context}

    Tugas: Apa satu tindakan fisik dan spesifik yang Anda lakukan SEKARANG?
    Gunakan format yang sangat ketat: `[NAMA LOKASI BARU] :: [DESKRIPSI AKSI SINGKAT]`
    - Ubah NAMA LOKASI BARU hanya jika Anda pindah. Jika tidak, gunakan lokasi saat ini.
    - DESKRIPSI AKSI SINGKAT harus berupa kalimat aktif (misal: "Memalu besi panas", bukan "Sedang memalu").

    Contoh:
    - Bengkel :: Memanaskan sebatang besi di tungku api.
    - Balai Kota :: Berjalan menuju taman.
    - Taman :: Duduk di bangku sambil membaca buku.

    Tindakan Anda sekarang:
    """
    try:
        response = ollama.generate(
            model='gemma3:4b',
            prompt=prompt,
            options={'temperature': 0.5},
            stream=False
        )
        return response['response'].strip()
    except Exception as e:
        print(f"Error saat memutuskan tindakan: {e}")
        return "Lokasi Saat Ini :: Berdiam diri dan berpikir."