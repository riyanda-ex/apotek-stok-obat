# Apotek Stok Obat - V1.2 FINAL PERFECT (100% Aman, Sistematis, Berguna)
# Input: Data stok obat (nama, stok, minimal stok, tanggal expired, harga)
# Output: Status AMAN / STOK MENIPIS / MAU EXPIRED / EXPIRED / PERLU ORDER + Saran order
# DISCLAIMER: Alat bantu administrasi apotek, BUKAN pengganti keputusan apoteker.
# Semua obat expired WAJIB dipisahkan & dimusnahkan sesuai SOP, jangan dijual.

import json
import os
import re
from datetime import datetime, date

class ApotekStokObat:
    def __init__(self, config_path="config.json"):
        self.config = self.load_config(config_path)
        self.batas_menipis_default = self.config.get("batas_menipis_default", 10)
        self.batas_mau_expired_hari = self.config.get("batas_mau_expired_hari", 90)
        self.obat_wajib = self.config.get("obat_wajib", [])

    def load_config(self, path):
        base = os.path.dirname(__file__)
        full = os.path.join(base, path)
        try:
            with open(full, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print("WARNING: config.json tidak ditemukan, pakai aturan cadangan")
            return {"batas_menipis_default": 10, "batas_mau_expired_hari": 90, "obat_wajib": ["paracetamol"]}

    def normalisasi_nama(self, nama):
        # "Paracetamol 500mg!!!" -> "paracetamol 500mg" (huruf kecil, simbol dibuang)
        if not nama or not str(nama).strip():
            return ""
        bersih = str(nama).lower().strip()
        bersih = re.sub(r'[^a-z0-9 ]', '', bersih)
        bersih = re.sub(r'\s+', ' ', bersih).strip()
        return bersih

    def parse_tanggal(self, tanggal_str):
        # Terima "2027-06-30" atau "31/12/2027" atau "31-12-2027"
        if not tanggal_str or not str(tanggal_str).strip():
            return None
        s = str(tanggal_str).strip()
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d"):
            try:
                return datetime.strptime(s, fmt).date()
            except ValueError:
                continue
        return None

    def hitung_sisa_hari_expired(self, tanggal_expired, hari_ini=None):
        tgl = self.parse_tanggal(tanggal_expired)
        if tgl is None:
            return None
        if hari_ini is None:
            hari_ini = date.today()
        return (tgl - hari_ini).days

    def cek_satu_obat(self, nama_obat, stok, stok_minimal=None, tanggal_expired=None, harga=None, hari_ini=None, simpan=True):
        nama_bersih = self.normalisasi_nama(nama_obat)
        if not nama_bersih:
            print("ERROR: Nama obat kosong, tidak diproses.")
            return None
        try:
            stok_int = int(stok)
        except (ValueError, TypeError):
            print(f"ERROR: Stok '{stok}' bukan angka, tidak diproses.")
            return None
        if stok_int < 0:
            print("ERROR: Stok tidak boleh negatif.")
            return None
        if stok_minimal is None:
            stok_minimal = self.batas_menipis_default
        try:
            minimal_int = int(stok_minimal)
        except (ValueError, TypeError):
            minimal_int = self.batas_menipis_default
        if minimal_int < 0:
            minimal_int = 0

        sisa_hari = self.hitung_sisa_hari_expired(tanggal_expired, hari_ini=hari_ini)
        tanggal_expired_bersih = str(tanggal_expired).strip() if tanggal_expired else "-"

        masalah = []
        saran = []

        # 1. CEK EXPIRED - PRIORITAS 1
        is_expired = sisa_hari is not None and sisa_hari < 0
        is_mau_expired = sisa_hari is not None and 0 <= sisa_hari <= self.batas_mau_expired_hari

        if sisa_hari is None and tanggal_expired:
            masalah.append(f"Tanggal expired tidak valid: '{tanggal_expired}', pakai format YYYY-MM-DD")
            saran.append("Perbaiki tanggal expired ke format YYYY-MM-DD, contoh: 2027-01-31")

        if is_expired:
            masalah.append(f"EXPIRED {abs(sisa_hari)} hari lalu ({tanggal_expired_bersih}) - JANGAN DIJUAL")
            saran.append("Pisahkan segera, karantina, musnahkan sesuai SOP. Jangan dijual / jangan dipakai.")
        elif is_mau_expired:
            masalah.append(f"Mau expired dalam {sisa_hari} hari ({tanggal_expired_bersih})")
            saran.append("Prioritaskan jual / pakai dulu (FEFO), jangan order baru sebelum stok lama habis.")

        # 2. CEK STOK
        is_habis = stok_int == 0
        is_menipis = 0 < stok_int <= minimal_int

        if is_habis:
            masalah.append("Stok HABIS (0)")
            saran.append("Order segera, jangan terima resep obat ini sampai stok datang.")
        elif is_menipis:
            masalah.append(f"Stok menipis: sisa {stok_int}, minimal {minimal_int}")
            saran.append(f"Segera order, stok tinggal untuk {stok_int} pasien.")

        # 3. CEK OBAT WAJIB KOSONG
        daftar_wajib_bersih = [self.normalisasi_nama(o) for o in self.obat_wajib]
        if nama_bersih in daftar_wajib_bersih and is_habis:
            masalah.append(f"Obat wajib '{nama_bersih}' HABIS - risiko pelayanan terganggu")
            saran.append("Prioritas order 1 - obat wajib tidak boleh kosong.")

        # 4. HITUNG SARAN ORDER
        if is_expired:
            saran_order = 0
            alasan_order = "Tidak usah order, stok lama expired - musnahkan dulu & cek penyebabnya."
        elif is_habis or is_menipis:
            target = (minimal_int * 3) + 10
            saran_order = max(0, target - stok_int)
            alasan_order = f"Target stok aman {target} (minimal x 3 + 10), sisa {stok_int}."
        else:
            saran_order = 0
            alasan_order = "Stok masih aman, belum perlu order."

        # 5. TENTUKAN STATUS - EXPIRED SELALU MENANG
        if is_expired:
            status = "EXPIRED - JANGAN DIJUAL"
            skor = 0
        elif is_habis:
            status = "STOK HABIS - PERLU ORDER"
            skor = 20
        elif is_mau_expired and is_menipis:
            status = "MAU EXPIRED + STOK MENIPIS"
            skor = 40
        elif is_mau_expired:
            status = "MAU EXPIRED"
            skor = 60
        elif is_menipis:
            status = "STOK MENIPIS - PERLU ORDER"
            skor = 50
        else:
            status = "AMAN"
            skor = 100

        nilai_stok = None
        if harga is not None:
            try:
                nilai_stok = float(harga) * stok_int
            except (ValueError, TypeError):
                nilai_stok = None

        hasil = {
            "nama_obat": nama_bersih,
            "nama_obat_input": str(nama_obat),
            "tanggal_cek": datetime.now().strftime("%d %B %Y %H:%M"),
            "stok": stok_int,
            "stok_minimal": minimal_int,
            "tanggal_expired": tanggal_expired_bersih,
            "sisa_hari_expired": sisa_hari,
            "is_expired": is_expired,
            "is_mau_expired": is_mau_expired,
            "is_stok_habis": is_habis,
            "is_stok_menipis": is_menipis,
            "masalah": masalah,
            "saran": saran,
            "saran_order_jumlah": saran_order,
            "alasan_order": alasan_order,
            "status": status,
            "skor_stok": skor,
            "nilai_stok": nilai_stok,
            "disclaimer": "Alat bantu administrasi apotek, BUKAN pengganti keputusan apoteker. Obat expired wajib dimusnahkan sesuai SOP.",
        }

        self.tampilkan_hasil(hasil)
        if simpan:
            self.simpan_laporan(hasil)
        return hasil

    def cek_banyak_obat(self, daftar_obat, simpan=True):
        semua = []
        for item in (daftar_obat or []):
            r = self.cek_satu_obat(
                item.get("nama"), item.get("stok"), item.get("stok_minimal"),
                item.get("expired"), item.get("harga"), simpan=False
            )
            if r:
                semua.append(r)

        ringkasan = {
            "tanggal_cek": datetime.now().strftime("%d %B %Y %H:%M"),
            "total_obat_dicek": len(semua),
            "total_aman": sum(1 for x in semua if x["status"] == "AMAN"),
            "total_menipis": sum(1 for x in semua if "MENIPIS" in x["status"] or "HABIS" in x["status"]),
            "total_mau_expired": sum(1 for x in semua if x["is_mau_expired"]),
            "total_expired": sum(1 for x in semua if x["is_expired"]),
            "total_saran_order": sum(x["saran_order_jumlah"] for x in semua),
            "total_nilai_stok": sum(x["nilai_stok"] for x in semua if x["nilai_stok"] is not None),
            "daftar_perlu_tindakan": [x["nama_obat"] for x in semua if x["status"] != "AMAN"],
            "detail": semua,
            "disclaimer": "Alat bantu administrasi apotek, BUKAN pengganti keputusan apoteker.",
        }
        if simpan:
            self.simpan_ringkasan(ringkasan)
        return ringkasan

    def simpan_laporan(self, hasil):
        folder = os.path.join(os.path.dirname(__file__), "laporan")
        os.makedirs(folder, exist_ok=True)
        nama_file = f"{hasil['nama_obat'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        path = os.path.join(folder, nama_file)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(hasil, f, indent=2, ensure_ascii=False)
        print(f"Laporan disimpan: {path}")

    def simpan_ringkasan(self, ringkasan):
        folder = os.path.join(os.path.dirname(__file__), "laporan")
        os.makedirs(folder, exist_ok=True)
        nama_file = f"RINGKASAN_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        path = os.path.join(folder, nama_file)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(ringkasan, f, indent=2, ensure_ascii=False)
        print(f"Ringkasan disimpan: {path}")

    def tampilkan_hasil(self, h):
        print("\n========== CEK STOK OBAT ==========")
        print(f"Obat: {h['nama_obat']} | Stok: {h['stok']} (minimal {h['stok_minimal']})")
        print(f"Expired: {h['tanggal_expired']} | Sisa: {h['sisa_hari_expired']} hari" if h['sisa_hari_expired'] is not None else f"Expired: {h['tanggal_expired']}")
        print(f"Status: {h['status']} | Skor: {h['skor_stok']}/100")
        print(f"Saran Order: {h['saran_order_jumlah']} | {h['alasan_order']}")
        if h['masalah']:
            print("Masalah:")
            for m in h['masalah']:
                print(f" - {m}")
        if h['saran']:
            print("Saran:")
            for s in h['saran']:
                print(f" - {s}")
        print("=====================================")
        print("DISCLAIMER: Obat expired jangan dijual.")

if __name__ == "__main__":
    print("=== Apotek Stok Obat ===")
    print("DISCLAIMER: Alat bantu administrasi, BUKAN pengganti keputusan apoteker.")
    apotek = ApotekStokObat()

    # CONTOH - DATA SINTETIS, BUKAN DATA APOTEK ASLI
    apotek.cek_satu_obat("Paracetamol", 50, 10, "2027-06-30", 5000)
    apotek.cek_satu_obat("Amoxicillin", 5, 10, "2027-01-15", 12000)
    apotek.cek_satu_obat("Oralit", 0, 10, "2027-03-01", 3000)
    apotek.cek_satu_obat("Vitamin C", 20, 10, "2025-01-01", 8000)
    apotek.cek_satu_obat("Omeprazole", 8, 10, "2026-12-20", 15000)

    print("\n--- RINGKASAN HARIAN ---")
    ringkasan = apotek.cek_banyak_obat([
        {"nama": "Paracetamol", "stok": 50, "stok_minimal": 10, "expired": "2027-06-30", "harga": 5000},
        {"nama": "Amoxicillin", "stok": 5, "stok_minimal": 10, "expired": "2027-01-15", "harga": 12000},
        {"nama": "Oralit", "stok": 0, "stok_minimal": 10, "expired": "2027-03-01", "harga": 3000},
    ])
    print(f"Total dicek: {ringkasan['total_obat_dicek']} | Aman: {ringkasan['total_aman']} | Perlu tindakan: {len(ringkasan['daftar_perlu_tindakan'])}")
