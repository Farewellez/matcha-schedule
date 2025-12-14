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