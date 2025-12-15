## 1. src/models/order.py
### Definisi Model Data (Class Order dengan @dataclass)
#### a. Tujuan: 
Kelas Order berfungsi sebagai representasi data Order dari database (Data Transfer Object). Penggunaan @dataclass membuat kode lebih ringkas dan secara otomatis menghasilkan method seperti __init__ dan __repr__.
#### b. Properti Dasar:
- order_id, customer_id, total_price, status_id, status_name: Ini adalah data transaksional standar yang diambil dari tabel Order.
- deadline: Ini adalah variabel kunci untuk urgensi. Waktu terakhir Order harus diselesaikan.
- total_quantity: Jumlah total produk yang diminta dalam Order (digunakan sebagai faktor pembobotan).
#### c. Properti Prioritas:
- priority_score: float = 0.0: Variabel Status. Ini adalah tempat hasil perhitungan bobot akan disimpan. Nilai default 0.0.
- items: List[OrderItem]: Menyimpan detail item-item di dalam Order tersebut (meskipun tidak digunakan di perhitungan skor utama yang Anda tunjukkan, ini penting untuk pengurangan stok).

### Method calculate_priority_score()
Ini adalah tempat logika bisnis diterapkan, menentukan seberapa penting suatu Order. Method ini menerima parameter bobot W_DEADLINE, W_QUANTITY, STOCK_BONUS dari src/config.py agar Order model tetap clean.

#### a. Menghitung Faktor Waktu (Time Factor)

```
time_remaining_seconds = (self.deadline - datetime.now()).total_seconds()
time_factor = 1.0 / max(1.0, time_remaining_seconds)
```

- Logika Urgensi: Menghitung sisa waktu hingga deadline dalam detik.
- Pembagi Invers: time_factor adalah 1/Waktu Tersisa
Jika waktu tersisa Besar (misalnya, 2 hari), time_factor akan menjadi Kecil dan Jika waktu tersisa Sangat Kecil (misalnya, 5 menit), time_factor akan menjadi Sangat Besar.
- Guardrail: Penggunaan max(1.0, ...) mencegah pembagian dengan nol atau nilai negatif jika deadline sudah terlampaui.

#### b. Menghitung Komponen Skor

```
score_deadline = W_DEADLINE * time_factor
score_quantity = W_QUANTITY * self.total_quantity
score_stock = STOCK_BONUS if current_stock_alert else 0
```

Ini adalah penerapan langsung dari rumus prioritas dengan bobot yang Anda tetapkan:
- Prioritas Urgensi: W_DEADLINE dikalikan dengan faktor waktu (urgensi). Karena W_DEADLINE Anda sangat besar (500.000,0), komponen ini mendominasi skor.
- Prioritas Kuantitas: W_QUANTITY (biasanya kecil) dikalikan dengan kuantitas total.
- Prioritas Dinamis (Stok): Jika current_stock_alert bernilai True (dikiriman dari Stock Controller), maka STOCK_BONUS akan ditambahkan.

#### c. Finalisasi

```
self.priority_score = score_deadline + score_quantity + score_stock
```

Hasil akhir disimpan di atribut priority_score, yang siap digunakan oleh ProductionPriorityQueue untuk menentukan posisi Order dalam antrian.

## 2 src/controllers/priority_queue
### Method add_order(self, order: Order)
Method ini bertanggung jawab untuk menerima Order baru, menghitung skor prioritas awalnya, dan menyisipkannya ke dalam struktur data Priority Queue (self.heap) dan map (self._order_map) untuk pelacakan.

#### a. Menghitung Skor Awal Order

```
def add_order(self, order: Order):
    order.calculate_priority_score(
        W_DEADLINE=W_DEADLINE,
        W_QUANTITY=W_QUANTITY,
        STOCK_BONUS=STOCK_BONUS,
        current_stock_alert=False
    )
```
- Fungsi: Baris ini memanggil method yang baru saja kita uji (calculate_priority_score) pada objek order yang masuk. Ini adalah langkah pertama dan paling krusial.
- Parameter: Method ini memasukkan nilai bobot W_DEADLINE, W_QUANTITY, STOCK_BONUS yang di-import dari src/config.py. Ini memastikan bahwa perhitungan skor konsisten di seluruh sistem.
- Status Awal Stok: Nilai current_stock_alert=False digunakan sebagai default. Ketika Order baru masuk, Order tersebut dihitung berdasarkan skor dasarnya (urgensi deadline dan kuantitas) tanpa adanya boost prioritas karena stok rendah. Stock boost akan diterapkan kemudian oleh Stock Controller jika diperlukan melalui method recalculate_all_priorities.

