# src/main.py (REVISI)

import sys
import os
import threading # Diperlukan untuk menjalankan Scheduler secara background
import time # Diperlukan untuk sleep
from src.views.auth_view import AuthView
from src.views.admin_view import AdminView
from src.views.customer_view import CustomerView

# --- Tambahan Import untuk Scheduler ---
from .controllers.scheduler import ProductionScheduler
from .config import SCHEDULER_POLLING_INTERVAL, PRODUCTION_MACHINE_COUNT
# ----------------------------------------

# Hapus fungsi hash_password jika sudah ada di AuthController/Utils
# Hapus fungsi initialize_data() karena kita pakai DB!

def main():
    print("\n" + "=" * 50)
    print("  🚀 SISTEM PRODUKSI MATCHA STARTING 🚀")
    print("=" * 50)
    
    # --- INISIALISASI SCHEDULER & DB ---
    # Scheduler diinisialisasi dan terhubung ke DB (TODO 3)
    try:
        scheduler = ProductionScheduler(num_machine=PRODUCTION_MACHINE_COUNT)
        
        # 1. Jalankan Scheduler di Thread terpisah!
        # Scheduler perlu berjalan terus menerus (loop) sementara menu interaktif berjalan.
        scheduler_thread = threading.Thread(
            target=scheduler.start_polling, 
            args=(SCHEDULER_POLLING_INTERVAL,),
            daemon=True # Daemon thread agar program bisa exit
        )
        scheduler_thread.start()
        print(f"✅ Production Scheduler STARTED (Mesin: {PRODUCTION_MACHINE_COUNT}, Interval: {SCHEDULER_POLLING_INTERVAL}s)")
        
    except Exception as e:
        print(f"\n❌ FATAL ERROR: Gagal memulai Scheduler atau Koneksi DB. Error: {e}")
        time.sleep(3)
        return # Keluar dari program
    # ----------------------------------------
    
    print("System ready! (Menu interaktif berjalan di thread utama)\n")
    
    # ⚠️ Data store ini HARUS DIHAPUS atau diganti
    # Karena View/Controller teman Anda menggunakan 'data_store',
    # kita harus me-refactor view/controller itu untuk menggunakan self.db_client!
    data_store = None # Tunjukkan bahwa ini tidak boleh digunakan lagi!
    
    try:
        while True:
            # 2. Authentication
            # Perhatian: AuthView harus di-refactor agar menggunakan scheduler.db_client!
            auth = AuthView(scheduler.db_client) # <-- Ganti data_store menjadi db_client
            role, user_data = auth.run()
            
            if role == 'exit':
                break
            elif role == 'admin' and user_data:
                admin_view = AdminView(scheduler.db_client, user_data) # <-- Ganti data_store
                admin_view.run()
            elif role == 'customer' and user_data:
                customer_view = CustomerView(scheduler.db_client, user_data) # <-- Ganti data_store
                customer_view.run()
    
    except KeyboardInterrupt:
        print("\n\nProgram dihentikan oleh user.")
    except Exception as e:
        print(f"\nError di Main Loop: {e}")
    finally:
        # 3. Cleanup Scheduler Thread
        # Karena kita menggunakan daemon=True, thread akan mati, 
        # tetapi kita tetap harus memanggil close() jika ada KeyboardInterrupt.
        if scheduler.db_client:
            scheduler.db_client.close() # Panggil cleanup yang ada di scheduler
        print("\nTerima kasih telah menggunakan sistem kami!\n")

if __name__ == "__main__":
    # Penting: Tambahkan sys.path jika diperlukan untuk import di atas
    # sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) 
    main()