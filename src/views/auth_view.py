import hashlib
import os

class AuthView:
    def __init__(self, data_store):
        self.data = data_store
        
    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def hash_password(self, password):
        """Simple password hashing"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def display_auth_menu(self):
        self.clear_screen()
        print("=" * 50)
        print("     SISTEM MANAJEMEN PRODUKSI MATCHA")
        print("=" * 50)
        print("\n1. Login Customer")
        print("2. Register Customer")
        print("3. Login Admin")
        print("4. Exit")
        print("=" * 50)
        
    def register_customer(self):
        self.clear_screen()
        print("=" * 50)
        print("         REGISTRASI CUSTOMER")
        print("=" * 50)
        
        try:
            username = input("\nUsername: ").strip()
            if not username:
                print("Username tidak boleh kosong!")
                input("Tekan Enter untuk kembali")
                return False
                
            fullname = input("Nama Lengkap: ").strip()
            if not fullname:
                print("Nama lengkap tidak boleh kosong!")
                input("Tekan Enter untuk kembali")
                return False
                
            phone = input("No. Telepon: ").strip()
            if not phone:
                print("No. telepon tidak boleh kosong!")
                input("Tekan Enter untuk kembali")
                return False
                
            email = input("Email: ").strip()
            if not email or '@' not in email:
                print("Email tidak valid!")
                input("Tekan Enter untuk kembali")
                return False
                
            password = input("Password: ").strip()
            if len(password) < 6:
                print("Password minimal 6 karakter!")
                input("Tekan Enter untuk kembali")
                return False
                
            confirm_password = input("Konfirmasi Password: ").strip()
            if password != confirm_password:
                print("Password tidak cocok!")
                input("Tekan Enter untuk kembali")
                return False
            
            # Check if username or email already exists
            for customer in self.data['customers']:
                if customer['username'] == username or customer['email'] == email:
                    print("Username atau email sudah terdaftar!")
                    input("Tekan Enter untuk kembali")
                    return False
            
            # Generate new customer ID
            new_id = max([c['customer_id'] for c in self.data['customers']], default=0) + 1
            
            # Add new customer
            hashed_password = self.hash_password(password)
            new_customer = {
                'customer_id': new_id,
                'role_id': 2,
                'username': username,
                'fullname': fullname,
                'phone': phone,
                'email': email,
                'password': hashed_password
            }
            
            self.data['customers'].append(new_customer)
            
            print("\nRegistrasi berhasil!")
            print(f"Selamat datang, {fullname}!")
            input("\nTekan Enter untuk login")
            return True
            
        except Exception as e:
            print(f"Error: {e}")
            input("Tekan Enter untuk kembali")
            return False
    
    def login_customer(self):
        self.clear_screen()
        print("=" * 50)
        print("           LOGIN CUSTOMER")
        print("=" * 50)
        
        try:
            username = input("\nUsername: ").strip()
            password = input("Password: ").strip()
            
            if not username or not password:
                print("Username dan password tidak boleh kosong!")
                input("Tekan Enter untuk kembali")
                return None
            
            hashed_password = self.hash_password(password)
            
            # Find customer
            for customer in self.data['customers']:
                if customer['username'] == username and customer['password'] == hashed_password:
                    print(f"\nLogin berhasil!")
                    print(f"Selamat datang, {customer['fullname']}!")
                    input("\nTekan Enter untuk melanjutkan")
                    return {
                        'customer_id': customer['customer_id'],
                        'username': customer['username'],
                        'fullname': customer['fullname'],
                        'email': customer['email']
                    }
            
            print("Username atau password salah!")
            input("Tekan Enter untuk kembali")
            return None
                
        except Exception as e:
            print(f"Error: {e}")
            input("Tekan Enter untuk kembali")
            return None
    
    def login_admin(self):
        self.clear_screen()
        print("=" * 50)
        print("            LOGIN ADMIN")
        print("=" * 50)
        
        try:
            username = input("\nUsername: ").strip()
            password = input("Password: ").strip()
            
            if not username or not password:
                print("Username dan password tidak boleh kosong!")
                input("Tekan Enter untuk kembali")
                return None
            
            hashed_password = self.hash_password(password)
            
            # Find admin
            for admin in self.data['admins']:
                if admin['username'] == username and admin['password'] == hashed_password:
                    print(f"\nLogin berhasil!")
                    print(f"Selamat datang, Admin {admin['username']}!")
                    input("\nTekan Enter untuk melanjutkan")
                    return {
                        'admin_id': admin['admin_id'],
                        'username': admin['username'],
                        'email': admin['email']
                    }
            
            print("Username atau password salah!")
            input("Tekan Enter untuk kembali")
            return None
                
        except Exception as e:
            print(f"Error: {e}")
            input("Tekan Enter untuk kembali")
            return None
    
    def run(self):
        while True:
            self.display_auth_menu()
            choice = input("\nPilih menu (1-4): ").strip()
            
            if choice == '1':
                customer = self.login_customer()
                if customer:
                    return 'customer', customer
            elif choice == '2':
                self.register_customer()
            elif choice == '3':
                admin = self.login_admin()
                if admin:
                    return 'admin', admin
            elif choice == '4':
                print("\nTerima kasih telah menggunakan sistem kami!")
                return 'exit', None
            else:
                print("Pilihan tidak valid!")
                input("Tekan Enter untuk kembali")