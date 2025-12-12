import sys
# Pastikan path ke src/ ditambahkan agar modul di dalamnya bisa diimpor
# sys.path.append('matcha-schedule') # Baris ini tidak perlu jika sudah menjalankan dari root

from src.api.client import DatabaseClient 
from src.config import PGHOST, PGDATABASE, PGPASSWORD, PGUSER

# --- PERUBAHAN DI SINI ---
try:
    # 1. Minta input Order ID dari user
    order_id_input = input("Masukkan Order ID yang ingin diubah statusnya ke 'Diproses' (ID 2): ")
    ORDER_ID_TARGET = int(order_id_input)
    NEW_STATUS_ID = 2 # ID untuk 'Diproses'
except ValueError:
    print("Input tidak valid. Harap masukkan angka (Order ID).")
    sys.exit()
# -------------------------

# Koneksi DB
db_client = None # Inisialisasi
try:
    print("DB Connect!")
    db_client = DatabaseClient()
    
    # Panggil fungsi yang sudah kamu buat
    success = db_client.force_order_status(ORDER_ID_TARGET, NEW_STATUS_ID)

    if success:
        print(f"✅ Order ID {ORDER_ID_TARGET} berhasil diubah ke Status ID {NEW_STATUS_ID} (Diproses).")
    else:
        print(f"❌ Order ID {ORDER_ID_TARGET} GAGAL diubah. Cek ID atau koneksi.")

except Exception as e:
    print(f"Koneksi/Eksekusi Error: {e}")

finally:
    if db_client and db_client.conn:
        db_client.conn.close()
        print("Koneksi ditutup")