#### b. Memasukkan Order ke Heap (Antrian Prioritas)
Meskipun menyertakan panggilan calculate_priority_score, biasanya setelah perhitungan skor, method add_order akan melanjutkan dengan langkah ini (berdasarkan kode yang kita lihat di sesi sebelumnya):
- Penyisipan ke Heap (heapq.heappush): Fungsi ini memasukkan Order ke dalam Min-Heap (self.heap) sambil menjaga heap property (elemen terkecil selalu di puncak).
- Negasi Skor (-order.priority_score): Seperti yang sudah dibahas, ini mengubah Max-Priority Queue menjadi Min-Heap.
- Tie-Breaker (-timestamp_float): Digunakan untuk memastikan bahwa jika dua Order memiliki skor yang persis sama, Order yang masuk lebih dulu (order_timestamp lebih lama) akan diprioritaskan.

#### c. Memasukkan Order ke Map (self._order_map)

```
self._order_map[order.order_id] = order
```
self._order_map (berupa dictionary di Python) berfungsi sebagai indeks cepat.Ini memungkinkan sistem untuk menemukan objek Order tertentu berdasarkan order_id. misalnya, saat perlu melakukan debugging atau ketika Order harus dihapus/diperbarui tanpa perlu mencari seluruh heap secara linear. Hal ini sangat penting untuk operasi seperti recalculate_all_priorities.

### Method get_highest_priority_order(self) -> -> Optional[Order]
Tujuannya untuk mengambil dan menghapus Order yang saat ini memiliki skor prioritas tertinggi (yang paling mendesak) dari Priority Queue. Scheduler memanggil method ini setiap kali Mesin Produksi siap menerima tugas baru.

if self.heap: -> Memeriksa apakah Priority Queue (self.heap) memiliki elemen di dalamnya. Ini adalah guardrail sederhana untuk mencegah program crash jika Scheduler mencoba menarik Order dari antrian yang kosong.

#### a. Penarikan Order Prioritas Tertinggi (The Core Operation)
neg_score, timestamp, order_id, order = heapq.heappop(self.heap)
- Mengambil elemen yang berada di puncak Min-Heap (karena negasi, adalah Order dengan Skor Prioritas TERBESAR).
- Mengatur ulang heap (melakukan heapify) untuk memastikan elemen prioritas tertinggi berikutnya langsung naik ke puncak. Operasi ini sangat efisien, berjalan dalam kompleksitas waktu O(log n).

Elemen yang diambil (berupa tuple) dibongkar kembali menjadi komponen aslinya: skor negatif, timestamp negatif, ID, dan objek Order itu sendiri.

#### b. Pembersihan dari Map (Pelacakan Status)

```
# Hapus dari map saat diproses
        if order_id in self._order_map:
            del self._order_map[order_id]
```

- Tujuan: Menjaga konsistensi data. Setelah Order ditarik dari heap untuk diproses (dikirim ke mesin), Order tersebut harus dihapus dari self._order_map.
- Mengapa Dihapus?: self._order_map hanya melacak Order yang saat ini sedang menunggu giliran di antrian. Setelah Order ditarik, ia dianggap "sedang diproses" (atau segera akan diproses) dan tidak lagi perlu dilacak oleh Priority Queue. Hal ini mencegah error dan pemborosan memori.
- Guardrail Tambahan: Pengecekan if order_id in self._order_map: mencegah KeyError jika Order entah bagaimana sudah dihapus atau tidak ada di map (meskipun seharusnya ada).

#### c. Mengembalikan Order

```
return order
    return None
```

### Method recalculate_all_priorities
Ketika dipanggil (biasanya oleh ProductionScheduler atau Stock Controller secara berkala, misalnya setiap 5 menit), method ini melakukan penyegaran total pada antrian prioritas. Ini diperlukan karena:
- Waktu Terus Berjalan: Waktu tersisa (time remaining) Order terus berkurang, membuat urgensi mereka meningkat.
- Perubahan Stok: Kondisi stok mungkin berubah, memicu STOCK_BONUS.

#### a. Inisialisasi Heap Baru

```
def recalculate_all_priorities(self, current_stock_alert: bool =False):
        """Memaksa hitung ulang skor prioritas untuk SEMUA Order di Queue dan membangun ulang heap."""
        new_heap = []
```

- Fungsi: Membuat list kosong baru (new_heap) yang akan menampung Order-Order yang sudah diperbarui.
- Strategi: Daripada mencoba memperbarui dan mengatur ulang setiap elemen di heap lama (yang secara teknis sulit dan lambat), method ini memilih strategi yang lebih sederhana dan aman: Membuat ulang seluruh heap dari awal.

#### b. Iterasi dan Perhitungan Ulang Skor

