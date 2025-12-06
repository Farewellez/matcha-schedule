# src/models/order.py
from src.config import W_QUANTITY, W_DEADLINE, STOCK_BONUS

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
    total_price: float
    status_id: int

    status_name: str 
    items: List[OrderItem] = field(default_factory=list) 

    priority_score: float = 0.0
    total_quantity: int = field(init=False)

    def __post_init__(self):
        self.total_quantity = sum(item.quantity for item in self.items) # belum paham
    
    def calculate_priority_score(self, current_stock_alert: bool = False):
        time_remaining_seconds = (self.deadline - datetime.datetime.now()).total_seconds()
        # time_to_deadline = (self.deadline - datetime.datetime.now()).total_seconds()
        time_factor = 1.0 / max(1.0, time_remaining_seconds)
        score_deadline = W_DEADLINE * time_factor
        score_quantity = W_QUANTITY * self.total_quantity
        score_stock = STOCK_BONUS if current_stock_alert else 0
        self.priority_score = score_deadline + score_quantity + score_stock

    def __lt__(self, other):
        return self.priority_score < other.priority_score