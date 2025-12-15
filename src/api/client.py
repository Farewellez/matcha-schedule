# src/api/client.py

import psycopg2
from typing import Optional, List, Tuple, Dict
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
        if self.cursor is None or self.conn is None:
            error_msg = "❌ Koneksi atau kursor DB belum diinisialisasi. Gagal eksekusi query."
            print(error_msg)
            raise ConnectionError(error_msg)
        try:
            self.cursor.execute(query, params)
            return self.cursor
        except psycopg2.Error as e:
            self.conn.rollback()
            print(f"❌ Error saat menjalankan query: {e}")
            raise

    def _commit(self):
        if self.conn is None:
            error_msg = "❌ Koneksi DB belum diinisialisasi. Gagal melakukan commit."
            print(error_msg)
            raise ConnectionError(error_msg)    
        try:
            self.conn.commit()
            return True
        except psycopg2.Error as e:
            self.conn.rollback()
            print(f"❌ Error saat melakukan commit. Rollback dilakukan. Error: {e}")
            raise

    def fetch_all_products(self) -> List[Dict]:
            query = "SELECT product_id, product_name, description, price FROM product;"
            
            if self.cursor is None or self.conn is None:
                error_msg = "❌ Koneksi DB belum diinisialisasi. Gagal melakukan commit."
                print(error_msg)
                raise ConnectionError(error_msg)
            
            try:
                self.cursor.execute(query)
                results = self.cursor.fetchall()
                
                if self.cursor.description is None:
                    # Jika tidak ada description, ini bukan hasil SELECT yang valid atau kursor error
                    print("❌ Query berhasil, namun tidak ada deskripsi kolom yang ditemukan.")
                    return []
                
                columns = [desc[0] for desc in self.cursor.description]
                
                products = []
                for row in results:
                    products.append(dict(zip(columns, row))) 
                    
                return products
                
            except psycopg2.Error as e:
                print(f"❌ Gagal mengambil produk: {e}")
                return []

    def force_order_status(self, order_id: int, new_status_id: int) -> bool:
        """Mengubah status order secara paksa untuk keperluan testing/admin."""
        query = "UPDATE orders SET status_id = %s WHERE order_id = %s;"
        
        if self.cursor is None or self.conn is None:
                error_msg = "❌ Koneksi DB belum diinisialisasi. Gagal melakukan commit."
                print(error_msg)
                raise ConnectionError(error_msg)
        
        try:
            self.cursor.execute(query, (new_status_id, order_id))
            self.conn.commit()
            # Cek apakah ada baris yang benar-benar terupdate
            return self.cursor.rowcount > 0 
        except psycopg2.Error as e:
            self.conn.rollback()
            print(f"❌ DB Error (force_order_status): {e}")
            return False

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
        
        if self.cursor is None or self.conn is None:
                error_msg = "❌ Koneksi DB belum diinisialisasi. Gagal melakukan commit."
                print(error_msg)
                raise ConnectionError(error_msg)
        
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

        if self.cursor is None or self.conn is None:
                error_msg = "❌ Koneksi DB belum diinisialisasi. Gagal melakukan commit."
                print(error_msg)
                raise ConnectionError(error_msg)
        
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

        if self.cursor is None or self.conn is None:
                error_msg = "❌ Koneksi DB belum diinisialisasi. Gagal melakukan commit."
                print(error_msg)
                raise ConnectionError(error_msg)
        
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

        if self.cursor is None or self.conn is None:
                error_msg = "❌ Koneksi DB belum diinisialisasi. Gagal melakukan commit."
                print(error_msg)
                raise ConnectionError(error_msg)
        
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

        if self.cursor is None or self.conn is None:
                error_msg = "❌ Koneksi DB belum diinisialisasi. Gagal melakukan commit."
                print(error_msg)
                raise ConnectionError(error_msg)
        
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

        if self.cursor is None or self.conn is None:
                error_msg = "❌ Koneksi DB belum diinisialisasi. Gagal melakukan commit."
                print(error_msg)
                raise ConnectionError(error_msg)

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
        
        if self.cursor is None or self.conn is None:
                error_msg = "❌ Koneksi DB belum diinisialisasi. Gagal melakukan commit."
                print(error_msg)
                raise ConnectionError(error_msg)
        
        try:
            # 1. INSERT ke tabel orders (Default status_id = 1 'Menunggu Konfirmasi')
            order_insert_query = """
                INSERT INTO orders (customer_id, deadline, total_price, total_quantity, status_id)
                VALUES (%s, %s, %s, %s, 1) RETURNING order_id;
            """
            
            self.cursor.execute(order_insert_query, 
                                (customer_id, deadline, total_price, total_quantity))
            
            fetched_result = self.cursor.fetchone()
        
            if fetched_result is None:
                # Jika INSERT gagal mengembalikan ID, ini adalah kegagalan fatal.
                print("❌ Transaction GAGAL: INSERT Order tidak mengembalikan Order ID.")
                self.conn.rollback() 
                return None
            
            new_order_id = fetched_result[0] # Ambil ID yang baru dibuat

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
        if self.cursor is None or self.conn is None:
            error_msg = "❌ Koneksi atau kursor DB belum diinisialisasi. Gagal memulai produksi."
            print(error_msg)
            raise ConnectionError(error_msg)
        
        try:
            update_order_query = "UPDATE orders SET status_id = 2 WHERE order_id = %s;"
            self.cursor.execute(update_order_query, (order_id,))

            insert_batch_query = """
                INSERT INTO production_batch (order_id, machine_id, start_time, status)
                VALUES (%s, %s, NOW(), 'IN_PROGRESS')
                RETURNING production_id;
            """
            self.cursor.execute(insert_batch_query, (order_id, machine_id))
            
            fetched_result = self.cursor.fetchone()

            if fetched_result is None:
                # Jika INSERT gagal mengembalikan ID, ini adalah kegagalan transaksi
                error_msg = f"❌ Transaction GAGAL: INSERT Batch tidak mengembalikan ID untuk Order ID {order_id}."
                print(error_msg)
                self.conn.rollback() 
                return None
            
            new_batch_id = fetched_result[0]
            self._commit() 
            
            return new_batch_id
            
        except psycopg2.Error as e:
            self.conn.rollback()
            print(f"❌ Transaction GAGAL saat memulai produksi Order ID {order_id}. Error: {e}")
            return None
    
    def finish_production_transaction(self, order_id: int, production_batch_id: int):
        
        if self.cursor is None or self.conn is None:
            error_msg = "❌ Koneksi atau kursor DB belum diinisialisasi. Gagal menyelesaikan produksi."
            print(error_msg)
            raise ConnectionError(error_msg)
    
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
        
        if self.cursor is None or self.conn is None:
            error_msg = "❌ Koneksi atau kursor DB belum diinisialisasi. Gagal update inventory."
            print(error_msg)
            raise ConnectionError(error_msg)
    
        update_query = """
            UPDATE ingredient
            SET stock = stock - %s 
            WHERE ingredient_name = %s;
        """

        try:
            for item_name, reduction_amount in item_changes:
                # Pastikan pengurangan adalah angka positif (reduction_amount)
                self.cursor.execute(update_query, (reduction_amount, item_name))
            
            self._commit()
            return True
        
        except psycopg2.Error as e:
            self.conn.rollback()
            print(f"❌ Transaction GAGAL saat update inventory. Error: {e}")
            return False

    def check_user_exists(self, username: str, email: str) -> bool:
        """Memeriksa apakah username atau email sudah terdaftar."""

        if self.cursor is None or self.conn is None:
            error_msg = "❌ Koneksi atau kursor DB belum diinisialisasi. Gagal memeriksa pengguna."
            print(error_msg)
            # Melempar error untuk ditangani oleh kode pemanggil
            raise ConnectionError(error_msg)
    
        # Query untuk Customer
        query_customer = """
            SELECT 1 FROM customer
            WHERE username = %s OR email = %s
            LIMIT 1;
        """
        # Query untuk Admin
        query_admin = """
            SELECT 1 FROM admin
            WHERE username = %s OR email = %s
            LIMIT 1;
        """
        
        try:
            self.cursor.execute(query_customer, (username, email))
            if self.cursor.fetchone():
                return True
            
            self.cursor.execute(query_admin, (username, email))
            if self.cursor.fetchone():
                return True

            return False
        except psycopg2.Error as e:
            print(f"❌ DB Error (check_user_exists): {e}")
            return True  # Asumsikan True (sudah ada) untuk menghindari registrasi ganda jika ada error

    def register_new_customer(self, username: str, fullname: str, phone: str, email: str, hashed_password: str) -> int | None:
        """Menyimpan pengguna baru ke tabel customer."""

        if self.cursor is None or self.conn is None:
            error_msg = "❌ Koneksi atau kursor DB belum diinisialisasi. Gagal registrasi pelanggan."
            print(error_msg)
            raise ConnectionError(error_msg)
    
        query = """
            INSERT INTO customer (username, fullname, phone, email, password, role_id)
            VALUES (%s, %s, %s, %s, %s, 2) 
            RETURNING customer_id;
        """
        try:
            self.cursor.execute(query, (username, fullname, phone, email, hashed_password))
            fetched_result = self.cursor.fetchone()
        
            if fetched_result is None:
                print("❌ DB Error: INSERT customer tidak mengembalikan ID.")
                self.conn.rollback() 
                return None

            new_customer_id = fetched_result[0]

            self.conn.commit()
            return new_customer_id
        
        except psycopg2.IntegrityError as e:
            self.conn.rollback()
            # IntegrityError terjadi jika UNIQUE (username/email) dilanggar
            print(f"❌ DB Integrity Error (register_new_customer): {e}")
            return None
        except psycopg2.Error as e:
            self.conn.rollback()
            print(f"❌ DB Error (register_new_customer): {e}")
            return None

    def authenticate_customer(self, username: str, hashed_password: str) -> dict | None:
        """Mencari dan memverifikasi Customer."""

        if self.cursor is None or self.conn is None:
            error_msg = "❌ Koneksi atau kursor DB belum diinisialisasi. Gagal autentikasi."
            print(error_msg)
            raise ConnectionError(error_msg)
        
        query = """
            SELECT customer_id, username, fullname, email
            FROM customer
            WHERE username = %s AND password = %s;
        """
        try:
            self.cursor.execute(query, (username, hashed_password))
            result = self.cursor.fetchone()

            if result:
                if self.cursor.description is None:
                    # Ini seharusnya tidak terjadi pada SELECT yang berhasil, tapi kita tangani
                    print("❌ Autentikasi berhasil, tapi metadata kolom tidak tersedia.")
                    return None 
            
                # Mengkonversi hasil tuple menjadi dictionary
                columns = [desc[0] for desc in self.cursor.description]
                return dict(zip(columns, result))
            else:
                return None
        except psycopg2.Error as e:
            print(f"❌ DB Error (authenticate_customer): {e}")
            return None

    def authenticate_admin(self, username: str, hashed_password: str) -> dict | None:
        """Mencari dan memverifikasi Admin."""
        if self.cursor is None or self.conn is None:
            error_msg = "❌ Koneksi atau kursor DB belum diinisialisasi. Gagal autentikasi Admin."
            print(error_msg)
            raise ConnectionError(error_msg)
    
        query = """
            SELECT admin_id, username, email
            FROM admin
            WHERE username = %s AND password = %s;
        """
        try:
            self.cursor.execute(query, (username, hashed_password))
            result = self.cursor.fetchone()

            if result:
                if self.cursor.description is None:
                    print("❌ Autentikasi Admin berhasil, tapi metadata kolom tidak tersedia.")
                    return None 

                # Mengkonversi hasil tuple menjadi dictionary
                columns = [desc[0] for desc in self.cursor.description]
                return dict(zip(columns, result))
            else:
                return None
        except psycopg2.Error as e:
            print(f"❌ DB Error (authenticate_admin): {e}")
            return None

    # Ganti definisi fungsi: tambahkan parameter 'recipe'
    def add_new_product_with_recipe(self, name: str, description: str, price: int, recipe: List[Tuple[int, int]]) -> Optional[int]:
        """
        Menyimpan produk baru ke tabel product dan resepnya ke product_ingredients dalam satu transaksi.
        Recipe: List of (ingredient_id, quantity).
        """
        if self.cursor is None or self.conn is None:
            error_msg = "❌ Koneksi atau kursor DB belum diinisialisasi. Gagal menambahkan produk."
            print(error_msg)
            raise ConnectionError(error_msg)
    
        # 1. Query untuk INSERT Produk
        product_query = """
            INSERT INTO product (product_name, description, price)
            VALUES (%s, %s, %s)
            RETURNING product_id;
        """
        
        # 2. Query untuk INSERT Resep
        recipe_query = """
            INSERT INTO product_ingredients (product_id, ingredient_id, quantity_per_unit)
            VALUES (%s, %s, %s);
        """
        
        try:
            # --- Langkah 1: INSERT Produk dan Ambil ID ---
            # Ini adalah tempat potensi kegagalan pertama (misal: koneksi putus)
            self.cursor.execute(product_query, (name, description, price))
            fetched_result = self.cursor.fetchone()
        
            if fetched_result is None:
                # Jika INSERT gagal mengembalikan ID, batalkan.
                print("❌ DB Error: INSERT Product tidak mengembalikan Product ID.")
                self.conn.rollback() # Aman karena guardrail di atas
                return None

            new_product_id = fetched_result[0]
            
            # --- Langkah 2: LOOP dan INSERT Resep ---
            # Ini adalah tempat potensi kegagalan kedua (misal: Foreign Key Constraint violation)
            for ing_id, quantity in recipe:
                self.cursor.execute(recipe_query, (new_product_id, ing_id, quantity))
            
            # --- Langkah 3: COMMIT Transaksi Penuh ---
            self.conn.commit()
            return new_product_id
            
        except psycopg2.Error as e:
            # --- Langkah 4: ROLLBACK Jika Terjadi Error ---
            # Jika terjadi error di Langkah 1 atau 2, ROLLBACK akan membatalkan semua perubahan.
            self.conn.rollback()
            print(f"❌ DB Error (add_new_product_with_recipe): Transaksi GAGAL. Detail: {e}")
            return None

    def get_product_by_id(self, product_id: int) -> dict | None:
        """Mengambil detail produk berdasarkan ID."""

        if self.cursor is None or self.conn is None:
            error_msg = "❌ Koneksi atau kursor DB belum diinisialisasi. Gagal mengambil produk."
            print(error_msg)
            raise ConnectionError(error_msg)
    
        query = """
            SELECT product_id, product_name, description, price
            FROM product
            WHERE product_id = %s;
        """
        try:
            self.cursor.execute(query, (product_id,))
            result = self.cursor.fetchone()

            if result:
                if self.cursor.description is None:
                    print("❌ SELECT berhasil, tetapi metadata kolom tidak tersedia.")
                    return None
            
                # Mengkonversi hasil tuple menjadi dictionary
                columns = [desc[0] for desc in self.cursor.description]
                return dict(zip(columns, result))
        
            return None
        except psycopg2.Error as e:
            print(f"❌ DB Error (get_product_by_id): {e}")
            return None
    
    def update_product(self, product_id: int, name: str, description: str, price: int) -> bool:
        """Memperbarui detail produk."""
        if self.cursor is None or self.conn is None:
            error_msg = "❌ Koneksi atau kursor DB belum diinisialisasi. Gagal update produk."
            print(error_msg)
            raise ConnectionError(error_msg)
    
        query = """
            UPDATE product
            SET product_name = %s, description = %s, price = %s
            WHERE product_id = %s;
        """
        try:
            # Perhatikan urutan argumen: name, description, price, product_id
            self.cursor.execute(query, (name, description, price, product_id))
            self.conn.commit()
            # Mengembalikan True jika ada baris yang berhasil diupdate
            return self.cursor.rowcount > 0 
        except psycopg2.Error as e:
            self.conn.rollback()
            print(f"❌ DB Error (update_product): Gagal update produk. {e}")
            return False
    
    def delete_product_and_relations(self, product_id: int) -> bool:
        """Menghapus produk dari tabel 'product'. Karena adanya FOREIGN KEY 
        dengan ON DELETE CASCADE di product_ingredients, relasi akan terhapus otomatis."""
        if self.cursor is None or self.conn is None:
            error_msg = "❌ Koneksi atau kursor DB belum diinisialisasi. Gagal menghapus produk."
            print(error_msg)
            raise ConnectionError(error_msg)
        
        query = """
            DELETE FROM product
            WHERE product_id = %s;
        """
        try:
            self.cursor.execute(query, (product_id,))
            self.conn.commit()
            # Mengembalikan True jika ada baris yang dihapus
            return self.cursor.rowcount > 0 
        except psycopg2.Error as e:
            self.conn.rollback()
            print(f"❌ DB Error (delete_product_and_relations): {e}")
            return False
    
    def fetch_all_ingredients(self) -> list:
        """Mengambil semua bahan baku dari tabel ingredient."""
        query = """
            SELECT ingredient_id, ingredient_name, unit, stock, minimum_stock
            FROM ingredient
            ORDER BY ingredient_id;
        """
        if self.cursor is None or self.conn is None:
            error_msg = "❌ Koneksi DB belum diinisialisasi. Gagal mengambil bahan baku."
            print(error_msg)
            raise ConnectionError(error_msg)
    
        try:
            self.cursor.execute(query)
            results = self.cursor.fetchall()
            # Ambil semua hasil
            if self.cursor.description is None:
                print("❌ SELECT berhasil, tetapi metadata kolom tidak tersedia.")
                return []
            
            columns = [desc[0] for desc in self.cursor.description]

            ingredients_list = []
            for row in results:
                ingredients_list.append(dict(zip(columns, row)))

            return ingredients_list

        except psycopg2.Error as e:
            print(f"❌ DB Error (fetch_all_ingredients): {e}")
            return []

    def check_ingredient_exists(self, name: str) -> dict | None:
        """Mencari bahan baku berdasarkan nama (case-insensitive). Mengembalikan data jika ditemukan."""
        if self.cursor is None or self.conn is None:
            error_msg = "❌ Koneksi DB belum diinisialisasi. Gagal memeriksa bahan baku."
            print(error_msg)
            raise ConnectionError(error_msg)
    
        query = """
            SELECT ingredient_id, ingredient_name, unit, stock, minimum_stock
            FROM ingredient
            WHERE LOWER(ingredient_name) = LOWER(%s);
        """
        try:
            self.cursor.execute(query, (name,))
            result = self.cursor.fetchone()
            if result:
                if self.cursor.description is None:
                    print("❌ SELECT berhasil, tetapi metadata kolom tidak tersedia.")
                    return None

                columns = [desc[0] for desc in self.cursor.description]
                return dict(zip(columns, result))
        
            return None
        except psycopg2.Error as e:
            print(f"❌ DB Error (check_ingredient_exists): {e}")
            return None

    def update_ingredient_stock(self, ingredient_id: int, added_stock: int) -> bool:
        """Menambahkan stok ke bahan baku yang sudah ada."""
        query = """
            UPDATE ingredient
            SET stock = stock + %s
            WHERE ingredient_id = %s;
        """
        if self.cursor is None or self.conn is None:
            error_msg = "❌ Koneksi DB belum diinisialisasi. Gagal update stok."
            print(error_msg)
            raise ConnectionError(error_msg)
    
        try:
            self.cursor.execute(query, (added_stock, ingredient_id))
            self.conn.commit()
            return self.cursor.rowcount > 0
        except psycopg2.Error as e:
            self.conn.rollback()
            print(f"❌ DB Error (update_ingredient_stock): {e}")
            return False

    def add_new_ingredient(self, name: str, unit: str, stock: int, min_stock: int) -> int | None:
        """Menyimpan bahan baku baru ke database."""
        if self.cursor is None or self.conn is None:
            error_msg = "❌ Koneksi DB belum diinisialisasi. Gagal menambah bahan baku."
            print(error_msg)
            raise ConnectionError(error_msg)
    
        query = """
            INSERT INTO ingredient (ingredient_name, unit, stock, minimum_stock)
            VALUES (%s, %s, %s, %s)
            RETURNING ingredient_id;
        """
        try:
            self.cursor.execute(query, (name, unit, stock, min_stock))
        
            # --- PERBAIKAN: Pengecekan fetchone() ---
            fetched_result = self.cursor.fetchone()

            if fetched_result is None:
                print("❌ DB Error: INSERT ingredient tidak mengembalikan ID.")
                self.conn.rollback() 
                return None

            new_id = fetched_result[0]
            # ---------------------------------------

            self.conn.commit()
            return new_id
    
        except psycopg2.Error as e:
            self.conn.rollback()
            print(f"❌ DB Error (add_new_ingredient): {e}")
            return None

    def get_ingredient_by_id(self, ing_id: int) -> dict | None:
        """Mengambil detail bahan baku berdasarkan ID."""
        if self.cursor is None or self.conn is None:
            error_msg = "❌ Koneksi DB belum diinisialisasi. Gagal mengambil detail bahan baku."
            print(error_msg)
            raise ConnectionError(error_msg)
    
        query = """
            SELECT ingredient_id, ingredient_name, unit, stock, minimum_stock
            FROM ingredient
            WHERE ingredient_id = %s;
        """
        try:
            self.cursor.execute(query, (ing_id,))
            result = self.cursor.fetchone()

            if result:
                if self.cursor.description is None:
                    print("❌ SELECT berhasil, tetapi metadata kolom tidak tersedia.")
                    return None

                columns = [desc[0] for desc in self.cursor.description]
                return dict(zip(columns, result))
        
            return None
        except psycopg2.Error as e:
            print(f"❌ DB Error (get_ingredient_by_id): {e}")
            return None

    def update_ingredient_details(self, ing_id: int, name: str, unit: str, min_stock: int) -> bool:
        """Memperbarui nama, unit, dan minimum_stock bahan baku."""
        if self.cursor is None or self.conn is None:
            error_msg = "❌ Koneksi DB belum diinisialisasi. Gagal update detail bahan baku."
            print(error_msg)
            raise ConnectionError(error_msg)
    
        query = """
            UPDATE ingredient
            SET ingredient_name = %s, unit = %s, minimum_stock = %s
            WHERE ingredient_id = %s;
        """
        try:
            # Perhatikan urutan argumen: name, unit, min_stock, ing_id
            self.cursor.execute(query, (name, unit, min_stock, ing_id))
            self.conn.commit()
            # Mengembalikan True jika ada baris yang berhasil diupdate
            return self.cursor.rowcount > 0 
        except psycopg2.Error as e:
            self.conn.rollback()
            print(f"❌ DB Error (update_ingredient_details): Gagal update bahan baku. {e}")
            return False

    def set_ingredient_stock(self, ing_id: int, new_stock: int) -> bool:
        """Mengatur nilai stok bahan baku ke nilai yang spesifik."""
        if self.cursor is None or self.conn is None:
            error_msg = "❌ Koneksi DB belum diinisialisasi. Gagal mengatur stok."
            print(error_msg)
            raise ConnectionError(error_msg)
        
        query = """
            UPDATE ingredient
            SET stock = %s
            WHERE ingredient_id = %s;
        """
        try:
            # Perhatikan urutan argumen: new_stock, ing_id
            self.cursor.execute(query, (new_stock, ing_id))
            self.conn.commit()
            # Mengembalikan True jika ada baris yang berhasil diupdate
            return self.cursor.rowcount > 0 
        except psycopg2.Error as e:
            self.conn.rollback()
            print(f"❌ DB Error (set_ingredient_stock): Gagal update stok. {e}")
            return False

    def delete_ingredient_and_relations(self, ing_id: int) -> bool:
        """Menghapus bahan baku dari tabel 'ingredient'. Relasi di product_ingredients
        akan terhapus otomatis karena adanya ON DELETE CASCADE."""
        if self.cursor is None or self.conn is None:
            error_msg = "❌ Koneksi DB belum diinisialisasi. Gagal menghapus bahan baku."
            print(error_msg)
            raise ConnectionError(error_msg)
    
        query = """
            DELETE FROM ingredient
            WHERE ingredient_id = %s;
        """
        try:
            self.cursor.execute(query, (ing_id,))
            self.conn.commit()
            # Mengembalikan True jika ada baris yang dihapus
            return self.cursor.rowcount > 0 
        except psycopg2.Error as e:
            self.conn.rollback()
            print(f"❌ DB Error (delete_ingredient_and_relations): {e}")
            return False
        
    def get_popular_products(self, limit: int = 10) -> list:
        """Mengambil daftar produk yang paling banyak dipesan (diurutkan berdasarkan total kuantitas)."""
        if self.cursor is None or self.conn is None:
            error_msg = "❌ Koneksi DB belum diinisialisasi. Gagal mengambil produk populer."
            print(error_msg)
            raise ConnectionError(error_msg)
    
        query = f"""
            SELECT 
                p.product_name,
                SUM(oi.quantity) AS total_ordered
            FROM 
                order_item oi
            JOIN 
                product p ON oi.product_id = p.product_id
            GROUP BY 
                p.product_name
            ORDER BY 
                total_ordered DESC
            LIMIT 
                {limit};
        """
        try:
            self.cursor.execute(query)
            results = self.cursor.fetchall()

            # --- GUARDRAIL DESCRIPTION ---
            if self.cursor.description is None:
                print("❌ SELECT berhasil, tetapi metadata kolom tidak tersedia.")
                return []

            # Mengkonversi hasil tuple menjadi dictionary
            columns = [desc[0] for desc in self.cursor.description]

            popular_products_list = []
            for row in results:
                popular_products_list.append(dict(zip(columns, row)))

            return popular_products_list
            
        except psycopg2.Error as e:
            print(f"❌ DB Error (get_popular_products): {e}")
            return []

    def get_low_stock_ingredients(self) -> list:
        """Mengambil daftar bahan baku yang stoknya lebih rendah atau sama dengan minimum_stock."""
        if self.cursor is None or self.conn is None:
            error_msg = "❌ Koneksi DB belum diinisialisasi. Gagal mengambil stok rendah."
            print(error_msg)
            raise ConnectionError(error_msg)
    
        query = """
            SELECT 
                ingredient_name, unit, stock, minimum_stock
            FROM 
                ingredient
            WHERE 
                stock <= minimum_stock
            ORDER BY 
                stock ASC;
        """
        try:
            self.cursor.execute(query)
            results = self.cursor.fetchall()
            
            # Mengkonversi hasil tuple menjadi dictionary (untuk kemudahan di View)
            if self.cursor.description is None:
                print("❌ SELECT berhasil, tetapi metadata kolom tidak tersedia.")
                return []
            
            columns = [desc[0] for desc in self.cursor.description] 
            
            low_stock_list = []
            for row in results:
                low_stock_list.append(dict(zip(columns, row)))
            
            return low_stock_list
        except psycopg2.Error as e:
            print(f"❌ DB Error (get_low_stock_ingredients): {e}")
            return []

    def adjust_ingredient_stock(self, ingredient_id: int, change_amount: int) -> bool:
        """
        Mengupdate stok bahan baku dengan menambahkan/mengurangi 'change_amount' 
        dari stok saat ini menggunakan UPDATE query.
        """
        if self.cursor is None or self.conn is None:
            error_msg = "❌ Koneksi DB belum diinisialisasi. Gagal mengubah stok."
            print(error_msg)
            raise ConnectionError(error_msg)
    
        # Kita menggunakan operator +/-, yang secara atomik menambahkan nilai.
        query = """
            UPDATE ingredient
            SET stock = stock + %s
            WHERE ingredient_id = %s;
        """
        try:
            self.cursor.execute(query, (change_amount, ingredient_id))
            self.conn.commit()
            return self.cursor.rowcount > 0
        except psycopg2.Error as e:
            self.conn.rollback()
            print(f"❌ DB Error (adjust_ingredient_stock): Gagal mengubah stok. {e}")
            return False

    # Di dalam class DatabaseClient di client.py:

    def deduct_ingredients_for_order(self, order_id: int) -> bool:
        """
        Menghitung total bahan baku yang terpakai untuk Order tertentu 
        dan mengurangi stok yang sesuai secara transaksional.
        """
        
        if self.cursor is None or self.conn is None:
            error_msg = "❌ Koneksi DB belum diinisialisasi. Gagal mengurangi stok untuk Order."
            print(error_msg)
            raise ConnectionError(error_msg)
    
        deduction_query = """
        WITH ingredients_needed AS (
            SELECT
                t2.ingredient_id,
                -- PERBAIKAN: Ganti t2.quantity menjadi t2.quantity_per_unit
                SUM(t1.quantity * t2.quantity_per_unit) AS total_deduction_amount 
            FROM
                order_item t1 -- Ini sudah kita perbaiki dari order_items
            JOIN
                product_ingredients t2 ON t1.product_id = t2.product_id
            WHERE
                t1.order_id = %s
            GROUP BY
                t2.ingredient_id
        )
        -- UPDATE semua stok bahan baku yang terdaftar di ingredients_needed
        UPDATE ingredient
        SET stock = ingredient.stock - ineeded.total_deduction_amount
        FROM ingredients_needed AS ineeded
        WHERE ingredient.ingredient_id = ineeded.ingredient_id
        RETURNING ingredient.ingredient_id;
        """
        
        try:
            # 1. Jalankan query pengurangan stok
            self.cursor.execute(deduction_query, (order_id,))
            
            # 2. Cek apakah ada baris yang terupdate
            if self.cursor.rowcount == 0:
                print(f"⚠️ CLIENT DB: Tidak ada stok bahan baku yang dikurangi untuk Order ID {order_id}. Order mungkin kosong atau resep tidak ditemukan.")
                self.conn.rollback() # Amankan transaksi
                return False
                
            # 3. Commit transaksi agar perubahan stok permanen
            self.conn.commit()
            return True
        
        except psycopg2.Error as e:
            self.conn.rollback() # JIKA GAGAL, KEMBALIKAN SEMUA PERUBAHAN
            print(f"❌ DB Error (deduct_ingredients_for_order): Gagal mengurangi stok! {e}")
            return False
        except Exception as e:
            self.conn.rollback()
            print(f"❌ Error tak terduga saat mengurangi stok: {e}")
            return False

    def __del__(self):
        self.close()