```
for order in self._order_map.values():
            # ... (Panggil calculate_priority_score)
            order.calculate_priority_score(
                W_DEADLINE=W_DEADLINE,
                W_QUANTITY=W_QUANTITY,
                STOCK_BONUS=STOCK_BONUS,
                current_stock_alert=current_stock_alert
            ) 
            # ...
```

- Iterasi (for order in self._order_map.values()): Loop ini mengambil semua objek Order yang saat ini sedang menunggu di antrian. Menggunakan self._order_map lebih efisien daripada memproses heap lama, karena map berisi objek Order yang sudah di-unpacked.
- Perhitungan Skor Ulang: Untuk setiap Order, method calculate_priority_score dipanggil lagi.
- Penting: Karena datetime.now() digunakan di dalam calculate_priority_score, perhitungan ini akan menghasilkan skor yang lebih tinggi (urgensi lebih besar) jika waktu telah berlalu sejak Order terakhir dihitung.
- Parameter Dinamis: Nilai current_stock_alert diterima sebagai argumen. Jika Stock Controller memanggil method ini dengan True (misalnya, bahan baku matcha sedang menipis), semua Order yang menggunakan bahan tersebut akan mendapatkan STOCK_BONUS.

### c. Membangun Tuple dan Memasukkan ke Heap Baru

```
timestamp_float = order.order_timestamp.timestamp()
            heapq.heappush(new_heap, 
                             (-order.priority_score, 
                              -timestamp_float, 
                              order.order_id, 
                              order))
```
- Fungsi: Setelah skor prioritas Order diperbarui, Order tersebut segera dimasukkan ke dalam new_heap sebagai tuple prioritas.
- Efek: Meskipun new_heap hanyalah list biasa saat ini, Order dimasukkan satu per satu menggunakan heapq.heappush. Ini memastikan elemen-elemennya memiliki struktur yang benar.

#### d. Mengganti Heap Lama (Finalisasi)

```
self.heap = new_heap
        heapq.heapify(self.heap)
```

- Penggantian: self.heap yang lama (yang skornya mungkin sudah basi) diganti dengan new_heap yang berisi Order dengan skor terbaru.
- Pembersihan (heapq.heapify): Meskipun Order dimasukkan menggunakan heappush (yang seharusnya sudah menjaga heap property), heapify adalah guardrail final untuk memastikan bahwa list baru tersebut benar-benar terstruktur sebagai Min-Heap yang valid. Ini menjamin bahwa Order dengan skor tertinggi (paling mendesak) berada di puncak (self.heap[0]).

## 3. src/controllers/scheduler.py
### Enumerasi Status Mesin (MachineStatus)

```
class MachineStatus(Enum):
    IDLE = auto()
    BUSY = auto()
```

- Apa itu Enum? Enum (Enumeration) adalah cara Python untuk membuat sekumpulan nama simbolis yang terikat pada nilai konstan.
- Tujuan: Memberikan status yang jelas dan terstruktur pada setiap mesin. Ini jauh lebih aman dan lebih mudah dibaca daripada menggunakan string ("IDLE", "BUSY") atau angka (0, 1).
- auto(): Ini secara otomatis memberikan nilai unik pada setiap anggota (misalnya, IDLE mungkin bernilai 1 dan BUSY bernilai 2), meskipun yang terpenting adalah nama simbolisnya, bukan nilainya.
- Inti Logika: Scheduler akan menggunakan status ini untuk menentukan mesin mana yang bisa diberikan tugas baru.

### Kelas Mesin Produksi (ProductionMachine)
Kelas ini adalah representasi digital dari setiap mesin fisik di lantai pabrik.

#### a. Konstruktor (__init__)

```
class ProductionMachine:
    def __init__(self, machine_id:int ,num_machines: int = PRODUCTION_MACHINE_COUNT):
        self.machine_id = machine_id
        self.status = MachineStatus.IDLE
```
- self.machine_id: Ini adalah ID unik untuk mesin ini (misalnya, Mesin 1, Mesin 2). Ini penting untuk pelacakan dan logging.
- self.status: Saat mesin baru diinisialisasi, status awalnya adalah MachineStatus.IDLE—artinya, siap menerima Order dari Priority Queue.
- num_machines: Argumen ini menerima jumlah total mesin yang ada (diambil dari src.config). Meskipun tidak digunakan secara langsung di constructor ini, ini bisa berguna jika Anda ingin menambahkan logika self-checking di masa depan.

### b. Atribut Dinamis (Status Tugas)

```
self.current_order: Optional[Order] = None
self.estimated_finish_time: Optional[datetime.datetime] = None
self.production_batch_id: Optional[int] = None
```

