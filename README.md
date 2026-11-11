# 💊 Apotek Stok Obat

[Python](https://img.shields.io/badge/Python-3.11-blue)
[Tests](https://github.com/riyanda-ex/apotek-stok-obat/actions/workflows/test.yml/badge.svg)
[License](https://img.shields.io/badge/License-MIT-green)
[Status](https://img.shields.io/badge/Status-Selesai-green)
[Klinik](https://img.shields.io/badge/Klinik-Al%20Madina%20Husada-teal)

Manajemen stok obat apotek otomatis. Cek expired, stok menipis, stok habis, & hitung saran order. Biar apotek nggak kehabisan obat & nggak jual obat expired.

Dibuat untuk Klinik Al Madina Husada, Nganjuk.

> **Disclaimer:** Alat bantu administrasi apotek, BUKAN pengganti keputusan apoteker. Obat expired WAJIB dipisahkan & dimusnahkan sesuai SOP, jangan dijual.

## ✨ Fitur
- Cek expired & mau expired (90 hari ke depan)
- Cek stok habis & stok menipis
- Saran order otomatis (target = minimal x 3 + 10)
- Hitung nilai stok (stok x harga)
- Ringkasan harian banyak obat sekaligus
- Terima format tanggal `YYYY-MM-DD` & `DD/MM/YYYY`
- Tolak input ngawur: stok negatif, stok bukan angka, nama kosong
- Simpan laporan JSON ke `laporan/`
- 15 Test Otomatis

## 🚀 Cara Pakai
```bash
python main.py
# atau
python test.py
