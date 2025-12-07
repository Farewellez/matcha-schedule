# src/controllers/scheduler.py

# import modul untuk class ProductionMachine
from enum import Enum, auto
from typing import Optional
import datetime
import time
from src.models.order import Order
from src.controllers.priority_queue import ProductionPriorityQueue

# import module untuk class ProductionScheduler
# from src.controllers.stock_controller
# from src.api.client
# from src.config

class MachineStatus(Enum):
    IDLE = auto()
    BUSY = auto()
    # MAINTENANCE = auto()

class ProductionMachine:
    def __init__(self, machine_id: int):
        self.machine_id = machine_id
        self.status = MachineStatus.IDLE
        self.current_order: Optional[Order] = None
        self.estimated_finish_time: Optional[datetime.datetime] = None
        self.production_batch_id: Optional[int] = None

    def start_production(self, order: Order, duration_minutes: float):
        if self.status == MachineStatus.IDLE:
            self.status = MachineStatus.BUSY
            self.current_order = order
            self.estimated_finish_time = datetime.datetime.now() + \
                                         datetime.timedelta(minutes=duration_minutes)
        
        # TOD0 1: Panggil DatabaseClient untuk:
        #   a. Update status order di DB ke 'Diproses'
        #   b. INSERT record baru di tabel 'production_batch'
        #   c. Simpan ID yang dikembalikkan: self.production_batch_id = new_id 
    
    def check_finish(self) -> Optional[Order]:
        if self.status == MachineStatus.BUSY and \
            self.estimated_finish_time <= datetime.datetime.now():
            finished_order = self.current_order

            self.status = MachineStatus.IDLE
            self.current_order = None
            self.estimated_finish_time = None
            self.production_batch_id = None

        # TOD0 2: Panggil Logika di StockController & DatabaseClient untuk:
        #   a. Kurangi stok bahan baku (Auto Adjust Stock)
        #   b. Update status order di DB ke 'Selesasi'.
        #   c. Update record di tabel 'production_batch' (set finish time)

            return finished_order
        return None

class ProductionScheduler:
    def __init__(self, num_machine: int = 2):
        self.queue = ProductionPriorityQueue()
        self.machine = [ProductionMachine(i + 1) for i in range(num_machine)]

        # TOD0 3: Inisialisasi DatabaseClient dan StockController di sini
        # self.db_client = DatabaseClient
        # self.stock_controller = StockController(self.db_client, self.queue)
    
    def _fetch_new_orders_from_db(self):
        # TOD0 4: Ini akan mengganti panggilana ke self.db_client.fetch_new_confirmed_orders()
        # for order in new_order_list:
        #     self.queue.add_order(order)
        pass

    def estimate_production_duration(self, order: Order) -> float:
        return order.total_quantity * 1.0
    
    def run_scheduling_cycle(self):
        self._fetch_new_orders_from_db()

        # TOD0 5: Panggil self.stock.controller.check_and_update_all_priorities()

        finished_orders = []
        for machine in self.machine:
            finished_order = machine.check_finish()
            if finished_orders:
                finished_orders.append(finished_order)
                # self.stock_controller.adjust_stock_after_production(finished_order)
        
        for machine in self.machine:
            if machine.status == MachineStatus.IDLE:
                next_order = self.queue.get_highest_priority_order()

                if next_order:
                    duration = self.estimate_production_duration()
                    machine.start_production(next_order, duration)
                else:
                    # untuk isi log antrian kosong
                    pass

    def start_polling(self, interval_seconds: int = 5):
        try:
            while True:
                self.run_scheduling_cycle()
                time.sleep(interval_seconds)
        except KeyboardInterrupt:
            # log untuk schedule dihentikan
            pass
        # TOD0: Tambahakan logika cleanup/disconnect DB
            