Atribut ini adalah bagian yang paling penting, karena mereka melacak pekerjaan yang sedang dilakukan:
- self.current_order: Optional[Order]:
Tujuan: Menyimpan objek Order yang sedang diproses oleh mesin ini.

Optional: Menggunakan type hint Optional[Order] menunjukkan bahwa nilai ini bisa berupa objek Order atau None (jika mesin sedang IDLE).

- self.estimated_finish_time: Optional[datetime.datetime]:
Tujuan: Menyimpan perkiraan waktu kapan Order yang sedang dikerjakan akan selesai.

Pentingnya: Data ini penting untuk simulasi, logging, dan untuk memberi tahu Scheduler kapan harus memindahkan mesin dari BUSY ke IDLE lagi.

- self.production_batch_id: Optional[int]:
Tujuan: ID yang unik untuk batch produksi ini. Dalam sistem real-world, ini biasanya ID yang dimasukkan ke dalam database saat Order mulai diproses. Ini memisahkan log Order (pesanan pelanggan) dari log Produksi (proses di pabrik).

### method check_finish(self, db_client) -> Optional[Order]
Method ini dipanggil secara berkala oleh Production Scheduler untuk mengecek apakah Order yang sedang dikerjakan oleh mesin ini sudah selesai. Jika sudah selesai, ia memicu transaksi akhir ke database dan mengosongkan mesin.

#### a. Kriteria Penyelesaian (The Check)

```
if self.status == MachineStatus.BUSY and \
   self.estimated_finish_time <= datetime.datetime.now():
```
- Logika: Ini adalah gerbang masuknya. Mesin baru akan mencoba menyelesaikan Order jika:
self.status == MachineStatus.BUSY: Mesin harus sedang bekerja (tidak menganggur).

self.estimated_finish_time <= datetime.datetime.now(): Waktu perkiraan selesai sudah tiba atau telah terlampaui.

- Jika Kondisi Tidak Terpenuhi: Kode akan melompat ke baris terakhir dan mengembalikan return None.

#### b. Persiapan Transaksi

```
finished_order = self.current_order
batch_id = self.production_batch_id
```

Data Order dan ID batch disalin ke variabel lokal. Ini penting karena data ini masih diperlukan untuk transaksi ke DB, meskipun status mesin sebentar lagi akan diubah.

#### c. Eksekusi Transaksi Database yang Kritis (ACID Principle)

```
try:
    success = db_client.finish_production_transaction(
        order_id=finished_order.order_id, 
        production_batch_id=batch_id
    )
except Exception as e:
    print(f"🚨 WARNING: Gagal menjalankan transaksi DB untuk Order ID {finished_order.order_id}. Error: {e}")
    return None
```

- Fungsi finish_production_transaction: Kita asumsikan method ini melakukan dua hal penting di database:
Mengubah status Order menjadi 'Selesai' (Completed). <br>
Mengurangi stok inventaris sesuai dengan OrderItem yang ada di dalam Order tersebut.

- try...except: Ini adalah guardrail penting! . Jika ada error yang tidak terduga saat koneksi ke DB (misalnya, network failure), program tidak akan crash. Sebaliknya, ia mencetak peringatan, dan yang terpenting, ia mengembalikan return None tanpa mengubah status mesin. Mesin tetap BUSY dan akan dicoba lagi pada interval polling berikutnya, mencegah data hilang.

Setelah transaksi dicoba, kita cek hasilnya:

```
if success:
    # ... (Reset status mesin) ...
    return finished_order 
else:
    # ... (Gagal return False) ...
    return None
```

- if success: (Transaksi Berhasil):
Logging ✅ SUCCESS dicetak.<br>
Transisi Status Aman: Status mesin di-reset menjadi IDLE dan semua atribut Order dibersihkan (None). Tindakan ini (reset) hanya dilakukan setelah DB mengonfirmasi keberhasilan. <br>
Output: Objek finished_order dikembalikan. Scheduler dapat menggunakan objek ini untuk logging lanjutan atau pemicu sistem lain (misalnya, notifikasi pengiriman).

- else: (Transaksi Gagal dengan return False):
Logging ❌ ERROR dicetak. <br>
Penting: Jika db_client mengembalikan False (berarti transaksi gagal di sisi DB karena alasan logika, bukan koneksi), mesin TIDAK di-reset dan tetap BUSY. Ini memastikan Order akan dicoba lagi untuk diselesaikan di polling berikutnya, mempertahankan integritas data.

==============================================================

## 4. src/api/client.py
### DatabaseClient
#### a. Import dan Konfigurasi

