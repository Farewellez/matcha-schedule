# src/controllers/scheduler.py
from enum import Enum, auto
from typing import Optional
import datetime
import time
from src.models.order import Order
from src.controllers.priority_queue import ProductionPriorityQueue
from src.api.client import DatabaseClient
from src.config import PRODUCTION_MACHINE_COUNT, SCHEDULER_POLLING_INTERVAL

class MachineStatus(Enum):
    IDLE = auto()
    BUSY = auto()

class ProductionMachine:
    def __init__(self, machine_id:int ,num_machines: int = PRODUCTION_MACHINE_COUNT):
        self.machine_id = machine_id
        self.status = MachineStatus.IDLE
        
        self.current_order: Optional[Order] = None
        self.estimated_finish_time: Optional[datetime.datetime] = None
        self.production_batch_id: Optional[int] = None

    def start_production(self, order: Order, duration_minutes: float, db_client):
        if self.status == MachineStatus.IDLE:
            self.status = MachineStatus.BUSY
            self.current_order = order
            self.estimated_finish_time = datetime.datetime.now() + \
                                         datetime.timedelta(minutes=duration_minutes)
            
            new_id = db_client.start_production_transaction(
                order_id=order.order_id, 
                machine_id=self.machine_id
            )
            
            if new_id is None:
                self.status = MachineStatus.IDLE 
                return False

            self.production_batch_id = new_id
            
            return True
        return False
    
    def check_finish(self, db_client: DatabaseClient) -> Optional[Order]:
        
        if self.status == MachineStatus.BUSY and \
            self.estimated_finish_time is not None and \
            self.current_order is not None and \
            self.production_batch_id is not None and \
            self.estimated_finish_time <= datetime.datetime.now():
            
            finished_order = self.current_order
            batch_id = self.production_batch_id
            
            try:
                success = db_client.finish_production_transaction(
                    order_id=finished_order.order_id, 
                    production_batch_id=batch_id
                )

            except Exception as e:
                print(f"🚨 WARNING: Gagal menjalankan transaksi DB untuk Order ID {finished_order.order_id}. Error: {e}")
                return None
            
            if success:
                print(f"✅ SUCCESS: Machine {self.machine_id} finished Order ID {finished_order.order_id}. Status DB updated.")
                
                self.status = MachineStatus.IDLE
                self.current_order = None
                self.estimated_finish_time = None
                self.production_batch_id = None
                
                return finished_order 
            else:
                print(f"❌ ERROR: Transaksi DB finish_production GAGAL (return False) untuk Order ID {finished_order.order_id}. Mesin tetap BUSY.")
                return None
                
        return None 
    
class ProductionScheduler:
    def __init__(self, num_machine: int = 2):
        self.queue = ProductionPriorityQueue()
        self.machine = [ProductionMachine(i + 1) for i in range(num_machine)]
        self.db_client = DatabaseClient()
        
        from src.controllers.stock_controller import StockController 
        self.stock_controller = StockController(self.db_client, self.queue)
    
    def _fetch_new_orders_from_db(self):
        new_orders_raw = self.db_client.fetch_new_orders()
        
        newly_added_count = 0
        for row in new_orders_raw:

            order = Order(
                order_id=row[0],
                customer_id=row[1],
                order_timestamp=row[2],
                deadline=row[3],
                total_price=row[4],
                status_id=row[5],
                total_quantity=row[6],
                status_name=row[7]
            )
            
            self.queue.add_order(order)
            newly_added_count += 1
            
        if newly_added_count > 0:
            pass

    def estimate_production_duration(self, order: Order) -> float:
        return 0.1
    
    def run_scheduling_cycle(self):
        self._fetch_new_orders_from_db()
        self.stock_controller.check_and_update_all_priorities()

        finished_orders = []
        for machine in self.machine:
            finished_order = machine.check_finish(self.db_client) 
            if finished_order:
                finished_orders.append(finished_order)
                self.stock_controller.adjust_stock_after_production(finished_order)
        
        for machine in self.machine:
            if machine.status == MachineStatus.IDLE:
                
                next_order = self.queue.get_highest_priority_order()
                
                if next_order:
                    duration = self.estimate_production_duration(next_order)
                    machine.start_production(next_order, duration, self.db_client)

    def start_polling(self, interval_seconds: int = SCHEDULER_POLLING_INTERVAL):
        print(f"--- Scheduler STARTED: Mengelola {len(self.machine)} Mesin. Interval: {interval_seconds}s ---")
        try:
            while True:
                self.run_scheduling_cycle()
                time.sleep(interval_seconds)
        except KeyboardInterrupt:
            print("\nScheduler dihentikan.")
            if self.db_client:
                self.db_client.close()
            print("Koneksi DB ditutup dengan aman.")
            