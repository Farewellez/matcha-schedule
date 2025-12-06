import hashlib
from datetime import datetime
from views.auth_view import AuthView
from views.admin_view import AdminView
from views.customer_view import CustomerView

def hash_password(password):
    "Helper function to hash password"
    return hashlib.sha256(password.encode()).hexdigest()

def initialize_data():
    "Initialize in-memory data store"
    data = {
        'roles': [
            {'role_id': 1, 'role_name': 'admin'},
            {'role_id': 2, 'role_name': 'customer'}
        ],
        'admins': [
            {
                'admin_id': 1,
                'role_id': 1,
                'username': 'nmirran',
                'email': 'namira@gmail.com',
                'password': hash_password('namira71')
            },
            {
                'admin_id': 2,
                'role_id': 1,
                'username': 'sfamhrn',
                'email': 'sefia@gmail.com',
                'password': hash_password('sefia25')
            }
        ],
        'customers': [
            {
                'customer_id': 1,
                'role_id': 2,
                'username': 'nayla',
                'fullname': 'Nayla Alya Namira',
                'phone': '08123456789',
                'email': 'nayla@gmail.com',
                'password': hash_password('pass123')
            },
            {
                'customer_id': 2,
                'role_id': 2,
                'username': 'andi',
                'fullname': 'Andi Rahmat',
                'phone': '0834728192',
                'email': 'andi@gmail.com',
                'password': hash_password('pass123')
            }
        ],
        'products': [
            {
                'product_id': 1,
                'product_name': 'Matcha Latte Blend Powder',
                'description': 'Campuran daun tencha, krimer, gula halus',
                'price': 45000
            },
            {
                'product_id': 2,
                'product_name': 'Matcha Energy Boost Powder',
                'description': 'Matcha dengan ekstrak buah apel, kiwi, nanas',
                'price': 55000
            },
            {
                'product_id': 3,
                'product_name': 'Pure Ceremonial Matcha Powder',
                'description': 'Matcha murni kualitas ceremonial, 100% daun tencha',
                'price': 85000
            },
            {
                'product_id': 4,
                'product_name': 'Kids Fun Matcha Drink Powder',
                'description': 'Matcha khusus anak, daun tencha, krimer, gula halus',
                'price': 30000
            },
            {
                'product_id': 5,
                'product_name': 'Matcha Culinary Powder Blend',
                'description': 'Matcha murni untuk masakan + maltodekstrin',
                'price': 40000
            }
        ],
        'ingredients': [
            {
                'ingredient_id': 1,
                'ingredient_name': 'Daun Tencha',
                'unit': 'gram',
                'stock': 5000,
                'minimum_stock': 500
            },
            {
                'ingredient_id': 2,
                'ingredient_name': 'Gula Halus',
                'unit': 'gram',
                'stock': 3000,
                'minimum_stock': 300
            },
            {
                'ingredient_id': 3,
                'ingredient_name': 'Krimer',
                'unit': 'gram',
                'stock': 2000,
                'minimum_stock': 200
            },
            {
                'ingredient_id': 4,
                'ingredient_name': 'Ekstrak Apel',
                'unit': 'gram',
                'stock': 1000,
                'minimum_stock': 100
            },
            {
                'ingredient_id': 5,
                'ingredient_name': 'Ekstrak Kiwi',
                'unit': 'gram',
                'stock': 1000,
                'minimum_stock': 100
            },
            {
                'ingredient_id': 6,
                'ingredient_name': 'Ekstrak Nanas',
                'unit': 'gram',
                'stock': 1000,
                'minimum_stock': 100
            },
            {
                'ingredient_id': 7,
                'ingredient_name': 'Maltodekstrin',
                'unit': 'gram',
                'stock': 2500,
                'minimum_stock': 250
            }
        ],
        'product_ingredients': [
            # Matcha Latte Blend Powder
            {'pi_id': 1, 'product_id': 1, 'ingredient_id': 1, 'quantity_per_unit': 20},
            {'pi_id': 2, 'product_id': 1, 'ingredient_id': 2, 'quantity_per_unit': 10},
            {'pi_id': 3, 'product_id': 1, 'ingredient_id': 3, 'quantity_per_unit': 10},
            
            # Matcha Energy Boost Powder
            {'pi_id': 4, 'product_id': 2, 'ingredient_id': 1, 'quantity_per_unit': 20},
            {'pi_id': 5, 'product_id': 2, 'ingredient_id': 4, 'quantity_per_unit': 5},
            {'pi_id': 6, 'product_id': 2, 'ingredient_id': 5, 'quantity_per_unit': 5},
            {'pi_id': 7, 'product_id': 2, 'ingredient_id': 6, 'quantity_per_unit': 5},
            
            # Pure Ceremonial Matcha
            {'pi_id': 8, 'product_id': 3, 'ingredient_id': 1, 'quantity_per_unit': 30},
            
            # Kids Fun Matcha Powder
            {'pi_id': 9, 'product_id': 4, 'ingredient_id': 1, 'quantity_per_unit': 10},
            {'pi_id': 10, 'product_id': 4, 'ingredient_id': 3, 'quantity_per_unit': 10},
            {'pi_id': 11, 'product_id': 4, 'ingredient_id': 2, 'quantity_per_unit': 10},
            
            # Culinary Matcha Powder
            {'pi_id': 12, 'product_id': 5, 'ingredient_id': 1, 'quantity_per_unit': 25},
            {'pi_id': 13, 'product_id': 5, 'ingredient_id': 7, 'quantity_per_unit': 15}
        ],
        'statuses': [
            {'status_id': 1, 'status_name': 'Menunggu Konfirmasi'},
            {'status_id': 2, 'status_name': 'Diproses'},
            {'status_id': 3, 'status_name': 'Dikirim'},
            {'status_id': 4, 'status_name': 'Selesai'}
        ],
        'orders': [
            {
                'order_id': 1,
                'customer_id': 1,
                'order_timestamp': datetime(2024, 12, 1, 10, 30),
                'total_price': 45000,
                'status': 'Menunggu Konfirmasi'
            },
            {
                'order_id': 2,
                'customer_id': 2,
                'order_timestamp': datetime(2024, 12, 2, 14, 15),
                'total_price': 85000,
                'status': 'Diproses'
            }
        ],
        'order_items': [
            {
                'order_item_id': 1,
                'order_id': 1,
                'product_id': 1,
                'quantity': 1
            },
            {
                'order_item_id': 2,
                'order_id': 2,
                'product_id': 3,
                'quantity': 1
            }
        ],
        'notifications': []
    }
    
    return data

def main():
    print("\n" + "=" * 50)
    print("  SELAMAT DATANG DI SISTEM PRODUKSI MATCHA")
    print("=" * 50)
    print("\nInitializing system...")
    
    # Initialize data store
    data_store = initialize_data()
    
    print("System ready!\n")
    
    try:
        while True:
            # Authentication
            auth = AuthView(data_store)
            role, user_data = auth.run()
            
            if role == 'exit':
                break
            elif role == 'admin' and user_data:
                # Admin Menu
                admin_view = AdminView(data_store, user_data)
                admin_view.run()
            elif role == 'customer' and user_data:
                # Customer Menu
                customer_view = CustomerView(data_store, user_data)
                customer_view.run()
    
    except KeyboardInterrupt:
        print("\n\nProgram dihentikan oleh user.")
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        print("\nTerima kasih telah menggunakan sistem kami!\n")

if __name__ == "__main__":
    main()