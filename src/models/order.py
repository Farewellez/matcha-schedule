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
    total_price: float
    status_id: int

    status_name: str # bakal dibuat untuk hasil JOIN dari tabel status
    # cara kerja field diambil dari fitur dataclassess
    # tiap kali ada data yang masuk dalam hal ini adalah order, maka akan dibuat sebuah list baru
    items: List[OrderItem] = field(default_factory=list) 

    priority_score: float = 0.0
    total_quantity: int = field(init=False)

    # method ini digunakan tepat setelah atribut __init__ sudah terinisialisasi. dalam kasus ini otomatis dengan menggunakan dataclass
    # disini __post_init__ mengakses atribut items dan melakukan iterasi terhadap semua elemen di list self.items yang merupakan list dari objek OrderItem
    # untuk tiap objek item, nilai atribut yang diambil adalah quantity. jadi tiap order maka diambil quantity dari order tersebut kemudiam dijumlahkan dan masuk ke total_quantity
    def __post_init__(self):
        self.total_quantity = sum(item.quantity for item in self.items) # belum paham

    def calculate_priority_score(self, current_stock_alert: bool = False):
        time_to_deadline = (self.deadline - datetime.datetime.now()).total_seconds()
        quantity_factor = self.total_quantity
        stock_factor = 50 if current_stock_alert else 0
        self.priority_score = 0.0

    def __lt__(self, other):
        return self.priority_score < other.priority_score