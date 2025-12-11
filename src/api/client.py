# src/api/client.py

import psycopg2
from typing import Optional, List, Tuple
from datetime import datetime
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

    def fetch_all_products(self) -> List[Tuple]:
        """Mengambil semua produk dari tabel product."""
        query = "SELECT product_id, product_name, description, price FROM product;"
        try:
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except psycopg2.Error as e:
            print(f"❌ Gagal mengambil produk: {e}")
            return []

    def fetch_new_orders(self) -> List[Tuple]:
        """
        Mengambil pesanan yang statusnya 'Diproses' (status_id=2) dan siap dijadwalkan.
        Mengembalikan data yang dibutuhkan untuk inisialisasi objek Order.
        """
        query = """
            SELECT 
            o.order_id, 
            o.customer_id,
            o.order_timestamp, 
            o.deadline,
            o.total_price, 
            o.status_id, 
            o.total_quantity, 
            s.status_name  -- Kolom terakhir, tanpa koma
        FROM 
            orders o -- Ambil dari tabel orders dengan alias 'o'
        JOIN 
            status s ON o.status_id = s.status_id -- Gabungkan dengan tabel status (alias 's')
        WHERE 
            o.status_id = 2 -- Filter status
        ORDER BY 
            o.order_timestamp ASC;
        """
        try:
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except psycopg2.Error as e:
            print(f"❌ Gagal mengambil order baru untuk Scheduler: {e}")
            return []

    def fetch_customer_orders(self, customer_id: int) -> List[Tuple]:
        """Mengambil daftar pesanan pelanggan, termasuk nama status."""
        query = """
            SELECT 
                o.order_id, 
                o.order_timestamp, 
                o.total_price, 
                s.status_name
            FROM 
                orders o
            JOIN 
                status s ON o.status_id = s.status_id
            WHERE 
                o.customer_id = %s
            ORDER BY 
                o.order_timestamp DESC;
        """
        try:
            self.cursor.execute(query, (customer_id,))
            return self.cursor.fetchall()
        except psycopg2.Error as e:
            print(f"❌ Gagal mengambil pesanan pelanggan: {e}")
            return []

    def fetch_low_stock_items(self, threshold: int) -> List[str]:
        """Mengambil nama-nama item yang stoknya di bawah ambang batas."""
        query = """
            SELECT ingredient_name FROM ingredient 
            WHERE stock < %s;
        """
        try:
            self.cursor.execute(query, (threshold,))
            # Mengambil list item_name (flattened list)
            return [row[0] for row in self.cursor.fetchall()]
        except psycopg2.Error as e:
            print(f"❌ Gagal mengambil stok rendah: {e}")
            return []
    
    def fetch_pending_orders_by_customer(self, customer_id: int) -> List[Tuple]:
        """Mengambil pesanan yang masih 'Menunggu Konfirmasi' (status_id=1) oleh pelanggan."""
        query = """
            SELECT 
                o.order_id, 
                o.order_timestamp, 
                o.total_price, 
                s.status_name -- Termasuk nama status
            FROM 
                orders o
            JOIN 
                status s ON o.status_id = s.status_id
            WHERE 
                o.customer_id = %s AND o.status_id = 1
            ORDER BY 
                o.order_timestamp DESC;
        """
        try:
            self.cursor.execute(query, (customer_id,))
            return self.cursor.fetchall()
        except psycopg2.Error as e:
            print(f"❌ Gagal mengambil pending orders: {e}")
            return []
    
    def fetch_order_details_by_id(self, order_id: int, customer_id: int) -> Optional[Tuple]:
        """
        Mengambil detail pesanan lengkap: Header dan Items.
        Menggunakan satu koneksi untuk efisiensi.
        """
        try:
            # 1. Ambil Data Header Pesanan (Orders + Status)
            header_query = """
                SELECT 
                    o.order_id, o.order_timestamp, o.total_price, s.status_name, o.deadline
                FROM 
                    orders o
                JOIN 
                    status s ON o.status_id = s.status_id
                WHERE 
                    o.order_id = %s AND o.customer_id = %s;
            """
            self.cursor.execute(header_query, (order_id, customer_id))
            order_header = self.cursor.fetchone()
            
            if not order_header:
                return None # Pesanan tidak ditemukan atau bukan milik customer
            
            # 2. Ambil Detail Item Pesanan (Order Item + Product)
            items_query = """
                SELECT 
                    p.product_id,
                    p.product_name, 
                    oi.quantity, 
                    p.price
                FROM 
                    order_item oi
                JOIN 
                    product p ON oi.product_id = p.product_id
                WHERE 
                    oi.order_id = %s;
            """
            self.cursor.execute(items_query, (order_id,))
            order_items = self.cursor.fetchall()
            
            # Kembalikan Header dan Items dalam satu tuple
            return (order_header, order_items)
            
        except psycopg2.Error as e:
            print(f"❌ Gagal mengambil detail pesanan {order_id}: {e}")
            return None

    def update_order_status(self, order_id: int, new_status_id: int) -> bool:
        """Mengupdate status_id pesanan berdasarkan order_id."""
        query = "UPDATE orders SET status_id = %s WHERE order_id = %s;"
        try:
            self.cursor.execute(query, (new_status_id, order_id))
            self._commit()
            return True
        except psycopg2.Error as e:
            self.conn.rollback()
            print(f"❌ Gagal update status pesanan {order_id}: {e}")
            return False
    
    def create_order_transaction(self, customer_id: int, total_price: float, total_quantity: int, 
                                 deadline: datetime, order_items: List[dict]) -> Optional[int]:
        """Membuat pesanan baru dan item pesanan secara transaksional.
           Mengembalikan order_id yang baru dibuat."""
        
        try:
            # 1. INSERT ke tabel orders (Default status_id = 1 'Menunggu Konfirmasi')
            order_insert_query = """
                INSERT INTO orders (customer_id, deadline, total_price, total_quantity, status_id)
                VALUES (%s, %s, %s, %s, 1) RETURNING order_id;
            """
            self.cursor.execute(order_insert_query, 
                                (customer_id, deadline, total_price, total_quantity))
            new_order_id = self.cursor.fetchone()[0] # Ambil ID yang baru dibuat

            # 2. INSERT massal ke tabel order_item
            order_item_insert_query = """
                INSERT INTO order_item (order_id, product_id, quantity)
                VALUES (%s, %s, %s);
            """
            
            for item in order_items:
                self.cursor.execute(order_item_insert_query, 
                                    (new_order_id, item['product_id'], item['quantity']))
            
            # 3. COMMIT Transaksi
            self._commit() 
            return new_order_id
            
        except psycopg2.Error as e:
            # Rollback jika ada error
            self.conn.rollback()
            print(f"❌ Transaction GAGAL saat membuat pesanan. Error: {e}")
            return None

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

    def adjust_inventory_transaction(self, item_changes: List[tuple]):
        """Mengurangi atau menambah stok bahan baku secara transaksional."""
        update_query = """
            UPDATE ingredient
            SET stock = stock - %s 
            WHERE ingredient_name = %s;
        """
        try:
            for reduction_amount, item_name in item_changes:
                # Pastikan pengurangan adalah angka positif (reduction_amount)
                self.cursor.execute(update_query, (reduction_amount, item_name))
            
            self._commit()
            return True
        except psycopg2.Error as e:
            self.conn.rollback()
            print(f"❌ Transaction GAGAL saat update inventory. Error: {e}")
            return False

    def __del__(self):
        self.close()