```
import psycopg2
from typing import Optional, List, Tuple, Dict
from datetime import datetime
# ...
from src.config import PGHOST, PGDATABASE, PGUSER, PGPASSWORD, PGSSLMODE
```
- psycopg2: Ini adalah library wajib untuk berinteraksi dengan database PostgreSQL dari Python.
- typing & datetime: Anda dengan tepat mengimpor modul ini untuk menjaga kualitas kode dengan type hinting (yang sudah sering kita diskusikan) dan untuk menangani data waktu.
- src.config: Ini adalah praktik terbaik (DevOps mindset!) untuk mengambil kredensial database (Host, User, Password) dari file konfigurasi terpisah. Ini menjaga kode inti tetap bersih dan kredensial tetap aman.

#### b. Konstruktor (__init__)

```
class DatabaseClient:
    def __init__(self):
        self.conn = None
        self.cursor = None
        self._connect()
```

- self.conn = None: Atribut ini akan menyimpan objek koneksi utama ke database setelah koneksi berhasil dibuat. Koneksi ini adalah jembatan komunikasi.
- self.cursor = None: Kursor adalah objek yang memungkinkan Anda mengirim perintah SQL dan menerima hasil dari database melalui koneksi (self.conn). Setiap operasi DB (SELECT, INSERT, UPDATE) melalui kursor.
- self._connect(): Ini adalah method inti yang dipanggil saat objek DatabaseClient dibuat. Ini memisahkan logika koneksi yang mungkin kompleks dari constructor yang sederhana.

### Method Koneksi dan Penutupan

#### a. _connect(self): Membuka Gerbang Komunikasi
Method ini bertanggung jawab untuk membangun koneksi ke database menggunakan parameter sensitif yang dimuat dari config.

```
try:
    self.conn = psycopg2.connect (
        host=PGHOST,
        database=PGDATABASE,
        user=PGUSER,
        password=PGPASSWORD,
        sslmode=PGSSLMODE
    )
```

- Fungsi: Menggunakan psycopg2.connect() untuk membuat objek koneksi (self.conn).
- Keamanan: Mengambil semua detail koneksi (Host, User, Password, SSL mode) dari variabel konfigurasi adalah praktik yang sangat baik, terutama untuk lingkungan produksi.

```
self.conn.autocommit = False
    self.cursor = self.conn.cursor()
    print("DB Connect!")
```

- self.conn.autocommit = False: Ini adalah baris terpenting di sini!
Autocommit: Jika True, setiap perintah SQL (INSERT, UPDATE, DELETE) akan langsung disimpan permanen di DB. <br>
Saat False (Setting Anda): Perubahan SQL (transaksi) tidak akan disimpan permanen sampai Anda memanggil self.conn.commit(). Ini memungkinkan Anda mengelompokkan beberapa query menjadi satu unit atomik. Jika ada error di tengah jalan, Anda bisa memanggil rollback() untuk membatalkan semuanya. Ini adalah standar emas untuk menjaga integritas data.

- self.cursor = self.conn.cursor(): Setelah koneksi dibuat, objek cursor dibuat. Cursor adalah alat yang akan membawa semua perintah SQL Anda ke DB.

```
except psycopg2.Error as e:
    print("Gagal connect DB, error: ", e)
```

Jika koneksi gagal (salah password, host tidak dapat dijangkau, DB down), psycopg2 akan melempar psycopg2.Error. Program Anda menangkapnya dan mencetak pesan error alih-alih crash total. Ini membuat sistem Anda robust saat inisialisasi.

```
def close(self):
    if self.cursor:
        self.cursor.close()
    if self.conn:
        self.conn.close()
    print("Koneksi ditutup")
```

Method ini memastikan bahwa sumber daya koneksi yang digunakan oleh program dibebaskan. Ini dipanggil saat program selesai atau saat objek DatabaseClient dihancurkan.

- Penutupan Bertahap:
if self.cursor: self.cursor.close(): Kursor harus ditutup terlebih dahulu. Pengecekan if self.cursor mencegah error jika koneksi DB gagal sejak awal dan self.cursor tetap None. <br>
if self.conn: self.conn.close(): Koneksi utama ke DB ditutup.

- Manfaat: Menutup koneksi sangat penting untuk menghindari kebocoran sumber daya (resource leak). Jika banyak koneksi dibiarkan terbuka, DB bisa kehabisan slot koneksi yang tersedia, menyebabkan Order baru gagal diproses.

#### b. method _execute_query(self, query: str, params=None)
- Fungsi: Menyediakan cara yang aman dan seragam untuk menjalankan perintah SQL (baik SELECT maupun operasi non-transaksional seperti query yang tidak memerlukan commit langsung) melalui kursor psycopg2.
- Keandalan: Memastikan bahwa kursor dan koneksi ada sebelum eksekusi dimulai, dan menangani kegagalan SQL dengan membatalkan transaksi yang sedang berjalan.

