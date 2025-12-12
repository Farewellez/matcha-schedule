# src/models/order.py

# ini buat OrderItem class
from dataclasses import dataclass
from typing import Optional

# ini buat Order class
import datetime
from dataclasses import dataclass, field
from typing import List

@dataclass
class OrderItem:
    # ini buat kolom dari tabel order_item (disesuaikan dengan yang ada di database)
    order_item_id: int 
    order_id: int
    product_id: int
    quantity: int

    # product name disini untuk representasi dari hasil join product_id
    product_name: Optional[str] = None

@dataclass
class Order:
    order_id: int
    customer_id: int
    order_timestamp: datetime.datetime
    deadline: datetime.datetime
    total_quantity: int

    total_price: float
    status_id: int
    status_name: str 

    priority_score: float = 0.0
    items: List[OrderItem] = field(default_factory=list) 

    def calculate_priority_score(self, W_DEADLINE: float, W_QUANTITY: float, STOCK_BONUS: float, current_stock_alert: bool = False):
        from datetime import datetime
        
        time_remaining_seconds = (self.deadline - datetime.now()).total_seconds()
        
        # 2. Faktor Waktu (Invers dari waktu tersisa)
        # Menggunakan max(1.0, time_remaining_seconds) untuk menghindari pembagian nol dan lonjakan skor saat waktu sangat mepet
        time_factor = 1.0 / max(1.0, time_remaining_seconds)
        
        score_deadline = W_DEADLINE * time_factor
        score_quantity = W_QUANTITY * self.total_quantity
        score_stock = STOCK_BONUS if current_stock_alert else 0
        
        self.priority_score = score_deadline + score_quantity + score_stock
        # print(f"DEBUG: Order ID {self.order_id} Score: {self.priority_score:.2f} (Deadline: {score_deadline:.2f}, Qty: {score_quantity:.2f})")

    def __lt__(self, other):
        return self.priority_score < other.priority_score