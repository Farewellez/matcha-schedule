import os
from datetime import datetime
from ..api.client import DatabaseClient

class CustomerView:
    def __init__(self, db_client: DatabaseClient, customer_data):
        self.db_client = db_client
        self.customer = customer_data
        
    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def display_main_menu(self):
        self.clear_screen()
        print("=" * 50)
        print(f"MENU CUSTOMER - {self.customer['fullname']}")
        print("=" * 50)
        print("\n1. Lihat Produk")
        print("2. Buat Pesanan")
        print("3. Lihat Daftar Pesanan")
        print("4. Upload Bukti Bayar")
        print("5. Lihat Status Pesanan")
        print("6. Repeat Order")
        print("7. Logout")
        print("=" * 50)
    
    # ==================== LIHAT PRODUK ====================
    def view_products(self):
        self.clear_screen()
        print("=" * 50)
        print("         DAFTAR PRODUK")
        print("=" * 50)
        
        try:
            products= self.db_client.fetch_all_products()

            if not products:
                print("\nBelum ada produk tersedia.")
            else:
                print("\n{:<5} {:<30} {:<40} {:<15}".format("ID", "Nama Produk", "Deskripsi", "Harga"))
                print("-" * 90)
                for p in products:
                    desc = (p['description'][:37] + "...") if len(p['description']) > 40 else p['description']
                    print("{:<5} {:<30} {:<40} Rp {:>12,}".format(
                        p['product_id'], p['product_name'][:28], desc, p['price']))
            
            input("\nTekan Enter untuk kembali")
            
        except Exception as e:
            print(f"Error: {e}")
            input("Tekan Enter untuk kembali")
    
    # ==================== BUAT PESANAN ====================
    def create_order(self):
        self.clear_screen()
        print("=" * 50)
        print("BUAT PESANAN")
        print("=" * 50)
        
        try:
            products = self.db_client.fetch_all_products()
            
            if not products:
                print("\nBelum ada produk tersedia.")
                input("Tekan Enter untuk kembali...")
                return
            
            print("\n{:<5} {:<40} {:<15}".format("ID", "Nama Produk", "Harga"))
            print("-" * 60)
            for p in products:
                print("{:<5} {:<40} Rp {:>12,}".format(
                    p['product_id'], p['product_name'][:38], p['price']))
            
            # Input order items
            order_items = []
            total_price = 0
            
            print("\n(Ketik '0' pada ID Produk untuk selesai)")
            
            while True:
                product_id = input("\nID Produk: ").strip()
                
                if product_id == '0':
                    break
                
                try:
                    product_id = int(product_id)
                except ValueError:
                    print("ID harus berupa angka!")
                    continue
                
                # Find product
                product = None
                for p in products:
                    if p['product_id'] == product_id:
                        product = p
                        break
                
                if not product:
                    print("Produk tidak ditemukan!")
                    continue
                
                quantity = input(f"Jumlah {product['product_name']}: ").strip()
                try:
                    quantity = int(quantity)
                    if quantity <= 0:
                        print("Jumlah harus lebih dari 0!")
                        continue
                except ValueError:
                    print("Jumlah harus berupa angka!")
                    continue
                
                # Add to order items
                order_items.append({
                    'product_id': product_id,
                    'product_name': product['product_name'],
                    'price': product['price'],
                    'quantity': quantity,
                    'subtotal': product['price'] * quantity
                })
                total_price += product['price'] * quantity
                
                print(f"{quantity}x {product['product_name']} ditambahkan (Subtotal: Rp {product['price'] * quantity:,})")
            
            if not order_items:
                print("\nPesanan kosong!")
                input("Tekan Enter untuk kembali")
                return
            
            # Show summary
            print("\n" + "=" * 50)
            print("RINGKASAN PESANAN:")
            print("-" * 50)
            for item in order_items:
                print(f"{item['quantity']}x {item['product_name']}")
                print(f"   Rp {item['price']:,} x {item['quantity']} = Rp {item['subtotal']:,}")
            print("-" * 50)
            print(f"TOTAL: Rp {total_price:,}")
            print("=" * 50)
            
            confirm = input("\nKonfirmasi pesanan? (y/n): ").strip().lower()
            
            if confirm != 'y':
                print("\nPesanan dibatalkan.")
                input("Tekan Enter untuk kembali")
                return
            
            deadline_format = "%Y-%m-%d %H:%M"
            # Loop untuk memastikan input deadline valid
            while True:
                deadline_input = input(f"\nMasukkan Deadline Pesanan ({deadline_format}): ").strip()
                try:
                    deadline_object = datetime.strptime(deadline_input, deadline_format)
                    
                    # Tambahkan validasi sederhana: deadline harus di masa depan
                    if deadline_object <= datetime.now():
                        print("❌ Deadline harus di masa depan!")
                        continue
                    break # Keluar dari loop jika valid
                except ValueError:
                    print(f"❌ Format tanggal/waktu salah! Gunakan format {deadline_format}")

            # 1. Hitung total quantity
            total_quantity = sum(item['quantity'] for item in order_items)

            try:
                order_id = self.db_client.create_order_transaction(
                    customer_id=self.customer['customer_id'],
                    total_price=total_price,
                    total_quantity=total_quantity, # <-- BARU!
                    deadline=deadline_object, # deadline object
                    order_items=order_items
                )

                if order_id:
                    print(f"\nPesanan berhasil dibuat dan dimasukkan ke DB! (Order ID: {order_id})")
                    print("Scheduler akan memproses pesanan ini.")
                else:
                    print("\n❌ Gagal membuat pesanan (Database Error).")

            except Exception as e:
                print(f"Error Database saat membuat pesanan: {e}")

        except Exception as e:
            print(e) 
            input("Tekan Enter untuk kembali")

    # ==================== LIHAT DAFTAR PESANAN ====================
    def view_orders(self):
        self.clear_screen()
        print("=" * 50)
        print("DAFTAR PESANAN SAYA")
        print("=" * 50)
        
        try:
            my_orders = self.db_client.fetch_customer_orders(self.customer['customer_id'])
            
            if not my_orders:
                print("\nBelum ada pesanan.")
            else:
                print("\n{:<8} {:<20} {:<15} {:<25}".format("ID", "Tanggal", "Total", "Status"))
                print("-" * 70)
                for o in my_orders:
                    timestamp = o[1].strftime("%d-%m-%Y %H:%M")
                    print("{:<8} {:<20} Rp {:>12,} {:<25}".format(
                        o[0], timestamp, o[2], o[3]))
            
            input("\nTekan Enter untuk kembali")
            
        except Exception as e:
            print(f"Error: {e}")
            input("Tekan Enter untuk kembali")
    
    # ==================== UPLOAD BUKTI BAYAR ====================
    def upload_payment_proof(self):
        self.clear_screen()
        print("=" * 50)
        print("UPLOAD BUKTI BAYAR")
        print("=" * 50)
        
        try:
            # Get pending orders
            pending_orders_raw = self.db_client.fetch_pending_orders_by_customer(self.customer['customer_id'])
            pending_orders = [
                {'order_id': r[0], 'order_timestamp': r[1], 'total_price': r[2], 'status': r[3]}
                for r in pending_orders_raw
            ]

            # pending_orders.sort(key=lambda x: x['order_timestamp'], reverse=True)
            
            if not pending_orders:
                print("\nTidak ada pesanan yang menunggu konfirmasi.")
                input("Tekan Enter untuk kembali")
                return
            
            print("\nPesanan yang menunggu konfirmasi:")
            print("-" * 60)
            print("{:<8} {:<20} {:<15}".format("ID", "Tanggal", "Total"))
            print("-" * 60)

            for o in pending_orders:
                timestamp = o['order_timestamp'].strftime("%d-%m-%Y %H:%M")
                print("{:<8} {:<20} Rp {:>12,}".format(o['order_id'], timestamp, o['total_price']))
            
            order_id_input = input("\nMasukkan Order ID: ").strip()
            
            try:
                order_id = int(order_id_input)
            except ValueError:
                print("ID harus berupa angka!")
                input("Tekan Enter untuk kembali")
                return
            
            # Find order
            order = next((o for o in pending_orders if o['order_id'] == order_id), None)
            # for o in pending_orders:
            #     if o['order_id'] == order_id:
            #         order = o
            #         break
            
            if not order:
                print("Order tidak ditemukan atau sudah dikonfirmasi!")
                input("Tekan Enter untuk kembali")
                return
            
            # Mock upload
            print(f"\nOrder ID: {order['order_id']}")
            print(f"Total: Rp {order['total_price']:,}")
            filename = input("\nNama file bukti bayar (contoh: bukti_bayar.jpg): ").strip()
            
            if not filename:
                print("Nama file tidak boleh kosong!")
                input("Tekan Enter untuk kembali")
                return
            
            # Mock upload process
            print("\nUploading file")
            # print("File berhasil diupload!")
            # print("Menunggu konfirmasi admin")
            
            # # In real implementation, could add payment_proof field to order
            # Update status pesanan di DB menjadi 'Diproses' (Asumsi status_id = 2)
            if self.db_client.update_order_status(order_id, 2):
                print("✅ Pembayaran berhasil dikonfirmasi!")
                print("Status pesanan diperbarui menjadi 'Diproses'.")
                print("Scheduler akan mulai menghitung prioritas dan menjadwalkan produksi.")
            else:
                print("❌ Gagal memperbarui status di database.")

            input("\nTekan Enter untuk kembali")
            
        except Exception as e:
            print(f"Error: {e}")
            input("Tekan Enter untuk kembali")
    
    # ==================== LIHAT STATUS PESANAN ====================
    def view_order_status(self):
        self.clear_screen()
        print("=" * 50)
        print("STATUS PESANAN")
        print("=" * 50)
        
        try:
            order_id = input("\nMasukkan Order ID: ").strip()
            try:
                order_id = int(order_id)
            except ValueError:
                print("ID harus berupa angka!")
                input("Tekan Enter untuk kembali")
                return
            
            # --- Perbaikan 1: Ambil data dari DB ---
            order_data = self.db_client.fetch_order_details_by_id(order_id, self.customer['customer_id'])

            if not order_data:
                print("Order tidak ditemukan!")
                input("Tekan Enter untuk kembali")
                return
            
            # Pisahkan hasil dari DB
            # order_header: (order_id, order_timestamp, total_price, status_name, deadline)
            order_header, items_raw = order_data
            
            # Konversi item untuk tampilan:
            items = [
                {'product_name': r[0], 'quantity': r[1], 'price': r[2]}
                for r in items_raw
            ]
            
            # Display
            print("\n" + "=" * 50)
            print(f"ORDER ID: {order_header[0]}")
            print(f"Tanggal Pesan: {order_header[1].strftime('%d-%m-%Y %H:%M')}")
            print(f"Status: {order_header[3]}")
            print(f"DEADLINE: {order_header[4].strftime('%d-%m-%Y %H:%M')}") # Tambah Deadline
            print("=" * 50)
            
            print("\nDetail Pesanan:")
            print("-" * 50)
            for item in items:
                print(f"{item['quantity']}x {item['product_name']}")
                print(f"Rp {item['price']:,} x {item['quantity']} = Rp {item['price'] * item['quantity']:,}")
            print("-" * 50)
            print(f"TOTAL: Rp {order_header['total_price']:,}")
            
            print("\n" + "=" * 50)
            print("Info Penerima:")
            print(f"Nama: {self.customer['fullname']}")
            print(f"Email: {self.customer['email']}")
            print("=" * 50)
            
            # 3. Status Timeline
            # Timeline menggunakan status_name (order_header[3])
            current_status = order_header[3]
            print("\nStatus Timeline:")

            # Cek status berikutnya (Diproses)
            if current_status in ['Diproses', 'Dikirim', 'Selesai']:
                print(f"✅ Diproses (Sedang diproduksi oleh Scheduler)")
            elif current_status == 'Menunggu Konfirmasi':
                print("   Diproses")
            
            # Cek status berikutnya (Dikirim)
            if current_status in ['Dikirim', 'Selesai']:
                print("✅ Dikirim")
            elif current_status in ['Menunggu Konfirmasi', 'Diproses']:
                print("   Dikirim")

            # Cek status terakhir (Selesai)
            if current_status == 'Selesai':
                print("✅ Selesai (Pesanan diterima)")
            
            input("\nTekan Enter untuk kembali")
            
        except Exception as e:
            print(f"Error: {e}")
            input("Tekan Enter untuk kembali")
    
    # ==================== REPEAT ORDER ====================
    def repeat_order(self):
        self.clear_screen()
        print("=" * 50)
        print("REPEAT ORDER")
        print("=" * 50)
        
        try:
            # Get customer orders
            my_orders_raw = self.db_client.fetch_customer_orders(self.customer['customer_id'])
            my_orders = [
                {'order_id': r[0], 'order_timestamp': r[1], 'total_price': r[2], 'status': r[3]}
                for r in my_orders_raw
            ]
            my_orders = my_orders[:10]  
            
            if not my_orders:
                print("\nBelum ada riwayat pesanan.")
                input("Tekan Enter untuk kembali...")
                return
            
            print("\nRiwayat Pesanan:")
            print("-" * 70)
            print("{:<8} {:<20} {:<15} {:<25}".format("ID", "Tanggal", "Total", "Status"))
            print("-" * 70)

            for o in my_orders:
                timestamp = o['order_timestamp'].strftime("%d-%m-%Y %H:%M")
                print("{:<8} {:<20} Rp {:>12,} {:<25}".format(
                    o['order_id'], timestamp, o['total_price'], o['status']))
            
            order_id = input("\nMasukkan Order ID yang ingin diulang: ").strip()
            
            try:
                order_id = int(order_id)
            except ValueError:
                print("ID harus berupa angka!")
                input("Tekan Enter untuk kembali")
                return
            
            # --- 2. AMBIL DETAIL ITEM DARI DB UNTUK PESANAN YANG DIPILIH ---
            
            # Kita panggil fetch_order_details_by_id (meski kita hanya pakai bagian Items)
            # Kita perlu customer_id untuk memastikan order ID ini valid milik customer
            order_data = self.db_client.fetch_order_details_by_id(order_id, self.customer['customer_id'])
            
            if not order_data:
                print("Order tidak ditemukan!")
                input("Tekan Enter untuk kembali")
                return
            
            order_header, items_raw = order_data

            # Format item dan hitung ulang Total Price & Total Quantity untuk pesanan BARU
            items_to_repeat = []
            items_to_insert = []
            new_total_price = 0
            new_total_quantity = 0

            # Loop untuk menghitung total dan menyiapkan list insert
            for p_id, p_name, quantity, price in items_raw:
                 # Siapkan data untuk tampilan
                 items_to_repeat.append({
                    'product_name': p_name,
                    'price': price,
                    'quantity': quantity
                })
                 # Siapkan data untuk insert (hanya ID dan Kuantitas)
                 items_to_insert.append({
                    'product_id': p_id, 
                    'quantity': quantity 
                })
                 new_total_price += price * quantity
                 new_total_quantity += quantity
            
            if not items_to_repeat:
                print("Tidak ada item dalam pesanan!")
                input("Tekan Enter untuk kembali")
                return
            
            if not items_to_repeat:
                print("Tidak ada item dalam pesanan!")
                input("Tekan Enter untuk kembali")
                return
            
            # Show summary
            print("\n" + "=" * 50)
            print("Detail Pesanan yang akan diulang:")
            print("-" * 50)
            for item in items_to_repeat:
                subtotal = item['price'] * item['quantity']
                print(f"{item['quantity']}x {item['product_name']}")
                print(f"   Rp {item['price']:,} x {item['quantity']} = Rp {subtotal:,}")
            print("-" * 50)
            print(f"TOTAL: Rp {new_total_price:,}")
            print("=" * 50)
            
            confirm = input("\nUlangi pesanan ini? (y/n): ").strip().lower()
            
            if confirm != 'y':
                print("\nPesanan dibatalkan.")
                input("Tekan Enter untuk kembali")
                return
            
            # --- Logika Insert ke DB (Menggantikan 7 baris dummy di bagian akhir) ---
            
            # Perlu input deadline lagi untuk pesanan baru
            deadline_format = "%Y-%m-%d %H:%M"
            while True:
                deadline_input = input(f"\nMasukkan Deadline Pesanan BARU ({deadline_format}): ").strip()
                try:
                    deadline_object = datetime.strptime(deadline_input, deadline_format)
                    if deadline_object <= datetime.now():
                        print("❌ Deadline harus di masa depan!")
                        continue
                    break
                except ValueError:
                    print(f"❌ Format tanggal/waktu salah!")

            try:
                # Panggil DB Client yang transaksional untuk membuat pesanan baru
                new_order_id = self.db_client.create_order_transaction(
                    customer_id=self.customer['customer_id'],
                    total_price=new_total_price,
                    total_quantity=new_total_quantity, 
                    deadline=deadline_object, 
                    order_items=items_to_insert # <-- Mengandung product_id dan quantity
                )

                if new_order_id:
                    print(f"\nPesanan berhasil diulang dan dimasukkan ke DB! (Order ID: {new_order_id})")
                    print("Scheduler akan memproses pesanan ini.")
                else:
                    print("\n❌ Gagal mengulang pesanan (Database Error).")

            except Exception as e:
                print(f"Error Database saat memproses transaksi: {e}")
            
            print("Silakan upload bukti pembayaran untuk konfirmasi.")
            input("\nTekan Enter untuk kembali")
            
        except Exception as e:
            print(f"Error: {e}")
            input("Tekan Enter untuk kembali")
    
    def run(self):
        while True:
            self.display_main_menu()
            choice = input("\nPilih menu (1-7): ").strip()
            
            if choice == '1':
                self.view_products()
            elif choice == '2':
                self.create_order()
            elif choice == '3':
                self.view_orders()
            elif choice == '4':
                self.upload_payment_proof()
            elif choice == '5':
                self.view_order_status()
            elif choice == '6':
                self.repeat_order()
            elif choice == '7':
                print("\nLogout berhasil!")
                input("Tekan Enter untuk kembali ke menu login")
                break
            else:
                print("Pilihan tidak valid!")
                input("Tekan Enter untuk kembali")