```
if self.cursor is None or self.conn is None:
    error_msg = "❌ Koneksi atau kursor DB belum diinisialisasi. Gagal eksekusi query."
    print(error_msg)
    raise ConnectionError(error_msg)
```

- Logika: Ini adalah lapisan pertahanan pertama (yang menghilangkan warning Pylance!). Ini secara eksplisit memeriksa apakah self.cursor dan self.conn masih bernilai None (yang seharusnya hanya terjadi jika _connect gagal).
- Penanganan Error: Jika koneksi belum siap, ia mencetak pesan error dan segera melempar ConnectionError.
Penting: Dengan melempar ConnectionError, kode yang memanggil _execute_query (misalnya, method get_pending_orders) akan tahu bahwa kegagalannya bersifat fatal dan terkait dengan infrastruktur, bukan karena query SQL yang salah.

```
try:
    self.cursor.execute(query, params)
    return self.cursor
```

- Fungsi: Jika guardrail berhasil dilewati, ini adalah tempat query SQL dijalankan.
self.cursor.execute(query, params): Ini mengirimkan query ke database. Menggunakan params (parameterisasi) sangat penting untuk mencegah serangan SQL Injection, yang merupakan praktik keamanan utama dalam pengembangan aplikasi.

- Output: Jika eksekusi berhasil, method mengembalikan objek kursor itu sendiri. Hal ini memungkinkan method pemanggil (misalnya, get_pending_orders) untuk langsung memanggil fungsi kursor seperti .fetchone() atau .fetchall() untuk mengambil hasil data.

```
except psycopg2.Error as e:
    self.conn.rollback()
    print(f"❌ Error saat menjalankan query: {e}")
    raise
```

- Logika: Bagian ini menangkap error yang spesifik terjadi selama eksekusi SQL (misalnya, syntax error, constraint violation, atau lock di DB).
- self.conn.rollback(): Ini adalah inti dari penanganan transaksi! Karena kita menyetel autocommit = False, jika terjadi error SQL, method ini akan membatalkan semua perubahan yang mungkin telah dilakukan oleh query sebelumnya dalam transaksi yang sama. Ini menjaga integritas data.
- raise: Setelah mencetak pesan error yang jelas, method ini melempar ulang (re-raise) exception psycopg2.Error. Ini penting agar Scheduler yang memanggil method ini tahu bahwa operasi DB gagal dan dapat menangani Order yang terkait (misalnya, tidak menghapus Order dari Priority Queue).

### Method Lainnya
sisa method akan disesuaikan (ga terlalu penting buat topik struktur data karena mengandalkan query SQL)

## 5. Kembali src/controllers/scheduler.py
### Penjelasan class ProductionScheduler: __init__
#### a. Inisialisasi Komponen Inti

self.queue = ProductionPriorityQueue()
- Apa itu? Ini adalah Priority Queue (Antrian Prioritas) kustom yang Anda buat.
- Fungsi: Bertindak sebagai buffer yang menampung semua pesanan yang menunggu untuk diproduksi. Kunci utamanya adalah Prioritas: pesanan yang paling mendesak (misalnya, yang paling cepat jatuh tempo) akan selalu berada di depan antrian, siap diambil oleh mesin.

self.machine = [ProductionMachine(i + 1) for i in range(num_machine)]
- Apa itu? Ini membuat daftar objek ProductionMachine.
- Fungsi: Merepresentasikan mesin fisik atau slot produksi yang tersedia di pabrik Anda. Jika num_machine adalah 2 (nilai default), Anda memiliki self.machine[0] dan self.machine[1]. Scheduler akan terus memeriksa mesin-mesin ini; jika ada yang IDLE, ia akan mengalokasikan pekerjaan baru.

self.db_client = DatabaseClient()
- Apa itu? Ini adalah instansi dari kelas DatabaseClient yang baru saja kita amankan bersama.
- Fungsi: Menyediakan akses yang aman dan transaksional ke database. Semua operasi kritis seperti mengambil pesanan baru, memperbarui status pesanan menjadi IN_PROGRESS atau COMPLETED, dan memeriksa stok dilakukan melalui objek ini.

#### b. Penyiapan Kontrol Stok (Dependency Injection)

```
from src.controllers.stock_controller import StockController
self.stock_controller = StockController(self.db_client, self.queue)
```
- Apa itu? Ini mengimpor dan menginisialisasi StockController.
- Fungsi: StockController bertanggung jawab untuk memastikan semua bahan baku tersedia sebelum pesanan dapat dimulai. Penting untuk dicatat bahwa Anda melakukan Dependency Injection di sini:
self.db_client diberikan ke StockController agar ia bisa memeriksa stok di DB. <br>
self.queue diberikan agar StockController dapat berinteraksi dengan antrian (misalnya, menahan pesanan jika stok tidak cukup).

