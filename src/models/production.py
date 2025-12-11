# src/models/production.py
from datetime import datetime
from typing import Optional

class ProductionBatch:
    """Mencatat satu entri produksi dari mesin untuk satu order."""
    def __init__(self, production_id: int, order_id: int, machine_id: int, 
                 start_time: datetime, status: str, finish_time: Optional[datetime] = None):
        self.production_id = production_id
        self.order_id = order_id
        self.machine_id = machine_id
        self.start_time = start_time
        self.finish_time = finish_time
        self.status = status

    def __repr__(self):
        return f"Batch(ID: {self.production_id}, Order: {self.order_id}, Machine: {self.machine_id}, Status: {self.status})"