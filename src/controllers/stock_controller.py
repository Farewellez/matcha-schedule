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
            self.queue.recalculate_all_priorities(current_stock_alert=False) # Pastikan semua order di-reset ke base score
            # print("Semua stok di atas ambang batas. Tidak ada perubahan prioritas.")
            return

        self.queue.recalculate_all_priorities(current_stock_alert=True) # <-- PANGGILAN YANG BENAR
        boost_count = len(self.queue._order_map) # Asumsi semua order di-recalculate dengan alert        
        if boost_count > 0:
            # print(f"⬆️ Prioritas {boost_count} order telah ditingkatkan karena kekurangan stok.")
            pass
            
    def adjust_stock_after_production(self, finished_order: Order):
        """
        Mengurangi stok bahan baku setelah suatu Order selesai diproduksi
        berdasarkan resep nyata (product_ingredients).
        """
        
        # 1. AMBIL DETAIL RESEP DARI DATABASE
        # Kita butuh fungsi baru di client.py: fetch_ingredients_for_order(order_id)
        # Fungsi ini akan mengembalikan list of tuples: [(ing_id, quantity_used), ...]
        
        try:
            is_deducted = self.db_client.deduct_ingredients_for_order(finished_order.order_id)
            
            if is_deducted:
                #  print(f"✅ STOCK: Stok berhasil dikurangi untuk Order ID {finished_order.order_id}.")
                pass
            else:
                 print(f"❌ STOCK: GAGAL mengurangi stok untuk Order ID {finished_order.order_id}. Cek DB Error.")

        except Exception as e:
            print(f"❌ STOCK CONTROLLER ERROR: Gagal memproses pengurangan stok untuk Order ID {finished_order.order_id}. Error: {e}")