### method _fetch_new_orders_from_db (Mengambil & Mengantri Pesanan)
Method ini bertanggung jawab untuk secara berkala "mengambil" pesanan baru yang masuk dan menempatkannya di Antrian Prioritas (self.queue) agar siap diproses. Method ini berfungsi sebagai Gateway antara Persistence Layer (DB) dan Scheduling Layer. Ini memastikan bahwa scheduler hanya berurusan dengan objek Order yang bersih dan mudah diatur.Aku coba bagi penjelasan per-bagian code

```
new_orders_raw = self.db_client.fetch_new_orders()
```
Memanggil method di DatabaseClient (yang sudah kita amankan) untuk mendapatkan daftar pesanan baru. Biasanya, ini adalah pesanan dengan status PENDING atau WAITING.

```
for row in new_orders_raw:
```
Mengulang setiap baris data mentah (tuple atau dict) yang dikembalikan dari database.

```
order = Order(...)
```
Ini adalah langkah kunci. Data mentah dari DB diubah menjadi objek Python Order yang terstruktur. Ini memudahkan manipulasi data di dalam scheduler tanpa harus bergantung pada indeks array DB (row[0], row[1], dll.).

```
self.queue.add_order(order)
```
Pesanan yang sudah menjadi objek Order ditambahkan ke ProductionPriorityQueue. Queue secara otomatis akan menempatkan pesanan ini sesuai prioritas (misalnya, berdasarkan deadline).

### method estimate_production_duration (Estimasi Durasi Produksi)
Method ini, meskipun terlihat sangat sederhana saat ini, memiliki peran yang sangat penting dalam sistem produksi di dunia nyata.

```
def estimate_production_duration(self, order: Order) -> float:
```
Menerima objek Order dan diharapkan mengembalikan estimasi waktu produksi dalam satuan waktu (misalnya, jam atau hari).

```
return 0.1
```
Saat ini, Anda mengembalikan nilai konstan 0.1. Ini adalah placeholder yang sangat umum.

Dalam implementasi yang lebih maju, method ini akan:
- Menghitung Kompleksitas: Menggunakan data di order.order_item untuk melihat jenis dan jumlah produk.
- Menghitung Resep: Memanggil DB untuk mendapatkan resep dan total bahan.
- Memperhitungkan Faktor: Menggunakan model untuk memperkirakan waktu berdasarkan sumber daya, kerumitan produk, dan pengalaman masa lalu.

Dengan return 0.1, Anda telah menyediakan kerangka kerja. Logika penjadwalan Anda di masa depan dapat menggunakan nilai ini untuk:
- Menghitung waktu penyelesaian (ETA).
- Menilai apakah pesanan dapat selesai sebelum deadline.

### method run_scheduling_cycle
Method run_scheduling_cycle ini adalah Algoritma Utama dari seluruh sistem. Ini adalah inti dari bagaimana pesanan diproses dan sumber daya dikelola.

#### a. Sinkronisasi dan Penyesuaian Prioritas
Ini adalah fase input dan validasi.

self._fetch_new_orders_from_db()
- Fungsi: Memeriksa database untuk pesanan baru (PENDING) yang mungkin masuk sejak siklus terakhir.
- Tujuan: Memastikan antrian (self.queue) selalu up-to-date dengan permintaan terbaru dari pelanggan.

self.stock_controller.check_and_update_all_priorities()
- Fungsi: Ini adalah panggilan method yang sangat penting. StockController akan memeriksa semua pesanan yang ada di antrian (self.queue).
- Logika Inti: Untuk setiap pesanan:<br>
Apakah semua bahan baku tersedia?<br>
Jika TIDAK tersedia (stok kurang), StockController mungkin akan menurunkan prioritas pesanan tersebut atau menandainya sebagai blocked.<br>
Jika YA tersedia, prioritasnya tetap terjaga (biasanya berdasarkan deadline).
- Tujuan: Mencegah mesin memulai pekerjaan yang tidak dapat diselesaikan karena kekurangan bahan baku.

#### b. Memeriksa Mesin yang Selesai Bekerja
Bagian ini bertujuan untuk menyelesaikan (finish) pekerjaan yang sudah berjalan dan membebaskan mesin.

