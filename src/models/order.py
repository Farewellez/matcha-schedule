# src/models/order.py
from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime

@dataclass
class OrderItem:
    order_item_id: int 
    order_id: int
    product_id: int
    quantity: int

    product_name: Optional[str] = None

@dataclass
class Order:
    order_id: int
    customer_id: int
    order_timestamp: datetime
    deadline: datetime
    total_price: float

    status_id: int
    total_quantity: int
    status_name: str 

    priority_score: float = 0.0
    items: List[OrderItem] = field(default_factory=list) 

    def calculate_priority_score(self, W_DEADLINE: float, W_QUANTITY: float, STOCK_BONUS: float, current_stock_alert: bool = False):
        
        time_remaining_seconds = (self.deadline - datetime.now()).total_seconds()
        
        time_factor = 1.0 / max(1.0, time_remaining_seconds)
        
        score_deadline = W_DEADLINE * time_factor
        score_quantity = W_QUANTITY * self.total_quantity
        score_stock = STOCK_BONUS if current_stock_alert else 0
        
        self.priority_score = score_deadline + score_quantity + score_stock

    def __lt__(self, other):
        return self.priority_score < other.priority_score
    
# if __name__ == "__main__":
#     from datetime import datetime, timedelta
    
#     # === KONFIGURASI PENGUJIAN ===
#     W_DEADLINE_TEST = 500000.0
#     W_QUANTITY_TEST = 1.0
#     STOCK_BONUS_TEST = 100.0 
    
#     # 1. Order ID 1: DEADLINE JAUH (Low Urgency)
#     print("--- 🧪 Menguji Order ID 1: DEADLINE JAUH ---")
#     deadline_jauh = datetime.now() + timedelta(days=3) # Deadline 3 hari dari sekarang
    
#     order_1 = Order(
#         order_id=1,
#         customer_id=101,
#         order_timestamp=datetime.now(),
#         deadline=deadline_jauh,
#         total_quantity=10,
#         total_price=100.0,
#         status_id=1,
#         status_name="Menunggu",
#         # priority_score dan items diisi otomatis
#     )
    
#     order_1.calculate_priority_score(
#         W_DEADLINE=W_DEADLINE_TEST,
#         W_QUANTITY=W_QUANTITY_TEST,
#         STOCK_BONUS=STOCK_BONUS_TEST,
#         current_stock_alert=False # Tidak ada Stock Alert
#     )
    
#     print(f"Deadline: {order_1.deadline.strftime('%Y-%m-%d %H:%M:%S')}")
#     print(f"Kuantitas: {order_1.total_quantity}")
#     print(f"Skor Prioritas Order 1 (Tanpa Alert): {order_1.priority_score:.4f}\n")
    
    
#     # 2. Order ID 2: DEADLINE MEPEPT (High Urgency)
#     print("--- 🧪 Menguji Order ID 2: DEADLINE MEPEPT ---")
#     deadline_mepet = datetime.now() + timedelta(hours=1) # Deadline 1 jam dari sekarang
    
#     order_2 = Order(
#         order_id=2,
#         customer_id=102,
#         order_timestamp=datetime.now(),
#         deadline=deadline_mepet,
#         total_quantity=5, # Kuantitas lebih kecil dari Order 1
#         total_price=50.0,
#         status_id=1,
#         status_name="Menunggu",
#     )
    
#     order_2.calculate_priority_score(
#         W_DEADLINE=W_DEADLINE_TEST,
#         W_QUANTITY=W_QUANTITY_TEST,
#         STOCK_BONUS=STOCK_BONUS_TEST,
#         current_stock_alert=False
#     )
    
#     print(f"Deadline: {order_2.deadline.strftime('%Y-%m-%d %H:%M:%S')}")
#     print(f"Kuantitas: {order_2.total_quantity}")
#     print(f"Skor Prioritas Order 2 (Tanpa Alert): {order_2.priority_score:.4f}\n")


#     # 3. Order ID 3: DEADLINE MEPEPT + STOCK ALERT (Highest Urgency)
#     print("--- 🧪 Menguji Order ID 3: DEADLINE MEPEPT + STOCK ALERT ---")
    
#     # Kita gunakan Order 2 lagi, tapi dengan Stock Alert
#     order_3 = order_2 
    
#     order_3.calculate_priority_score(
#         W_DEADLINE=W_DEADLINE_TEST,
#         W_QUANTITY=W_QUANTITY_TEST,
#         STOCK_BONUS=STOCK_BONUS_TEST,
#         current_stock_alert=True # Ada Stock Alert
#     )
    
#     print(f"Skor Prioritas Order 3 (DENGAN Alert): {order_3.priority_score:.4f}")
#     print(f"Skor Order 3 HARUS lebih besar dari Skor Order 2.")
    
#     # === HASIL PERBANDINGAN ===
#     print("\n=============================================")
#     print("HASIL PERBANDINGAN SKOR (Harusnya: Order 2 > Order 1)")
#     print(f"Skor Order 1: {order_1.priority_score:.4f}")
#     print(f"Skor Order 2: {order_2.priority_score:.4f}")
#     print(f"Skor Order 3: {order_3.priority_score:.4f}")
#     print("=============================================")