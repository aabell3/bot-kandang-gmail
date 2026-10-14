# 🤖 Bot Kandang Gmail

Bot Telegram modular berbasis Python untuk mengelola dan memfasilitasi tugas pembuatan akun Gmail (Task Farming) lengkap dengan sistem panel admin berjenjang (Tanggal ➔ Member ➔ Tugas) dan pencatatan saldo otomatis.

---

## 📂 Struktur Proyek
Proyek ini dirancang secara modular agar lebih rapi dan mudah dirawat:
- `bot.py` : Logika utama bot, *handler* pesan, tombol interaktif (*inline/reply*), dan sistem navigasi admin.
- `database.py` : Pengaturan koneksi SQLite, pembuatan tabel otomatis, dan manajemen konfigurasi sistem.
- `config.py` : Konfigurasi token bot, daftar ID admin, dan data konstan.

---

## ⚙️ Fitur Utama
- **Multi-Tasking Member:** Member dapat mengambil dan mengerjakan beberapa tugas secara paralel tanpa harus menunggu tugas sebelumnya di-review.
- **Hierarchical Admin Panel:** Review tugas admin yang terstruktur rapi berdasarkan Tanggal ➔ Nama Member ➔ Task ID.
- **Auto-Generation:** Pembuatan nama depan/belakang otomatis menggunakan pustaka `Faker` (lokalisasi `id_ID`) serta pola email & password dinamis.
- **Sistem Saldo & Statistik:** Pengecekan saldo, riwayat *hold balance*, jumlah tugas *approved/rejected*, dan statistik akun.

---

## 🚀 Panduan Instalasi (Termux)

Ikuti langkah-langkah di bawah ini untuk menginstal dan menjalankan bot dari awal di Termux:

### 1. Update & Install Ketergantungan (Dependencies)
Buka aplikasi Termux Anda, lalu jalankan perintah berikut untuk memastikan Python, Git, dan pustaka pendukung terinstal:
```bash
pkg update && pkg upgrade -y
pkg install python git -y
pip install --upgrade pip
