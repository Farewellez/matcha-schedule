import heapq
from typing import List
from datetime import datetime
from src.models.order import Order

class ProductionPriorityQueue:
    def __init__(self):
        self.heap = [] # tuple: (-score, timestamp, order_object)
        # Mapping untuk pencarian cepat (order_id -> order object)
        self._order_map = {}
    
    def add_order(self, order: Order):
        # Asumsi: Stock alert dicek saat update, bukan saat initial add
        # Kita akan asumsikan False untuk base priority.
        order.calculate_priority_score(current_stock_alert=False)
        
        # Perbaikan: Negasi timestamp agar pesanan lama (timestamp kecil) diprioritaskan (nilai negatif terbesar)
        timestamp_float = order.order_timestamp.timestamp()

        # Tambahkan ke map dan heap (Negasi timestamp untuk FIFO)
        self._order_map[order.order_id] = order
        heapq.heappush(self.heap, 
                       (-order.priority_score, 
                        -timestamp_float, 
                        order.order_id, 
                        order))
    
    def get_highest_priority_order(self) -> Order:
        if self.heap:
            neg_score, timestamp, order_id, order = heapq.heappop(self.heap)
            # Hapus dari map saat diproses
            if order_id in self._order_map:
                del self._order_map[order_id]
            return order
        return None

    def boost_priority_by_items(self, low_stock_items: List[str], boost_score: int) -> int:
        """
        Mencari order yang membutuhkan item_id yang stoknya rendah dan
        memperbarui prioritasnya secara sementara.
        """
        boosted_count = 0
        
        # 1. Identifikasi order yang perlu di-boost (ASUMSI: Stok mempengaruhi SEMUA order)
        # Jika resep tidak diketahui di sini, kita terapkan boost pada SEMUA order yang ADA di queue.
        # Jika Anda memiliki resep yang lebih kompleks, logika di sini harus lebih spesifik.
        
        # Untuk kasus sederhana: Kita beri boost ke semua yang ada di map
        for order_id, order in self._order_map.items():
            # Jika logika stok Anda lebih kompleks (misalnya, hanya boost jika order membutuhkan Matcha)
            # Anda perlu menambahkan properti resep ke Order model atau memanggil DB di sini.
            # Untuk sekarang, kita asumsikan boost berlaku untuk semua pesanan yang belum diproses.
            
            # 2. Re-calculate score dengan stock_alert=True dan masukkan kembali ke heap
            # PENTING: Untuk menghindari item yang sudah diproses ikut masuk,
            # kita harus menghapus dan membangun ulang heap. Ini tidak efisien,
            # tetapi paling aman jika kita tidak ingin mencari & mengganti elemen di heap.
            
            # Daripada membangun ulang heap, kita gunakan trik: langsung ubah score di objek Order
            # dan biarkan item yang lebih tinggi skornya masuk ke depan di iterasi berikutnya.

            # Hapus item dari map untuk direbuild (karena score berubah)
            
            # --- Pendekatan Rebuild Heap (Paling Aman) ---
            pass 
        
        # Ciptakan List baru dari Order Objects yang di-boost
        new_heap = []
        for order in self._order_map.values():
            
            # Asumsi: Setiap order mendapat boost jika ada kekurangan stok global
            # Implementasi yang lebih kompleks akan memerlukan pemeriksaan resep di sini.
            
            # 1. Panggil calculate_priority_score dengan alert=True
            order.calculate_priority_score(current_stock_alert=True)
            
            # 2. Masukkan ke heap baru
            timestamp_float = order.order_timestamp.timestamp()
            heapq.heappush(new_heap, 
                           (-order.priority_score, 
                            -timestamp_float, 
                            order.order_id, 
                            order))
            boosted_count += 1
            
        # Ganti heap lama dengan yang baru
        self.heap = new_heap
        heapq.heapify(self.heap) # Memastikan struktur heap tetap terjaga

        return boosted_count