import os
from datetime import datetime

class CustomerView:
    def __init__(self, data_store, customer_data):
        self.data = data_store
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
            products = self.data['products']
            
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
            products = self.data['products']
            
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
            
            # Generate new order ID
            new_order_id = max([o['order_id'] for o in self.data['orders']], default=0) + 1
            
            # Create order
            new_order = {
                'order_id': new_order_id,
                'customer_id': self.customer['customer_id'],
                'order_timestamp': datetime.now(),
                'total_price': total_price,
                'status': 'Menunggu Konfirmasi'
            }
            
            self.data['orders'].append(new_order)
            
            # Add order items
            for item in order_items:
                new_item_id = max([oi['order_item_id'] for oi in self.data['order_items']], default=0) + 1
                new_order_item = {
                    'order_item_id': new_item_id,
                    'order_id': new_order_id,
                    'product_id': item['product_id'],
                    'quantity': item['quantity']
                }
                self.data['order_items'].append(new_order_item)
            
            print(f"\nPesanan berhasil dibuat! (Order ID: {new_order_id})")
            print("Silakan upload bukti pembayaran untuk konfirmasi.")
            input("\nTekan Enter untuk kembali...")
            
        except Exception as e:
            print(f"Error: {e}")
            input("Tekan Enter untuk kembali...")
    
    # ==================== LIHAT DAFTAR PESANAN ====================
    def view_orders(self):
        self.clear_screen()
        print("=" * 50)
        print("DAFTAR PESANAN SAYA")
        print("=" * 50)
        
        try:
            # Filter orders by customer
            my_orders = [o for o in self.data['orders'] if o['customer_id'] == self.customer['customer_id']]
            my_orders.sort(key=lambda x: x['order_timestamp'], reverse=True)
            
            if not my_orders:
                print("\nBelum ada pesanan.")
            else:
                print("\n{:<8} {:<20} {:<15} {:<25}".format("ID", "Tanggal", "Total", "Status"))
                print("-" * 70)
                for o in my_orders:
                    timestamp = o['order_timestamp'].strftime("%d-%m-%Y %H:%M")
                    print("{:<8} {:<20} Rp {:>12,} {:<25}".format(
                        o['order_id'], timestamp, o['total_price'], o['status']))
            
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
            pending_orders = [
                o for o in self.data['orders'] 
                if o['customer_id'] == self.customer['customer_id'] 
                and o['status'] == 'Menunggu Konfirmasi'
            ]
            pending_orders.sort(key=lambda x: x['order_timestamp'], reverse=True)
            
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
            
            order_id = input("\nMasukkan Order ID: ").strip()
            try:
                order_id = int(order_id)
            except ValueError:
                print("ID harus berupa angka!")
                input("Tekan Enter untuk kembali")
                return
            
            # Find order
            order = None
            for o in pending_orders:
                if o['order_id'] == order_id:
                    order = o
                    break
            
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
            print("File berhasil diupload!")
            print("Menunggu konfirmasi admin")
            
            # In real implementation, could add payment_proof field to order
            
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
            
            # Find order
            order = None
            for o in self.data['orders']:
                if o['order_id'] == order_id and o['customer_id'] == self.customer['customer_id']:
                    order = o
                    break
            
            if not order:
                print("Order tidak ditemukan!")
                input("Tekan Enter untuk kembali")
                return
            
            # Get order items
            items = []
            for oi in self.data['order_items']:
                if oi['order_id'] == order_id:
                    product = next((p for p in self.data['products'] if p['product_id'] == oi['product_id']), None)
                    if product:
                        items.append({
                            'product_name': product['product_name'],
                            'quantity': oi['quantity'],
                            'price': product['price']
                        })
            
            # Display
            print("\n" + "=" * 50)
            print(f"ORDER ID: {order['order_id']}")
            print(f"Tanggal: {order['order_timestamp'].strftime('%d-%m-%Y %H:%M')}")
            print(f"Status: {order['status']}")
            print("=" * 50)
            
            print("\nDetail Pesanan:")
            print("-" * 50)
            for item in items:
                print(f"{item['quantity']}x {item['product_name']}")
                print(f"Rp {item['price']:,} x {item['quantity']} = Rp {item['price'] * item['quantity']:,}")
            print("-" * 50)
            print(f"TOTAL: Rp {order['total_price']:,}")
            
            print("\n" + "=" * 50)
            print("Info Penerima:")
            print(f"Nama: {self.customer['fullname']}")
            print(f"Email: {self.customer['email']}")
            print("=" * 50)
            
            # Status timeline
            print("\nStatus Timeline:")
            print("Menunggu Konfirmasi")
            if order['status'] in ['Diproses', 'Dikirim', 'Selesai']:
                print("Diproses")
            if order['status'] in ['Dikirim', 'Selesai']:
                print("Dikirim")
            if order['status'] == 'Selesai':
                print("Selesai")
            
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
            my_orders = [o for o in self.data['orders'] if o['customer_id'] == self.customer['customer_id']]
            my_orders.sort(key=lambda x: x['order_timestamp'], reverse=True)
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
            
            # Find order
            order = None
            for o in my_orders:
                if o['order_id'] == order_id:
                    order = o
                    break
            
            if not order:
                print("Order tidak ditemukan!")
                input("Tekan Enter untuk kembali")
                return
            
            # Get order items
            items = []
            total_price = 0
            for oi in self.data['order_items']:
                if oi['order_id'] == order_id:
                    product = next((p for p in self.data['products'] if p['product_id'] == oi['product_id']), None)
                    if product:
                        items.append({
                            'product_id': product['product_id'],
                            'product_name': product['product_name'],
                            'price': product['price'],
                            'quantity': oi['quantity']
                        })
                        total_price += product['price'] * oi['quantity']
            
            if not items:
                print("Tidak ada item dalam pesanan!")
                input("Tekan Enter untuk kembali")
                return
            
            # Show summary
            print("\n" + "=" * 50)
            print("Detail Pesanan yang akan diulang:")
            print("-" * 50)
            for item in items:
                subtotal = item['price'] * item['quantity']
                print(f"{item['quantity']}x {item['product_name']}")
                print(f"   Rp {item['price']:,} x {item['quantity']} = Rp {subtotal:,}")
            print("-" * 50)
            print(f"TOTAL: Rp {total_price:,}")
            print("=" * 50)
            
            confirm = input("\nUlangi pesanan ini? (y/n): ").strip().lower()
            
            if confirm != 'y':
                print("\nPesanan dibatalkan.")
                input("Tekan Enter untuk kembali")
                return
            
            # Generate new order ID
            new_order_id = max([o['order_id'] for o in self.data['orders']], default=0) + 1
            
            # Create new order
            new_order = {
                'order_id': new_order_id,
                'customer_id': self.customer['customer_id'],
                'order_timestamp': datetime.now(),
                'total_price': total_price,
                'status': 'Menunggu Konfirmasi'
            }
            
            self.data['orders'].append(new_order)
            
            # Copy order items
            for item in items:
                new_item_id = max([oi['order_item_id'] for oi in self.data['order_items']], default=0) + 1
                new_order_item = {
                    'order_item_id': new_item_id,
                    'order_id': new_order_id,
                    'product_id': item['product_id'],
                    'quantity': item['quantity']
                }
                self.data['order_items'].append(new_order_item)
            
            print(f"\nPesanan berhasil diulang! (Order ID: {new_order_id})")
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