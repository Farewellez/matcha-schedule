import os
from ..api.client import DatabaseClient

class AdminView:
    def __init__(self, db_client: DatabaseClient, admin_data):
        self.db_client = db_client
        self.admin = admin_data
        
    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def display_main_menu(self):
        self.clear_screen()
        print("=" * 50)
        print(f"     ADMIN PANEL - {self.admin['username']}")
        print("=" * 50)
        print("\n1. Kelola Produk")
        print("2. Kelola Bahan Baku")
        print("3. Lihat Stok & Alert")
        print("4. Laporan")
        print("5. Logout")
        print("=" * 50)
    
    # ==================== MANAGE PRODUK ====================
    def manage_product_menu(self):
        while True:
            self.clear_screen()
            print("=" * 50)
            print("         KELOLA PRODUK")
            print("=" * 50)
            print("\n1. Lihat Semua Produk")
            print("2. Tambah Produk")
            print("3. Edit Produk")
            print("4. Hapus Produk")
            print("5. Kembali")
            print("=" * 50)
            
            choice = input("\nPilih menu (1-5): ").strip()
            
            if choice == '1':
                self.view_products()
            elif choice == '2':
                self.add_product()
            elif choice == '3':
                self.edit_product()
            elif choice == '4':
                self.delete_product()
            elif choice == '5':
                break
            else:
                print("Pilihan tidak valid!")
                input("Tekan Enter untuk kembali")
    
    def view_products(self):
        self.clear_screen()
        print("=" * 50)
        print("DAFTAR PRODUK")
        print("=" * 50)
        
        try:
            products = self.db_client.fetch_all_products()
            
            if not products:
                print("\nBelum ada produk.")
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

    def _display_products_list(self): 
        # Salin semua logika tampilan produk dari view_products di sini

        # PASTIKAN HANYA ADA LOGIKA TAMPILAN, TIDAK ADA INPUT()s
        try:
            products = self.db_client.fetch_all_products()
            if products:
                print("\n" + "=" * 50)
                print("DAFTAR PRODUK YANG SUDAH ADA:")
                print("{:<5} {:<30} {:<15}".format("ID", "Nama Produk", "Harga"))
                print("-" * 50)
                for p in products:
                    print("{:<5} {:<30} Rp {:>12,}".format(p['product_id'], p['product_name'][:28], p['price']))
                print("-" * 50)
        
        except Exception as e:
            # Jika ada error, cukup tampilkan error tanpa input jeda
            print(f"Error saat menampilkan daftar produk: {e}")
        
    def add_product(self):
        self.clear_screen()
        print("=" * 50)
        print("TAMBAH PRODUK")
        print("=" * 50)
        
        try:
            # --- SARAN TIM TESTING 1: TAMPILKAN PRODUK YANG ADA ---
            self._display_products_list() # Re-use fungsi yang sudah ada (atau tampilkan secara ringkas)
            print("\n" + "=" * 50)

            # --- SARAN TIM TESTING 2: TAMPILKAN BAHAN BAKU (ID, NAMA, UNIT, STOK) ---
            print("DAFTAR BAHAN BAKU (untuk resep):")
            ingredients = self.db_client.fetch_all_ingredients()
            if ingredients:
                print("\n{:<5} {:<30} {:<10} {:<10}".format("ID", "Nama Bahan", "Unit", "Stok"))
                print("-" * 55)
                for ing in ingredients:
                    print("{:<5} {:<30} {:<10} {:<10}".format(
                        ing['ingredient_id'], ing['ingredient_name'][:28], 
                        ing['unit'], ing['stock']))
                print("-" * 55)
            else:
                print("❌ Belum ada Bahan Baku. Harap tambah di Kelola Bahan Baku terlebih dahulu!")
                input("Tekan Enter untuk kembali")
                return # Tidak bisa lanjut jika tidak ada bahan baku
            
            name = input("\nNama Produk: ").strip()
            if not name:
                print("Nama produk tidak boleh kosong!")
                input("Tekan Enter untuk kembali")
                return
            
            description = input("Deskripsi: ").strip()
            if not description:
                print("Deskripsi tidak boleh kosong!")
                input("Tekan Enter untuk kembali")
                return
            
            price = input("Harga: ").strip()
            try:
                price = int(price)
                if price <= 0:
                    print("Harga harus lebih dari 0!")
                    input("Tekan Enter untuk kembali...")
                    return
            except ValueError:
                print("Harga harus berupa angka!")
                input("Tekan Enter untuk kembali...")
                return
            
            # --- INPUT RESEP ---
            print("\n" + "=" * 50)
            print("INPUT RESEP (Bahan Baku & Kuantitas)")
            print("Tekan Enter di ID Bahan jika sudah selesai.")

            recipe = [] # List untuk menyimpan pasangan (ingredient_id, quantity)
            while True:
                ing_id_input = input(f"Masukkan ID Bahan ke-{len(recipe) + 1}: ").strip()
                
                if not ing_id_input:
                    break # Keluar dari loop input resep
                    
                try:
                    ing_id = int(ing_id_input)
                    
                    # Cek keberadaan bahan baku
                    ingredient = self.db_client.get_ingredient_by_id(ing_id)
                    if not ingredient:
                        print("❌ ID Bahan Baku tidak ditemukan! Cek daftar di atas.")
                        continue # Lanjut ke input ID berikutnya
                        
                    print(f"Bahan: {ingredient['ingredient_name']} ({ingredient['unit']})")
                    
                    quantity_input = input(f"Kuantitas ({ingredient['unit']}): ").strip()
                    quantity = int(quantity_input)
                    
                    if quantity <= 0:
                        print("Kuantitas harus positif!")
                        continue
                        
                    # Simpan resep
                    recipe.append((ing_id, quantity))
                    
                except ValueError:
                    print("Input harus berupa angka!")
                    continue
                except Exception as e:
                    print(f"Error saat input resep: {e}")
                    continue
            
            if not recipe:
                print("⚠️ Produk tidak memiliki resep. Pembatalan penambahan produk.")
                input("Tekan Enter untuk kembali...")
                return
            
            new_id = self.db_client.add_new_product_with_recipe(name, description, price, recipe) 
            
            if new_id:
                print("\nProduk berhasil ditambahkan!")
                print(f"ID Produk Baru: {new_id}")
                # Logika Tampilan Resep yang baru ditambahkan (Opsional)
            else:
                print("\nProduk GAGAL ditambahkan! Cek error database.")

            input("Tekan Enter untuk kembali...")
            
        except Exception as e:
            print(f"Error: {e}")
            input("Tekan Enter untuk kembali")
    
    def edit_product(self):
        self.clear_screen()
        print("=" * 50)
        print("EDIT PRODUK")
        print("=" * 50)
        
        self._display_products_list()
        self._display_ingredients_list()

        try:
            product_id = input("\nMasukkan ID Produk: ").strip()
            try:
                product_id = int(product_id)
            except ValueError:
                print("ID harus berupa angka!")
                input("Tekan Enter untuk kembali")
                return
            
            product = self.db_client.get_product_by_id(product_id)
            
            if not product:
                print("Produk tidak ditemukan!")
                input("Tekan Enter untuk kembali")
                return
            
            print(f"\nProduk saat ini:")
            print(f"Nama: {product['product_name']}")
            print(f"Deskripsi: {product['description']}")
            print(f"Harga: Rp {product['price']:,}")
            print("\n(Kosongkan jika tidak ingin mengubah)")
            
            name = input("\nNama Produk baru: ").strip() or product['product_name']
            description = input("Deskripsi baru: ").strip() or product['description']
            price_input = input("Harga baru: ").strip()
            
            if price_input:
                try:
                    price = int(price_input)
                    if price <= 0:
                        print("Harga harus lebih dari 0!")
                        input("Tekan Enter untuk kembali")
                        return
                except ValueError:
                    print("Harga harus berupa angka!")
                    input("Tekan Enter untuk kembali")
                    return
            else:
                price = product['price']
            
            is_updated = self.db_client.update_product(
                product_id, name, description, price
            )
            
            if is_updated:
                print("\nProduk berhasil diupdate!")
            else:
                print("\nProduk GAGAL diupdate. Cek error database.")
            
            input("Tekan Enter untuk kembali")
            
        except Exception as e:
            print(f"Error: {e}")
            input("Tekan Enter untuk kembali")
    
    def delete_product(self):
        self.clear_screen()
        print("=" * 50)
        print("HAPUS PRODUK")
        print("=" * 50)
        
        self._display_products_list()
        self._display_ingredients_list()

        try:
            product_id = input("\nMasukkan ID Produk: ").strip()
            try:
                product_id = int(product_id)
            except ValueError:
                print("ID harus berupa angka!")
                input("Tekan Enter untuk kembali")
                return
            
            product = self.db_client.get_product_by_id(product_id)
            
            if not product:
                print("Produk tidak ditemukan!")
                input("Tekan Enter untuk kembali")
                return
            
            confirm = input(f"\nHapus produk '{product['product_name']}'? (y/n): ").strip().lower()
            
            if confirm == 'y':
                is_deleted = self.db_client.delete_product_and_relations(product_id)
                if is_deleted:
                    print("\nProduk berhasil dihapus!")
                else:
                    print("\nProduk GAGAL dihapus! Cek database atau ID.")
            else:
                print("\nPenghapusan dibatalkan.")
            
            input("Tekan Enter untuk kembali")
            
        except Exception as e:
            print(f"Error: {e}")
            input("Tekan Enter untuk kembali")
    
    # ==================== MANAGE BAHAN BAKU ====================
    def manage_ingredient_menu(self):
        while True:
            self.clear_screen()
            print("=" * 50)
            print("       KELOLA BAHAN BAKU")
            print("=" * 50)
            print("\n1. Lihat Semua Bahan Baku")
            print("2. Tambah Bahan Baku")
            print("3. Edit Bahan Baku")
            print("4. Update Stok")
            print("5. Hapus Bahan Baku")
            print("6. Kembali")
            print("=" * 50)
            
            choice = input("\nPilih menu (1-6): ").strip()
            
            if choice == '1':
                self.view_ingredients()
            elif choice == '2':
                self.add_ingredient()
            elif choice == '3':
                self.edit_ingredient()
            elif choice == '4':
                self.update_stock()
            elif choice == '5':
                self.delete_ingredient()
            elif choice == '6':
                break
            else:
                print("Pilihan tidak valid!")
                input("Tekan Enter untuk kembali")
    
    def view_ingredients(self):
        self.clear_screen()
        print("=" * 50)
        print("DAFTAR BAHAN BAKU")
        print("=" * 50)
        
        try:
            ingredients = self.db_client.fetch_all_ingredients()
            
            if not ingredients:
                print("\nBelum ada bahan baku.")
            else:
                print("\n{:<5} {:<25} {:<10} {:<15} {:<15}".format("ID", "Nama Bahan", "Unit", "Stok", "Min. Stok"))
                print("-" * 70)
                for ing in ingredients:
                    status = "" if ing['stock'] <= ing['minimum_stock'] else ""
                    print("{:<5} {:<25} {:<10} {}{:<14} {:<15}".format(
                        ing['ingredient_id'], ing['ingredient_name'][:23], 
                        ing['unit'], status, ing['stock'], ing['minimum_stock']))
            
            input("\nTekan Enter untuk kembali")
            
        except Exception as e:
            print(f"Error: {e}")
            input("Tekan Enter untuk kembali")
    
    def add_ingredient(self):
        self.clear_screen()
        print("=" * 50)
        print("TAMBAH BAHAN BAKU")
        print("=" * 50)
        
        self._display_ingredients_list()

        try:
            name = input("\nNama Bahan: ").strip()
            if not name:
                print("Nama bahan tidak boleh kosong!")
                input("Tekan Enter untuk kembali")
                return
            
            # Check if ingredient already exists (case insensitive)
            existing_ingredient = self.db_client.check_ingredient_exists(name)
            
            if existing_ingredient:
                
                ing_id = existing_ingredient['ingredient_id']
                current_stock = existing_ingredient['stock']
                ing_unit = existing_ingredient['unit']

                print(f"\nBahan '{existing_ingredient['ingredient_name']}' sudah ada!")
                print(f"Stok saat ini: {current_stock} {ing_unit}")                
                
                add_stock = input("\nTambah stok ke bahan yang sudah ada? (y/n): ").strip().lower()
                
                if add_stock == 'y':
                    additional_stock = input(f"Jumlah stok yang ditambahkan: ").strip()
                    try:
                        additional_stock = int(additional_stock)
                        if additional_stock < 0:
                            print("Jumlah tidak boleh negatif!")
                            input("Tekan Enter untuk kembali...")
                            return
                        
                        if self.db_client.update_ingredient_stock(ing_id, additional_stock):
                            new_stock = current_stock + additional_stock
                            print(f"\nStok berhasil ditambahkan!")
                            print(f"Stok baru: {new_stock} {ing_unit}")
                        else:
                             print("\nStok GAGAL ditambahkan! Cek koneksi DB.")
                        
                        input("Tekan Enter untuk kembali...")
                        return

                    except ValueError:
                        print("Jumlah harus berupa angka!")
                        input("Tekan Enter untuk kembali...")
                        return
                else:
                    print("\nPenambahan dibatalkan.")
                    input("Tekan Enter untuk kembali...")
                    return
            
            # If ingredient doesn't exist, create new one
            unit = input("Unit (gram/ml/pcs): ").strip()
            if not unit:
                print("Unit tidak boleh kosong!")
                input("Tekan Enter untuk kembali")
                return
            
            stock = input("Stok awal: ").strip()
            try:
                stock = int(stock)
                if stock < 0:
                    print("Stok tidak boleh negatif!")
                    input("Tekan Enter untuk kembali")
                    return
            except ValueError:
                print("Stok harus berupa angka!")
                input("Tekan Enter untuk kembali")
                return
            
            min_stock = input("Minimum stok: ").strip()
            try:
                min_stock = int(min_stock)
                if min_stock < 0:
                    print("Minimum stok tidak boleh negatif!")
                    input("Tekan Enter untuk kembali")
                    return
            except ValueError:
                print("Minimum stok harus berupa angka!")
                input("Tekan Enter untuk kembali")
                return
            
            new_id = self.db_client.add_new_ingredient(name, unit, stock, min_stock)

            if new_id:
                print("\nBahan baku berhasil ditambahkan!")
                print(f"ID Bahan Baku Baru: {new_id}")
            else:
                 print("\nBahan baku GAGAL ditambahkan! Cek error database.")
                        
            input("Tekan Enter untuk kembali")
            
        except Exception as e:
            print(f"Error: {e}")
            input("Tekan Enter untuk kembali")
    
    def _display_ingredients_list(self): 
        """Menampilkan daftar ID, Nama, Stok, dan Min. Stok Bahan Baku tanpa jeda input."""
        try:
            ingredients = self.db_client.fetch_all_ingredients()

            if ingredients:
                print("\n" + "=" * 50)
                print("DAFTAR BAHAN BAKU SAAT INI (ID diperlukan untuk edit):")
                print("{:<5} {:<30} {:<10} {:<10}".format("ID", "Nama Bahan", "Stok", "Min. Stok"))
                print("-" * 55)
                for ing in ingredients:
                    print("{:<5} {:<30} {:<10} {:<10}".format(
                        ing['ingredient_id'], ing['ingredient_name'][:28], 
                        ing['stock'], ing['minimum_stock']))
                print("-" * 55)
            else:
                print("Belum ada bahan baku.")

        except Exception as e:
            print(f"Error saat menampilkan daftar bahan baku: {e}")

    def edit_ingredient(self):
        self.clear_screen()
        print("=" * 50)
        print("EDIT BAHAN BAKU")
        print("=" * 50)

        self._display_ingredients_list()
        
        try:
            ing_id = input("\nMasukkan ID Bahan: ").strip()
            try:
                ing_id = int(ing_id)
            except ValueError:
                print("ID harus berupa angka!")
                input("Tekan Enter untuk kembali")
                return
            
            # Find ingredient
            ingredient = self.db_client.get_ingredient_by_id(ing_id)
            
            if not ingredient:
                print("Bahan baku tidak ditemukan!")
                input("Tekan Enter untuk kembali")
                return
            
            print(f"\nBahan saat ini:")
            print(f"Nama: {ingredient['ingredient_name']}")
            print(f"Unit: {ingredient['unit']}")
            print(f"Minimum Stok: {ingredient['minimum_stock']}")
            print("\n(Kosongkan jika tidak ingin mengubah)")
            
            name = input("\nNama Bahan baru: ").strip() or ingredient['ingredient_name']
            unit = input("Unit baru: ").strip() or ingredient['unit']
            min_stock_input = input("Minimum stok baru: ").strip()
            
            if min_stock_input:
                try:
                    min_stock = int(min_stock_input)
                    if min_stock < 0:
                        print("Minimum stok tidak boleh negatif!")
                        input("Tekan Enter untuk kembali")
                        return
                except ValueError:
                    print("Minimum stok harus berupa angka!")
                    input("Tekan Enter untuk kembali")
                    return
            else:
                min_stock = ingredient['minimum_stock']
            
            is_updated = self.db_client.update_ingredient_details(
                ing_id, name, unit, min_stock
            )

            if is_updated:
                print("\nBahan baku berhasil diupdate!")
            else:
                print("\nBahan baku GAGAL diupdate. Cek error database.")

            input("Tekan Enter untuk kembali")

        except Exception as e:
            print(f"Error: {e}")
            input("Tekan Enter untuk kembali")
    
    def update_stock(self):
        self.clear_screen()
        print("=" * 50)
        print("UPDATE STOK")
        print("=" * 50)
        
        self._display_ingredients_list()

        try:
            ing_id = input("\nMasukkan ID Bahan: ").strip()
            try:
                ing_id = int(ing_id)
            except ValueError:
                print("ID harus berupa angka!")
                input("Tekan Enter untuk kembali")
                return
            
            # Find ingredient
            ingredient = self.db_client.get_ingredient_by_id(ing_id)
            
            if not ingredient:
                print("Bahan baku tidak ditemukan!")
                input("Tekan Enter untuk kembali")
                return
            
            print(f"\nBahan: {ingredient['ingredient_name']}")
            print(f"Stok saat ini: {ingredient['stock']}")
            
            change_amount_input = input("\nMasukkan Jumlah Penambahan/Pengurangan (e.g., 500 atau -760): ").strip()
            if not change_amount_input:
                print("Pembatalan update stok.")
                input("Tekan Enter untuk kembali")
                return
            
            try:
                change_amount = int(change_amount_input) 
        
                 # HITUNG STOK AKHIR: Stok Lama + Perubahan
                final_stock = ingredient['stock'] + change_amount
        
                if final_stock < 0:
                    print("Stok tidak boleh negatif! (Stok saat ini:", ingredient['stock'], ")")
                    input("Tekan Enter untuk kembali")
                    return
                
                is_updated = self.db_client.adjust_ingredient_stock(ing_id, change_amount)

                if is_updated:
                    print("\nStok berhasil diupdate!")
                else:
                    print("\nStok GAGAL diupdate. Cek error database.")
                    
            except ValueError:
                print("Stok harus berupa angka!")
                input("Tekan Enter untuk kembali")
                return

            input("Tekan Enter untuk kembali")
            
        except Exception as e:
            print(f"Error: {e}")
            input("Tekan Enter untuk kembali")
    
    def delete_ingredient(self):
        self.clear_screen()
        print("=" * 50)
        print("HAPUS BAHAN BAKU")
        print("=" * 50)
        
        self._display_ingredients_list()

        try:
            ing_id = input("\nMasukkan ID Bahan: ").strip()
            try:
                ing_id = int(ing_id)
            except ValueError:
                print("ID harus berupa angka!")
                input("Tekan Enter untuk kembali")
                return
            
            # Find ingredient
            ingredient = self.db_client.get_ingredient_by_id(ing_id)
            
            if not ingredient:
                print("Bahan baku tidak ditemukan!")
                input("Tekan Enter untuk kembali")
                return
            
            confirm = input(f"\n⚠️  Hapus bahan '{ingredient['ingredient_name']}'? (y/n): ").strip().lower()
            
            if confirm == 'y':
                is_deleted = self.db_client.delete_ingredient_and_relations(ing_id)                
                if is_deleted:
                    print("\nBahan baku dan semua relasi resep yang terkait berhasil dihapus!")
                else:
                    print("\nBahan baku GAGAL dihapus! Cek database atau ID.")
            else:
                print("\nPenghapusan dibatalkan.")
            
            input("Tekan Enter untuk kembali")
            
        except Exception as e:
            print(f"Error: {e}")
            input("Tekan Enter untuk kembali")
    
    # ==================== STOCK & ALERT ====================
    def view_stock_alert(self):
        self.clear_screen()
        print("=" * 50)
        print("STOK & ALERT BAHAN BAKU")
        print("=" * 50)
        
        try:
            ingredients_raw = self.db_client.fetch_all_ingredients() 
            ingredients = sorted(ingredients_raw, key=lambda x: x['stock'])

            if not ingredients:
                print("\nBelum ada data bahan baku.")
                input("\nTekan Enter untuk kembali")
                return
            
            low_stock = [ing for ing in ingredients if ing['stock'] <= ing['minimum_stock']]
            
            if low_stock:
                print("\nALERT - Stok Menipis:")
                print("-" * 70)
                print("{:<5} {:<25} {:<10} {:<15} {:<15}".format("ID", "Nama Bahan", "Unit", "Stok", "Min. Stok"))
                print("-" * 70)
                for ing in low_stock:
                    print("{:<5} {:<25} {:<10} {:<15} {:<15}".format(
                        ing['ingredient_id'], ing['ingredient_name'][:23], 
                        ing['unit'], ing['stock'], ing['minimum_stock']))
            else:
                print("\nSemua stok aman!")
            
            print("\n" + "=" * 50)
            print("SEMUA BAHAN BAKU:")
            print("-" * 70)
            print("{:<5} {:<25} {:<10} {:<15} {:<15}".format("ID", "Nama Bahan", "Unit", "Stok", "Min. Stok"))
            print("-" * 70)
            for ing in ingredients:
                status = "" if ing['stock'] <= ing['minimum_stock'] else ""
                print("{:<5} {:<25} {:<10} {}{:<14} {:<15}".format(
                    ing['ingredient_id'], ing['ingredient_name'][:23], 
                    ing['unit'], status, ing['stock'], ing['minimum_stock']))
            
            input("\nTekan Enter untuk kembali")
            
        except Exception as e:
            print(f"Error: {e}")
            input("Tekan Enter untuk kembali")
    
    # ==================== LAPORAN ====================
    def view_reports(self):
        while True:
            self.clear_screen()
            print("=" * 50)
            print("LAPORAN")
            print("=" * 50)
            print("\n1. Produk Paling Banyak Dipesan")
            print("2. Stok Bahan Baku Menipis")
            print("3. Kembali")
            print("=" * 50)
            
            choice = input("\nPilih menu (1-3): ").strip()
            
            if choice == '1':
                self.report_popular_products()
            elif choice == '2':
                self.report_low_stock()
            elif choice == '3':
                break
            else:
                print("Pilihan tidak valid!")
                input("Tekan Enter untuk kembali")
    
    def report_popular_products(self):
        self.clear_screen()
        print("=" * 50)
        print("PRODUK PALING BANYAK DIPESAN")
        print("=" * 50)
        
        try:
            # Calculate total ordered per product
            popular_products = self.db_client.get_popular_products(limit=10)        

            if not popular_products:
                print("\nBelum ada data pesanan.")
            else:
                # # Get product names and sort
                # product_list = []
                # for product_id, total in product_list.items():
                #     product = next((p for p in self.db_client['products'] if p['product_id'] == product_id), None)
                #     if product:
                #         product_list.append({
                #             'name': product['product_name'],
                #             'total': total
                #         })
                print("\n{:<5} {:<40} {:<15}".format("No", "Nama Produk", "Total Dipesan"))
                print("-" * 60)
                
                # popular_products.sort(key=lambda x: x['total'], reverse=True)
                
                # print("\n{:<5} {:<40} {:<15}".format("No", "Nama Produk", "Total Dipesan"))
                # print("-" * 60)
                # for idx, p in enumerate(product_list[:10], 1):
                #     print("{:<5} {:<40} {:<15}".format(idx, p['name'][:38], p['total']))
                for idx, p in enumerate(popular_products, 1):
                    print("{:<5} {:<40} {:<15}".format(
                        idx, 
                        p['product_name'][:38], # Menggunakan kunci dari DB
                        p['total_ordered']))    # Menggunakan kunci dari DB
            
            input("\nTekan Enter untuk kembali")
            
        except Exception as e:
            print(f"Error: {e}")
            input("Tekan Enter untuk kembali")
    
    def report_low_stock(self):
        self.clear_screen()
        print("=" * 50)
        print("STOK BAHAN BAKU MENIPIS")
        print("=" * 50)
        
        try:
            # low_stock = [
            #     ing for ing in self.data['ingredients'] 
            #     if ing['stock'] <= ing['minimum_stock']
            # ]
            
            low_stock = self.db_client.get_low_stock_ingredients()            
            
            if not low_stock:
                print("\nSemua stok bahan baku aman!")
            else:
                print("\n{:<30} {:<10} {:<15} {:<15}".format("Nama Bahan", "Unit", "Stok", "Min. Stok"))
                print("-" * 70)
                for ing in low_stock:
                    print("{:<30} {:<10} {:<15} {:<15}".format(
                        ing['ingredient_name'][:28], ing['unit'], 
                        ing['stock'], ing['minimum_stock']))
            
            input("\nTekan Enter untuk kembali")
            
        except Exception as e:
            print(f"Error: {e}")
            input("Tekan Enter untuk kembali")
    
    def run(self):
        while True:
            self.display_main_menu()
            choice = input("\nPilih menu (1-5): ").strip()
            
            if choice == '1':
                self.manage_product_menu()
            elif choice == '2':
                self.manage_ingredient_menu()
            elif choice == '3':
                self.view_stock_alert()
            elif choice == '4':
                self.view_reports()
            elif choice == '5':
                print("\nLogout berhasil!")
                input("Tekan Enter untuk kembali ke menu login")
                break
            else:
                print("Pilihan tidak valid!")
                input("Tekan Enter untuk kembali")