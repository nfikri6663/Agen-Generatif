from agent import Agent 
import random

if __name__ == "__main__":
    toni = Agent(name="Toni", location="Rumah")

    # Daftar kejadian yang mungkin
    all_possible_events = [
        "sedang tidur siang.",
        "bangun dan pergi ke dapur.",
        "membuat secangkir kopi.",
        "duduk di teras belakang dan menikmati kopi.",
        "sedang membaca buku di ruang tamu.",
        "menonton film di ruang tamu.",
        "menyiram tanaman di kebun.",
        "menelepon teman di kamar tidur.",
        "memasak makan siang sederhana di dapur.",
        "mendengarkan musik di teras depan."
    ]

    # Pilih 3 sampai 5 kejadian secara acak
    random_events_count = random.randint(3, 5)
    initial_events = random.sample(all_possible_events, random_events_count)
    
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