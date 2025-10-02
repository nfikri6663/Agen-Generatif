# Definisi peta lingkungan
MAP = {
    "Rumah": ["Dapur", "Ruang Tamu", "Kamar Tidur", "Teras Depan"],
    "Dapur": ["Rumah"],
    "Ruang Tamu": ["Rumah"],
    "Kamar Tidur": ["Rumah"],
    "Teras Depan": ["Rumah"],
    "Kebun": ["Rumah"],
    "Toko": ["Rumah"]
}

# Daftar lokasi untuk digunakan dalam prompt
LOCATIONS = list(MAP.keys())