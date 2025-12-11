# src/controllers/scheduler.py

# import modul untuk class ProductionMachine
from enum import Enum, auto
from typing import Optional
import datetime
import time
from src.models.order import Order
from src.controllers.priority_queue import ProductionPriorityQueue

# import module untuk class ProductionScheduler
# from src.controllers.stock_controller
from src.api.client import DatabaseClient
from src.config import PRODUCTION_MACHINE_COUNT, SCHEDULER_POLLING_INTERVAL

class MachineStatus(Enum):
    IDLE = auto()
    BUSY = auto()
    # MAINTENANCE = auto()

class ProductionMachine:
    def __init__(self, machine_id:int ,num_machines: int = PRODUCTION_MACHINE_COUNT):
        self.machine_id = machine_id
        self.status = MachineStatus.IDLE
        
        self.current_order: Optional[Order] = None
        self.estimated_finish_time: Optional[datetime.datetime] = None
        self.production_batch_id: Optional[int] = None

    def start_production(self, order: Order, duration_minutes: float, db_client): # <--- Tambah db_client
        """Menetapkan order ke mesin, menghitung waktu selesai, dan memulai simulasi."""
        if self.status == MachineStatus.IDLE:
            self.status = MachineStatus.BUSY
            self.current_order = order
            self.estimated_finish_time = datetime.datetime.now() + \
                                         datetime.timedelta(minutes=duration_minutes)
            
            # ✅ TODO 1: Panggil DatabaseClient untuk mencatat dimulainya produksi
            new_id = db_client.start_production_transaction(
                order_id=order.order_id, 
                machine_id=self.machine_id
            )
            
            if new_id is None:
                # Jika transaksi gagal, kembalikan status mesin dan log
                self.status = MachineStatus.IDLE 
                print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] 🛑 [MESIN {self.machine_id}] Gagal mencatat produksi Order ID {order.order_id} ke DB. Dibatalkan.")
                return False

            self.production_batch_id = new_id # Simpan ID batch yang baru dikembalikan DB
            
            print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] [MESIN {self.machine_id}] Mulai produksi Order ID {order.order_id}. Est. Selesai: {self.estimated_finish_time.strftime('%H:%M:%S')}")
            return True
        return False
    
    def check_finish(self, db_client) -> Optional[Order]: # <--- Tambah db_client
        """Memeriksa apakah order di mesin sudah selesai diproses."""
        
        # ... (Logika check finish tetap sama)
        if self.status == MachineStatus.BUSY and \
           self.estimated_finish_time <= datetime.datetime.now():
            
            # Produksi Selesai!
            finished_order = self.current_order
            batch_id = self.production_batch_id # Ambil ID batch sebelum direset
            
            # Reset status mesin
            self.status = MachineStatus.IDLE
            self.current_order = None
            self.estimated_finish_time = None
            self.production_batch_id = None
            
            # ✅ TODO 2: Panggil DatabaseClient & StockController
            
            # 1. Update status di DB (Production Batch & Order)
            success = db_client.finish_production_transaction(
                order_id=finished_order.order_id, 
                production_batch_id=batch_id
            )
            
            # TODO 2a: Kurangi stok bahan baku (Logika ini ada di StockController, akan dikerjakan nanti)
            # stock_controller.adjust_stock_after_production(finished_order)
            
            if success:
                print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] ✅ [MESIN {self.machine_id}] Order ID {finished_order.order_id} SELESAI diproduksi dan DB diupdate.")
            else:
                print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] ⚠️ [MESIN {self.machine_id}] Order ID {finished_order.order_id} SELESAI, TAPI GAGAL update di DB. Perlu pengecekan!")

            return finished_order
        return None

class ProductionScheduler:
    def __init__(self, num_machine: int = 2):
        self.queue = ProductionPriorityQueue()
        self.machine = [ProductionMachine(i + 1) for i in range(num_machine)]
        self.db_client = DatabaseClient()
        

        # ✅ TODO 3: Inisialisasi DatabaseClient dan StockController di sini
        from src.controllers.stock_controller import StockController # Tambah import ini
        self.stock_controller = StockController(self.db_client, self.queue)
    
    def _fetch_new_orders_from_db(self):
        """
        ✅ [TODO 4] Menarik order baru dari DB dan memasukkannya ke Queue.
        Order yang ditarik adalah yang statusnya 'Menunggu Konfirmasi'.
        """
        # print("Mencari Order Baru dari Database...")
        
        # Panggil DatabaseClient untuk mendapatkan data mentah (tuple list)
        new_orders_raw = self.db_client.fetch_new_orders()
        
        newly_added_count = 0
        for row in new_orders_raw:
            # Data dari DB: (order_id, deadline, total_quantity, order_timestamp, status_id, customer_id)
            
            # Konversi data mentah (row) menjadi objek Order
            order = Order(
                order_id=row[0],
                customer_id=row[1],
                order_timestamp=row[2],
                deadline=row[3],
                total_price=row[4],
                status_id=row[5],
                total_quantity=row[6],
                status_name=row[7]
                # Catatan: priority_score akan dihitung di ProductionPriorityQueue.add_order()
            )
            
            # Masukkan objek Order ke Queue. Queue akan menghitung skor prioritasnya
            self.queue.add_order(order)
            newly_added_count += 1
            
        if newly_added_count > 0:
            print(f"✅ {newly_added_count} order baru telah ditambahkan ke antrian.")

    def estimate_production_duration(self, order: Order) -> float:
        return order.total_quantity * 1.0
    
    def run_scheduling_cycle(self):
        """Logika utama yang dijalankan setiap interval."""
        
        # --- FASE 1: Ambil Order Baru & Update Stok (Akan diisi nanti) ---
        self._fetch_new_orders_from_db()
        # ✅ TODO 5: Panggil self.stock_controller.check_and_update_all_priorities()
        self.stock_controller.check_and_update_all_priorities()

        # 2. Cek Mesin Selesai & Post-Production
        finished_orders = []
        for machine in self.machine:
            # Panggil check_finish dan LEWATKAN self.db_client!
            finished_order = machine.check_finish(self.db_client) 
            if finished_order:
                finished_orders.append(finished_order)
                # Di sini StockController akan mengurangi bahan baku
                self.stock_controller.adjust_stock_after_production(finished_order)
        
        # --- FASE 3: Alokasikan Pekerjaan Baru (Mesin IDLE vs Queue) ---
        for machine in self.machine:
            if machine.status == MachineStatus.IDLE:
                
                next_order = self.queue.get_highest_priority_order()
                
                if next_order:
                    duration = self.estimate_production_duration(next_order)
                    
                    # Panggil start_production dan LEWATKAN self.db_client!
                    # Start production akan memanggil DB Client untuk update status order
                    machine.start_production(next_order, duration, self.db_client)
        # print("-" * 30)

    def start_polling(self, interval_seconds: int = SCHEDULER_POLLING_INTERVAL):
        """Memulai loop simulasi yang berjalan terus menerus."""
        print(f"--- Scheduler STARTED: Mengelola {len(self.machine)} Mesin. Interval: {interval_seconds}s ---")
        try:
            while True:
                self.run_scheduling_cycle()
                time.sleep(interval_seconds)
        except KeyboardInterrupt:
            print("\nScheduler dihentikan.")
            # ✅ TODO: Tambahkan logika cleanup/disconnect DB
            if self.db_client:
                self.db_client.close() # Panggil metode close() yang sudah kita definisikan!
            print("Koneksi DB ditutup dengan aman.")
            