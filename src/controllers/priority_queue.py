import heapq
from typing import List
from datetime import datetime
from src.models.order import Order
from src.config import W_DEADLINE, W_QUANTITY, STOCK_BONUS

class ProductionPriorityQueue:
    def __init__(self):
        self.heap = [] # tuple: (-score, timestamp, order_object)
        # Mapping untuk pencarian cepat (order_id -> order object)
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
    
    def get_highest_priority_order(self) -> Order:
        if self.heap:
            neg_score, timestamp, order_id, order = heapq.heappop(self.heap)
            # Hapus dari map saat diproses
            if order_id in self._order_map:
                del self._order_map[order_id]
            return order
        return None

    def recalculate_all_priorities(self, current_stock_alert: bool =False):
        """Memaksa hitung ulang skor prioritas untuk SEMUA Order di Queue dan membangun ulang heap."""
        new_heap = []

        for order in self._order_map.values():
            # 🚨 PERBAIKAN 3: Panggil calculate_priority_score dengan argumen config
            order.calculate_priority_score(
                W_DEADLINE=W_DEADLINE,
                W_QUANTITY=W_QUANTITY,
                STOCK_BONUS=STOCK_BONUS,
                current_stock_alert=current_stock_alert # Asumsi re-calc dasar tanpa stock alert
            ) 

            timestamp_float = order.order_timestamp.timestamp()

            heapq.heappush(new_heap, 
                            (-order.priority_score, 
                             -timestamp_float, 
                             order.order_id, 
                             order))

        self.heap = new_heap
        heapq.heapify(self.heap)