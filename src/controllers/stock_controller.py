# src/controllers/stock_controller.py

from src.api.client import DatabaseClient
from src.controllers.priority_queue import ProductionPriorityQueue 
from src.models.order import Order # Diperlukan untuk pengurangan stok
from typing import List

class StockController:
    def __init__(self, db_client: DatabaseClient, queue: ProductionPriorityQueue):
        self.db_client = db_client
        self.queue = queue
        
        # Konstanta ambang batas (Threshold)
        self.LOW_STOCK_THRESHOLD = 1000 # Contoh: Stok dianggap rendah jika kurang dari 1000 unit
        self.PRIORITY_BOOST_SCORE = 10  # Contoh: Skor yang ditambahkan ke order saat stok rendah

    # --- TODO 5: Logika Prioritas Dinamis ---
    
    def check_and_update_all_priorities(self):
        """
        [TODO 5] Memeriksa semua stok bahan baku dan meningkatkan prioritas order 
        yang membutuhkan bahan yang kritis (stok rendah).
        """
        # 1. Ambil status stok dari DB
        # ASUMSI: Ada tabel 'inventory' dengan kolom: item_name, current_stock
        low_stock_items = self.db_client.fetch_low_stock_items(self.LOW_STOCK_THRESHOLD)
        
        if not low_stock_items:
            # print("Semua stok di atas ambang batas. Tidak ada perubahan prioritas.")
            return

        print(f"⚠️ Stok rendah terdeteksi pada item: {', '.join(low_stock_items)}")
        
        # 2. Tingkatkan prioritas order yang membutuhkan item tersebut
        boost_count = self.queue.boost_priority_by_items(low_stock_items, self.PRIORITY_BOOST_SCORE)
        
        if boost_count > 0:
            print(f"⬆️ Prioritas {boost_count} order telah ditingkatkan karena kekurangan stok.")
            
    # --- Mendukung TODO 2: Logika Pengurangan Stok ---
    
    def adjust_stock_after_production(self, finished_order: Order):
        """
        Mengurangi stok bahan baku setelah suatu Order selesai diproduksi.
        Ini dipanggil oleh Scheduler setelah check_finish().
        """
        # ASUMSI: Kita tahu resep (bahan baku yang dibutuhkan) untuk Order ini.
        # Untuk penyederhanaan, kita asumsikan semua produk menggunakan 'Matcha Powder'
        # dan 'Susu' berdasarkan total_quantity.
        
        quantity = finished_order.total_quantity
        
        # 1. Hitung Pengurangan (Contoh sederhana)
        required_matcha = quantity * 10 # Misalnya 10g per unit
        required_milk = quantity * 20  # Misalnya 20ml per unit
        
        # 2. Panggil DatabaseClient untuk mengurangi stok (ini juga harus transaksional)
        self.db_client.adjust_inventory_transaction(
            item_changes=[
                ("Matcha Powder", required_matcha),
                ("Susu", required_milk)
            ]
        )
        print(f"⬇️ Stok dikurangi untuk Order ID {finished_order.order_id}. Total {quantity} unit.")