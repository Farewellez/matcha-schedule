import os

class AdminView:
    def __init__(self, data_store, admin_data):
        self.data = data_store
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
            products = self.data['products']
            
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
    
    def add_product(self):
        self.clear_screen()
        print("=" * 50)
        print("TAMBAH PRODUK")
        print("=" * 50)
        
        try:
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
            
            # Generate new product ID
            new_id = max([p['product_id'] for p in self.data['products']], default=0) + 1
            
            new_product = {
                'product_id': new_id,
                'product_name': name,
                'description': description,
                'price': price
            }
            
            self.data['products'].append(new_product)
            
            print("\nProduk berhasil ditambahkan!")
            input("Tekan Enter untuk kembali...")
            
        except Exception as e:
            print(f"Error: {e}")
            input("Tekan Enter untuk kembali")
    
    def edit_product(self):
        self.clear_screen()
        print("=" * 50)
        print("EDIT PRODUK")
        print("=" * 50)
        
        try:
            product_id = input("\nMasukkan ID Produk: ").strip()
            try:
                product_id = int(product_id)
            except ValueError:
                print("ID harus berupa angka!")
                input("Tekan Enter untuk kembali")
                return
            
            # Find product
            product = None
            for p in self.data['products']:
                if p['product_id'] == product_id:
                    product = p
                    break
            
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
            
            # Update product
            product['product_name'] = name
            product['description'] = description
            product['price'] = price
            
            print("\nProduk berhasil diupdate!")
            input("Tekan Enter untuk kembali")
            
        except Exception as e:
            print(f"Error: {e}")
            input("Tekan Enter untuk kembali")
    
    def delete_product(self):
        self.clear_screen()
        print("=" * 50)
        print("HAPUS PRODUK")
        print("=" * 50)
        
        try:
            product_id = input("\nMasukkan ID Produk: ").strip()
            try:
                product_id = int(product_id)
            except ValueError:
                print("ID harus berupa angka!")
                input("Tekan Enter untuk kembali")
                return
            
            # Find product
            product = None
            for p in self.data['products']:
                if p['product_id'] == product_id:
                    product = p
                    break
            
            if not product:
                print("Produk tidak ditemukan!")
                input("Tekan Enter untuk kembali")
                return
            
            confirm = input(f"\nHapus produk '{product['product_name']}'? (y/n): ").strip().lower()
            
            if confirm == 'y':
                self.data['products'].remove(product)
                
                # Also remove related product_ingredients
                self.data['product_ingredients'] = [
                    pi for pi in self.data['product_ingredients'] 
                    if pi['product_id'] != product_id
                ]
                
                print("\nProduk berhasil dihapus!")
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
            ingredients = self.data['ingredients']
            
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
        
        try:
            name = input("\nNama Bahan: ").strip()
            if not name:
                print("Nama bahan tidak boleh kosong!")
                input("Tekan Enter untuk kembali")
                return
            
            # Check if ingredient already exists (case insensitive)
            existing_ingredient = None
            for ing in self.data['ingredients']:
                if ing['ingredient_name'].lower() == name.lower():
                    existing_ingredient = ing
                    break
            
            if existing_ingredient:
                print(f"\nBahan '{existing_ingredient['ingredient_name']}' sudah ada!")
                print(f"Stok saat ini: {existing_ingredient['stock']} {existing_ingredient['unit']}")
                
                add_stock = input("\nTambah stok ke bahan yang sudah ada? (y/n): ").strip().lower()
                
                if add_stock == 'y':
                    additional_stock = input(f"Jumlah stok yang ditambahkan: ").strip()
                    try:
                        additional_stock = int(additional_stock)
                        if additional_stock < 0:
                            print("Jumlah tidak boleh negatif!")
                            input("Tekan Enter untuk kembali...")
                            return
                        
                        existing_ingredient['stock'] += additional_stock
                        print(f"\nStok berhasil ditambahkan!")
                        print(f"Stok baru: {existing_ingredient['stock']} {existing_ingredient['unit']}")
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
            
            # Generate new ingredient ID
            new_id = max([i['ingredient_id'] for i in self.data['ingredients']], default=0) + 1
            
            new_ingredient = {
                'ingredient_id': new_id,
                'ingredient_name': name,
                'unit': unit,
                'stock': stock,
                'minimum_stock': min_stock
            }
            
            self.data['ingredients'].append(new_ingredient)
            
            print("\nBahan baku berhasil ditambahkan!")
            input("Tekan Enter untuk kembali")
            
        except Exception as e:
            print(f"Error: {e}")
            input("Tekan Enter untuk kembali")
    
    def edit_ingredient(self):
        self.clear_screen()
        print("=" * 50)
        print("EDIT BAHAN BAKU")
        print("=" * 50)
        
        try:
            ing_id = input("\nMasukkan ID Bahan: ").strip()
            try:
                ing_id = int(ing_id)
            except ValueError:
                print("ID harus berupa angka!")
                input("Tekan Enter untuk kembali")
                return
            
            # Find ingredient
            ingredient = None
            for ing in self.data['ingredients']:
                if ing['ingredient_id'] == ing_id:
                    ingredient = ing
                    break
            
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
            
            # Update ingredient
            ingredient['ingredient_name'] = name
            ingredient['unit'] = unit
            ingredient['minimum_stock'] = min_stock
            
            print("\nBahan baku berhasil diupdate!")
            input("Tekan Enter untuk kembali")
            
        except Exception as e:
            print(f"Error: {e}")
            input("Tekan Enter untuk kembali")
    
    def update_stock(self):
        self.clear_screen()
        print("=" * 50)
        print("UPDATE STOK")
        print("=" * 50)
        
        try:
            ing_id = input("\nMasukkan ID Bahan: ").strip()
            try:
                ing_id = int(ing_id)
            except ValueError:
                print("ID harus berupa angka!")
                input("Tekan Enter untuk kembali")
                return
            
            # Find ingredient
            ingredient = None
            for ing in self.data['ingredients']:
                if ing['ingredient_id'] == ing_id:
                    ingredient = ing
                    break
            
            if not ingredient:
                print("Bahan baku tidak ditemukan!")
                input("Tekan Enter untuk kembali")
                return
            
            print(f"\nBahan: {ingredient['ingredient_name']}")
            print(f"Stok saat ini: {ingredient['stock']}")
            
            new_stock = input("\nStok baru: ").strip()
            try:
                new_stock = int(new_stock)
                if new_stock < 0:
                    print("Stok tidak boleh negatif!")
                    input("Tekan Enter untuk kembali")
                    return
            except ValueError:
                print("Stok harus berupa angka!")
                input("Tekan Enter untuk kembali")
                return
            
            # Update stock
            ingredient['stock'] = new_stock
            
            print("\nStok berhasil diupdate!")
            input("Tekan Enter untuk kembali")
            
        except Exception as e:
            print(f"Error: {e}")
            input("Tekan Enter untuk kembali")
    
    def delete_ingredient(self):
        self.clear_screen()
        print("=" * 50)
        print("HAPUS BAHAN BAKU")
        print("=" * 50)
        
        try:
            ing_id = input("\nMasukkan ID Bahan: ").strip()
            try:
                ing_id = int(ing_id)
            except ValueError:
                print("ID harus berupa angka!")
                input("Tekan Enter untuk kembali")
                return
            
            # Find ingredient
            ingredient = None
            for ing in self.data['ingredients']:
                if ing['ingredient_id'] == ing_id:
                    ingredient = ing
                    break
            
            if not ingredient:
                print("Bahan baku tidak ditemukan!")
                input("Tekan Enter untuk kembali")
                return
            
            confirm = input(f"\n⚠️  Hapus bahan '{ingredient['ingredient_name']}'? (y/n): ").strip().lower()
            
            if confirm == 'y':
                self.data['ingredients'].remove(ingredient)
                
                # Also remove related product_ingredients
                self.data['product_ingredients'] = [
                    pi for pi in self.data['product_ingredients'] 
                    if pi['ingredient_id'] != ing_id
                ]
                
                print("\nBahan baku berhasil dihapus!")
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
            ingredients = sorted(self.data['ingredients'], key=lambda x: x['stock'])
            
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
            product_totals = {}
            
            for order_item in self.data['order_items']:
                product_id = order_item['product_id']
                quantity = order_item['quantity']
                
                if product_id not in product_totals:
                    product_totals[product_id] = 0
                product_totals[product_id] += quantity
            
            if not product_totals:
                print("\nBelum ada data pesanan.")
            else:
                # Get product names and sort
                product_list = []
                for product_id, total in product_totals.items():
                    product = next((p for p in self.data['products'] if p['product_id'] == product_id), None)
                    if product:
                        product_list.append({
                            'name': product['product_name'],
                            'total': total
                        })
                
                product_list.sort(key=lambda x: x['total'], reverse=True)
                
                print("\n{:<5} {:<40} {:<15}".format("No", "Nama Produk", "Total Dipesan"))
                print("-" * 60)
                for idx, p in enumerate(product_list[:10], 1):
                    print("{:<5} {:<40} {:<15}".format(idx, p['name'][:38], p['total']))
            
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
            low_stock = [
                ing for ing in self.data['ingredients'] 
                if ing['stock'] <= ing['minimum_stock']
            ]
            
            low_stock.sort(key=lambda x: x['stock'])
            
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