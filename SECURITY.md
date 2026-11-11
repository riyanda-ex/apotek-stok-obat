# Keamanan

## Jangan Laporkan Data Asli di Issue Publik
Jangan pernah upload faktur supplier, harga beli asli, data penjualan, nama pasien, atau foto stok apotek ke GitHub Issue.

## Melaporkan Celah Keamanan
Hubungi pemilik repo melalui GitHub secara privat.
Jelaskan: file yang bermasalah, langkah reproduksi, dan dampaknya.

## Prinsip
- Data apotek asli tidak pernah disimpan di repo ini.
- Hanya data sintetis (contoh) yang boleh di-commit.
- File faktur / Excel / database diblokir oleh `.gitignore`.
- Obat expired wajib dimusnahkan sesuai SOP, sistem ini hanya pengingat.
