# src/controllers/priority_queue
import heapq
from typing import Optional
from src.models.order import Order
from src.config import W_DEADLINE, W_QUANTITY, STOCK_BONUS

class ProductionPriorityQueue:
    def __init__(self):
        self.heap = []
        self._order_map = {}
    
    def add_order(self, order: Order):
        order.calculate_priority_score(
            W_DEADLINE=W_DEADLINE,
            W_QUANTITY=W_QUANTITY,
            STOCK_BONUS=STOCK_BONUS,
            current_stock_alert=False
        )

        timestamp_float = order.order_timestamp.timestamp()

        self._order_map[order.order_id] = order
        heapq.heappush(self.heap, 
                        (-order.priority_score, 
                         -timestamp_float, 
                         order.order_id, 
                         order))
    
    def get_highest_priority_order(self) -> Optional[Order]:
        if self.heap:
            neg_score, timestamp, order_id, order = heapq.heappop(self.heap)
            if order_id in self._order_map:
                del self._order_map[order_id]
            return order
        return None

    def recalculate_all_priorities(self, current_stock_alert: bool =False):
        new_heap = []

        for order in self._order_map.values():
            order.calculate_priority_score(
                W_DEADLINE=W_DEADLINE,
                W_QUANTITY=W_QUANTITY,
                STOCK_BONUS=STOCK_BONUS,
                current_stock_alert=current_stock_alert
            ) 

            timestamp_float = order.order_timestamp.timestamp()

            heapq.heappush(new_heap, 
                            (-order.priority_score, 
                             -timestamp_float, 
                             order.order_id, 
                             order))

        self.heap = new_heap
        heapq.heapify(self.heap)

# # File: ProductionPriorityQueue.py
# # ... (Semua kode class ProductionPriorityQueue di atas) ...

# if __name__ == "__main__":
#     from datetime import datetime, timedelta
    
#     # --- KONFIGURASI PENGUJIAN ---
#     # Gunakan bobot yang sama agar hasil skor terprediksi
#     W_DEADLINE_TEST = 500000.0
#     W_QUANTITY_TEST = 1.0
#     STOCK_BONUS_TEST = 100.0 
    
#     # Ganti import config dengan nilai test jika Anda ingin menguji di luar environment
#     W_DEADLINE = W_DEADLINE_TEST
#     W_QUANTITY = W_QUANTITY_TEST
#     STOCK_BONUS = STOCK_BONUS_TEST
    
#     # --- 1. SETUP ANTRIAN (3 ORDER) ---
#     print("==================================================")
#     print("🧪 FASE 1: MENAMBAHKAN ORDER KE ANTRIAN PRIORITAS")
    
#     pq = ProductionPriorityQueue()
#     current_time = datetime.now()
    
#     # Order A: Priority MENENGAH (Deadline 3 hari)
#     # Kuantitas 10, Skor ~11.9
#     order_a = Order(1, 101, current_time, current_time + timedelta(days=3), 100.0, 10 , 1, 'Waiting')
#     pq.add_order(order_a)

#     # Order B: Priority TERTINGGI (Deadline 1 jam)
#     # Kuantitas 5, Skor ~143.8
#     order_b = Order(2, 102, current_time, current_time + timedelta(hours=1), 50.0, 5,  1, 'Waiting')
#     pq.add_order(order_b)

#     # Order C: Priority TERENDAH (Deadline 5 hari)
#     # Kuantitas 20, Skor ~5.8
#     order_c = Order(3, 103, current_time, current_time + timedelta(days=5), 200.0, 20, 1, 'Waiting')
#     pq.add_order(order_c)
    
#     print(f"Order A Score (3 Hari): {order_a.priority_score:.2f}")
#     print(f"Order B Score (1 Jam): {order_b.priority_score:.2f}")
#     print(f"Order C Score (5 Hari): {order_c.priority_score:.2f}")
#     print(f"Jumlah Order di Map: {len(pq._order_map)}")
#     print(f"Jumlah Order di Heap: {len(pq.heap)}\n")
    
#     # --- 2. UJI GET HIGHEST PRIORITY ORDER ---
#     print("==================================================")
#     print("🧪 FASE 2: MENGAMBIL ORDER PRIORITAS TERTINGGI")

#     # Order yang diambil HARUS Order B (Skor ~143.8)
#     highest_order = pq.get_highest_priority_order()

#     if highest_order and highest_order.order_id == 2:
#         print(f"✅ SUKSES: Order ID {highest_order.order_id} ditarik (Order B).")
#     else:
#         ditarik_id = highest_order.order_id if highest_order is not None else "NONE"
#         print(f"❌ GAGAL: Order ID yang ditarik adalah {ditarik_id} (Seharusnya 2).")

#     print(f"Jumlah Order di Map setelah pop: {len(pq._order_map)} (Harusnya 2)")
#     print(f"Jumlah Order di Heap setelah pop: {len(pq.heap)} (Harusnya 2)\n")

    
#     # --- 3. UJI RECALCULATE ALL PRIORITIES (Dynamic Change) ---
#     print("==================================================")
#     print("🧪 FASE 3: RECALCULATE PRIORITIES (Stock Alert)")
    
#     # Sekarang, kita panggil recalculate_all_priorities dan AKTIFKAN STOCK ALERT.
#     # Order yang tersisa (A dan C) akan mendapat +100 dari STOCK_BONUS.
#     pq.recalculate_all_priorities(current_stock_alert=True) 

#     # Skor yang Diharapkan (Perkiraan):
#     # Order A (11.92 + 100) = ~111.92
#     # Order C (5.8 + 100) = ~105.8
    
#     # Periksa Order A (ID 1) dan C (ID 3) di map (Skor seharusnya diperbarui)
#     print(f"Order A Score (ID 1) setelah Recalc: {pq._order_map[1].priority_score:.2f}")
#     print(f"Order C Score (ID 3) setelah Recalc: {pq._order_map[3].priority_score:.2f}")

#     # Order yang diambil HARUS Order A (111.92 > 105.8)
#     highest_after_recalc = pq.get_highest_priority_order()

#     if highest_after_recalc and highest_after_recalc.order_id == 1:
#         print(f"✅ SUKSES: Order ID {highest_after_recalc.order_id} ditarik (Order A). Prioritas berubah.")
#     else:
#         ditarik_id = highest_after_recalc.order_id if highest_after_recalc is not None else "NONE"
#         print(f"❌ GAGAL: Order ID yang ditarik adalah {ditarik_id} (Seharusnya 1).")

#     print(f"Jumlah Order di Map setelah pop: {len(pq._order_map)} (Harusnya 1)")
#     print("==================================================")
    
#     # Uji return None
#     pq.get_highest_priority_order() # Pop Order C
#     no_order = pq.get_highest_priority_order()

#     if no_order is None:
#         print("✅ SUKSES: Antrian kosong, mengembalikan None.")
#     else:
#         print("❌ GAGAL: Antrian kosong, tapi masih mengembalikan Order.")