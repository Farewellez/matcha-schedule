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
            # ... (Validasi fullname, phone, email, password) ...
            
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
            
            # --- START: PERUBAHAN UNTUK MENGGUNAKAN DATABASE CLIENT (self.data) ---
            
            # 1. Check if username or email already exists
            # self.data adalah DatabaseClient. Kita asumsikan ada metode 'check_user_exists'
            if self.data.check_user_exists(username, email):
                print("Username atau email sudah terdaftar!")
                input("Tekan Enter untuk kembali")
                return False
            
            # 2. Add new customer
            hashed_password = self.hash_password(password)
            
            # Kita panggil metode DB untuk menyimpan data dan mendapatkan ID baru
            customer_id = self.data.register_new_customer(
                username=username,
                fullname=fullname,
                phone=phone,
                email=email,
                hashed_password=hashed_password
            )
            
            if customer_id:
                print("\nRegistrasi berhasil!")
                print(f"Selamat datang, {fullname}!")
                input("\nTekan Enter untuk login")
                return True
            else:
                print("\nRegistrasi gagal karena masalah database!")
                input("Tekan Enter untuk kembali")
                return False

            # --- END: PERUBAHAN ---
            
        except Exception as e:
            # Karena kode lama menggunakan try/except yang luas, kita pertahankan
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
            
            # --- START: PERUBAHAN UNTUK MENGGUNAKAN DATABASE CLIENT (self.data) ---
            
            # 1. Find customer (Ganti loop dengan pemanggilan metode DB)
            # self.data adalah DatabaseClient. Kita asumsikan ada metode 'authenticate_customer'
            customer_data = self.data.authenticate_customer(username, hashed_password)
            
            if customer_data:
                # Login berhasil, customer_data berisi data dari DB
                print(f"\nLogin berhasil!")
                print(f"Selamat datang, {customer_data['fullname']}!")
                input("\nTekan Enter untuk melanjutkan")
                
                # Mengembalikan data yang diterima dari DatabaseClient
                return customer_data 
            else:
                # Login gagal
                print("Username atau password salah!")
                input("Tekan Enter untuk kembali")
                return None

            # --- END: PERUBAHAN ---
                
        except Exception as e:
            # Karena kode lama menggunakan try/except yang luas, kita pertahankan
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
            
            # --- START: PERUBAHAN UNTUK MENGGUNAKAN DATABASE CLIENT (self.data) ---
            
            # 1. Find admin (Ganti loop dengan pemanggilan metode DB)
            # self.data adalah DatabaseClient. Kita asumsikan ada metode 'authenticate_admin'
            admin_data = self.data.authenticate_admin(username, hashed_password)
            
            if admin_data:
                # Login berhasil, admin_data berisi data dari DB
                print(f"\nLogin berhasil!")
                print(f"Selamat datang, Admin {admin_data['username']}!")
                input("\nTekan Enter untuk melanjutkan")
                
                # Mengembalikan data yang diterima dari DatabaseClient
                return admin_data 
            else:
                # Login gagal
                print("Username atau password salah!")
                input("Tekan Enter untuk kembali")
                return None

            # --- END: PERUBAHAN ---
                
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