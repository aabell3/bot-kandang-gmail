

<div class="container">
  <h1>🤖 Bot Kandang Gmail <span class="badge">v1.0.0</span></h1>
  <p>Bot Telegram modular berbasis Python untuk mengelola dan memfasilitasi tugas pembuatan akun Gmail (Task Farming) lengkap dengan sistem panel admin berjenjang (Tanggal ➔ Member ➔ Tugas) dan pencatatan saldo otomatis.</p>

  <div class="hr"></div>

  <h2>📂 Struktur Proyek Modular</h2>
  <p>Proyek ini dirancang secara modular agar kode tetap rapi, terorganisir, dan mudah dirawat:</p>
  <ul>
    <li><code>bot.py</code> : Logika utama bot, handler pesan, tombol interaktif (inline/reply), dan sistem navigasi admin.</li>
    <li><code>database.py</code> : Pengaturan koneksi SQLite, pembuatan tabel otomatis, dan manajemen konfigurasi sistem.</li>
    <li><code>config.py</code> : Konfigurasi token bot, daftar ID admin, dan data konstan.</li>
  </ul>

  <h2>⚙️ Fitur Utama</h2>
  <ul>
    <li><strong>Multi-Tasking Member:</strong> Member dapat mengambil dan mengerjakan beberapa tugas secara paralel tanpa harus menunggu tugas sebelumnya di-review.</li>
    <li><strong>Hierarchical Admin Panel:</strong> Review tugas admin yang terstruktur rapi berdasarkan Tanggal ➔ Nama Member ➔ Task ID.</li>
    <li><strong>Auto-Generation:</strong> Pembuatan nama depan/belakang otomatis menggunakan pustaka <code>Faker</code> (lokalisasi <code>id_ID</code>) serta pola email & password dinamis.</li>
    <li><strong>Sistem Saldo & Statistik:</strong> Pengecekan saldo, riwayat hold balance, jumlah tugas approved/rejected, dan statistik akun.</li>
  </ul>

  <h2>🚀 Panduan Instalasi & Pengaturan Awal (Termux)</h2>
  <p>Ikuti langkah-langkah di bawah ini untuk menyiapkan dan menjalankan bot dari awal di Termux:</p>

  <h3>1. Membuat Bot di Telegram (BotFather)</h3>
  <ol>
    <li>Buka aplikasi Telegram, cari dan buka bot resmi <strong>@BotFather</strong>.</li>
    <li>Kirim perintah <code>/newbot</code> untuk membuat bot baru.</li>
    <li>Masukkan nama bot Anda (contoh: <code>Kandang Gmail</code>).</li>
    <li>Masukkan username bot Anda (harus berakhiran <code>bot</code>, contoh: <code>kandang_gmail_bot</code>).</li>
    <li>BotFather akan memberikan <strong>HTTP API Token</strong> (simpan token ini).</li>
  </ol>

  <h3>2. Mendapatkan Telegram Admin ID</h3>
  <ol>
    <li>Cari dan buka bot <strong>@userinfobot</strong> di Telegram.</li>
    <li>Kirim pesan apa saja, dan bot akan membalas dengan menampilkan <strong>ID</strong> akun Telegram Anda (contoh: <code>5711825456</code>).</li>
  </ol>

  <h3>3. Update & Install Paket Dasar di Termux</h3>
  <p>Buka aplikasi Termux Anda, lalu jalankan perintah berikut:</p>
  <pre><code>pkg update && pkg upgrade -y
pkg install python git -y
pip install --upgrade pip</code></pre>

  <h3>4. Install Pustaka Python yang Dibutuhkan</h3>
  <p>Install pustaka <code>python-telegram-bot</code> dan <code>Faker</code> dengan perintah:</p>
  <pre><code>pip install python-telegram-bot faker</code></pre>

  <h3>5. Clone Repository dari GitHub</h3>
  <p>Jalankan perintah <code>git clone</code> untuk mengunduh proyek. Git akan otomatis membuatkan folder <code>bot-kandang-gmail</code>:</p>
  <pre><code>cd ~
git clone https://github.com/aabell3/bot-kandang-gmail.git
cd bot-kandang-gmail</code></pre>

  <h3>6. Konfigurasi Token & Admin ID</h3>
  <p>Sesuaikan Token Bot dan Admin ID Anda di dalam file <code>config.py</code>:</p>
  <pre><code>nano config.py</code></pre>
  <p>Masukkan Token dari BotFather dan ID Telegram Anda, lalu simpan dengan menekan <code>Ctrl + O</code>, tekan <code>Enter</code>, lalu <code>Ctrl + X</code>.</p>

  <h2>▶️ Cara Menjalankan Bot</h2>
  <p>Setelah berada di dalam folder <code>bot-kandang-gmail</code>, jalankan bot dengan perintah:</p>
  <pre><code>python bot.py</code></pre>
  <p>Jika berhasil, terminal akan menampilkan pesan: <code>Bot modular siap dijalankan...</code></p>

  <h2>🔄 Cara Update Kode dari GitHub</h2>
  <p>Jika Anda melakukan perubahan atau pembaruan kode langsung melalui web GitHub dan ingin menerapkannya ke Termux:</p>
  <ol>
    <li>Matikan bot yang sedang berjalan di Termux dengan menekan <code>Ctrl + C</code>.</li>
    <li>Masuk ke folder bot dan tarik pembaruan terbaru:
      <pre><code>cd ~/bot-kandang-gmail
git pull origin main</code></pre>
    </li>
    <li>Jalankan kembali bot:
      <pre><code>python bot.py</code></pre>
    </li>
  </ol>

</div>
