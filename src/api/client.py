# src/api/client.py

import psycopg2
from typing import Optional
from src.config import PGHOST, PGDATABASE, PGUSER, PGPASSWORD, PGSSLMODE

class DatabaseClient:
    def __init__(self):
        self.conn = None
        self.cursor = None
        self._connect()

    def _connect(self):
        try:
            self.conn = psycopg2.connect (
                host=PGHOST,
                database=PGDATABASE,
                user=PGUSER,
                password=PGPASSWORD,
                sslmode=PGSSLMODE
            )

            self.conn.autocommit = False
            self.cursor = self.conn.cursor()
            print("DB Connect!")
        
        except psycopg2.Error as e:
            print("Gagal connect DB, error: ", e)
        
    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        print("Koneksi ditutup")

    def _execute_query(self, query: str, params=None):
        """Metode dasar untuk menjalankan query SELECT atau operasi non-transaksional."""
        try:
            self.cursor.execute(query, params)
            return self.cursor
        except psycopg2.Error as e:
            self.conn.rollback()
            print(f"❌ Error saat menjalankan query: {e}")
            raise

    def _commit(self):
        """Melakukan commit untuk menyimpan perubahan di database."""
        try:
            self.conn.commit()
            return True
        except psycopg2.Error as e:
            self.conn.rollback()
            print(f"❌ Error saat melakukan commit. Rollback dilakukan. Error: {e}")
            raise

    def fetch_new_orders(self) -> list:
        """Mengambil order baru yang siap diproses dari DB."""
        query = """
            SELECT order_id, deadline, total_quantity, order_timestamp, status_id, customer_id
            FROM orders
            WHERE status_id = 1  -- Asumsi 1 = 'Menunggu Konfirmasi'
            ORDER BY order_timestamp ASC;
        """
        try:
            self.cursor.execute(query)
            results = self.cursor.fetchall() 
            
            return results 
        except psycopg2.Error as e:
            print(f"❌ Gagal mengambil order baru: {e}")
            return []
    
    def start_production_transaction(self, order_id: int, machine_id: int) -> Optional[int]:
        """
        [TODO 1] Memulai transaksi produksi:
        1. UPDATE status order menjadi 'Diproses' (status_id = 2).
        2. INSERT record baru di production_batch dan ambil production_id yang baru.
        """
        try:
            update_order_query = "UPDATE orders SET status_id = 2 WHERE order_id = %s;"
            self.cursor.execute(update_order_query, (order_id,))

            insert_batch_query = """
                INSERT INTO production_batch (order_id, machine_id, start_time, status)
                VALUES (%s, %s, NOW(), 'IN_PROGRESS')
                RETURNING production_id;
            """
            self.cursor.execute(insert_batch_query, (order_id, machine_id))
            
            new_batch_id = self.cursor.fetchone()[0]
            self._commit() 
            
            return new_batch_id
            
        except psycopg2.Error as e:
            self.conn.rollback()
            print(f"❌ Transaction GAGAL saat memulai produksi Order ID {order_id}. Error: {e}")
            return None
    
    def finish_production_transaction(self, order_id: int, production_batch_id: int):
        """
        [TODO 2] Menyelesaikan transaksi produksi:
        1. UPDATE record production_batch (set finish_time dan status 'COMPLETED').
        2. UPDATE status order menjadi 'Selesai' (status_id = 4).
        """
        try:
            update_batch_query = """
                UPDATE production_batch SET finish_time = NOW(), status = 'COMPLETED'
                WHERE production_id = %s;
            """
            self.cursor.execute(update_batch_query, (production_batch_id,))

            update_order_query = "UPDATE orders SET status_id = 4 WHERE order_id = %s;"
            self.cursor.execute(update_order_query, (order_id,))
            
            self._commit() 
            
            return True
            
        except psycopg2.Error as e:
            self.conn.rollback()
            print(f"❌ Transaction GAGAL saat menyelesaikan produksi Order ID {order_id}. Error: {e}")
            return False
        
    def __del__(self):
        self.close()