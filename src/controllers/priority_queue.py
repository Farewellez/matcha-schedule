import heapq
from datetime import datetime
from src.models.order import Order

class ProductionPriorityQueue:
    def __init__(self):
        self.heap = [] # tuple: (-score, timestamp, order_object)
    
    def add_order(self, order: Order):
        order.calculate_priority_score(current_stock_alert=False)
        timestamp_float = order.order_timestamp.timestamp()

        heapq.heappush(self.heap, (-order.priority_score, timestamp_float, order.order_id, order))
    
    def get_highest_priority_order(self) -> Order:
        if self.heap:
            neg_score, timestamp, order_id, order = heapq.heappop(self.heap)
            return order
        return None

    def update_order_priority(self, order_id: int):
        pass