```
for machine in self.machine:
    finished_order = machine.check_finish(self.db_client) 
    if finished_order:
        finished_orders.append(finished_order)
        self.stock_controller.adjust_stock_after_production(finished_order)
```
finished_order = machine.check_finish(self.db_client)
- Fungsi: Setiap ProductionMachine memeriksa jamnya sendiri. Jika waktu saat ini (time.time()) sudah melewati waktu penyelesaian yang direncanakan (finish_time), maka mesin akan: <br>
Mengubah status pesanan di DB menjadi COMPLETED. <br>
Mengubah status mesinnya menjadi IDLE. <br>
Mengembalikan objek pesanan yang baru selesai. <br>

self.stock_controller.adjust_stock_after_production(finished_order)
- Fungsi: Ini mengacu pada method yang Anda buat sebelumnya: deduct_ingredients_for_order (atau sejenisnya).
- Logika Inti: Setelah pesanan selesai, Stock Controller mengurangi stok bahan baku yang telah terpakai secara permanen dari inventaris di DB. Ini memastikan inventaris Anda selalu mencerminkan stok fisik yang tersisa.

#### c. Mengalokasikan Pekerjaan Baru ke Mesin yang IDLE
Ini adalah fase dispatching atau alokasi.

```
for machine in self.machine:
    if machine.status == MachineStatus.IDLE:
        # ... alokasi pekerjaan ...
```

if machine.status == MachineStatus.IDLE:
- Fungsi: Hanya mesin yang kosong (tidak sedang memproduksi) yang dipertimbangkan untuk pekerjaan baru.

next_order = self.queue.get_highest_priority_order()
- Fungsi: Mengambil pesanan dengan prioritas tertinggi dari antrian.
- Logika Kritis: Karena Langkah 1 sudah memastikan prioritas diurutkan (termasuk validasi stok), scheduler mengambil pesanan yang paling mendesak dan memiliki stok yang cukup. Jika antrian kosong, ini akan mengembalikan None.

duration = self.estimate_production_duration(next_order)
- Fungsi: Menghitung estimasi waktu yang diperlukan untuk menyelesaikan pesanan ini (saat ini 0.1, tetapi akan ditingkatkan).

machine.start_production(next_order, duration, self.db_client)
- Fungsi: Memulai pekerjaan pada mesin tersebut. Method ini akan:<br>
Mengubah status pesanan di DB menjadi IN_PROGRESS.<br>
Mengatur start_time dan finish_time pada objek mesin (start_time + duration).<br>
Mengubah status mesin menjadi BUSY.

run_scheduling_cycle adalah siklus Fetch -> Check/Adjust -> Finish -> Dispatch. Logika ini adalah model yang sangat efektif dan umum digunakan dalam sistem penjadwalan produksi:
- Prioritas (Keterdesakan)
- Ketersediaan Sumber Daya (Stok)
- Ketersediaan Mesin (IDLE)

### Method start_polling
Method start_polling ini mengubah ProductionScheduler dari sekadar koleksi fungsi menjadi service yang terus berjalan, mirip dengan cara kerja layanan latar belakang (background service) di dunia nyata.

#### a. pemberitahuan awal

```
print(f"--- Scheduler STARTED: ... {interval_seconds}s ---")
```
Menginformasikan user atau developer bahwa scheduler telah aktif dan menunjukkan konfigurasi utamanya (jumlah mesin dan interval pengecekan).

#### b. Main Loop

```
try: while True:
```
Memulai perulangan tak terbatas (while True). Ini adalah jantung dari service yang berjalan tanpa henti, memastikan scheduler selalu memantau dan memproses.

#### c. Eksekusi Siklus

```
self.run_scheduling_cycle()
```
Ini adalah inti dari loop. Pada setiap iterasi, scheduler melakukan tugas lengkapnya: mengambil pesanan baru, memeriksa stok, menyelesaikan pesanan yang selesai, dan mengirimkan pesanan baru ke mesin yang IDLE (seperti yang kita bahas sebelumnya).

#### d. Polling Interval

```
time.sleep(interval_seconds)
```
Menghentikan eksekusi loop sejenak selama interval_seconds. Ini penting untuk: 
1) Mengontrol laju konsumsi sumber daya CPU, dan 
2) Mensimulasikan pengecekan berkala (polling) terhadap database dan status mesin, alih-alih mengecek terus menerus.

#### e. Graceful Shutdown

```
except KeyboardInterrupt:
```
Menangkap sinyal Ctrl+C dari user atau terminal. Ini adalah cara yang aman (graceful) untuk menghentikan program tanpa mematikannya secara paksa.

#### f. Cleanup Koneksi DB

```
self.db_client.close()
```
Ini adalah langkah penting. Sebelum program benar-benar berhenti, ia memastikan koneksi database ditutup dengan benar dan aman. Ini mencegah kebocoran koneksi (connection leaks) di database server Anda.

