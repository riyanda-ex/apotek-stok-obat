# Test otomatis - Apotek Stok Obat V1.2 PERFECT
import os, sys
from datetime import date, timedelta
sys.path.insert(0, os.path.dirname(__file__))
from main import ApotekStokObat

def test(nama, kondisi):
    print(f"{'✅' if kondisi else '❌'} {nama}")
    return kondisi

if __name__ == "__main__":
    print("=== TEST Apotek Stok Obat ===\n")
    a = ApotekStokObat()
    hasil = []
    hari_ini = date.today()
    jauh = (hari_ini + timedelta(days=365)).strftime("%Y-%m-%d")
    dekat = (hari_ini + timedelta(days=30)).strftime("%Y-%m-%d")
    lewat = (hari_ini - timedelta(days=10)).strftime("%Y-%m-%d")

    r1 = a.cek_satu_obat("Paracetamol", 50, 10, jauh, 5000, simpan=False)
    hasil.append(test("1. Stok aman -> AMAN 100", r1["status"] == "AMAN" and r1["skor_stok"] == 100 and r1["saran_order_jumlah"] == 0))
    r2 = a.cek_satu_obat("Amoxicillin", 5, 10, jauh, 12000, simpan=False)
    hasil.append(test("2. Stok menipis ketahuan + saran order > 0", "MENIPIS" in r2["status"] and r2["saran_order_jumlah"] > 0))
    r3 = a.cek_satu_obat("Oralit", 0, 10, jauh, 3000, simpan=False)
    hasil.append(test("3. Stok habis -> HABIS", "HABIS" in r3["status"] and r3["saran_order_jumlah"] > 0))
    r4 = a.cek_satu_obat("Vitamin C", 20, 10, lewat, 8000, simpan=False)
    hasil.append(test("4. Expired ketahuan + order 0", "EXPIRED" in r4["status"] and r4["saran_order_jumlah"] == 0 and r4["skor_stok"] == 0))
    r5 = a.cek_satu_obat("Omeprazole", 50, 10, dekat, 15000, simpan=False)
    hasil.append(test("5. Mau expired ketahuan", "MAU EXPIRED" in r5["status"] and r5["is_mau_expired"] is True))
    r6 = a.cek_satu_obat("", 10, 10, jauh, simpan=False)
    hasil.append(test("6. Nama kosong ditolak", r6 is None))
    r7 = a.cek_satu_obat("Paracetamol", -5, 10, jauh, simpan=False)
    hasil.append(test("7. Stok negatif ditolak", r7 is None))
    r8 = a.cek_satu_obat("Paracetamol", "abc", 10, jauh, simpan=False)
    hasil.append(test("8. Stok bukan angka ditolak", r8 is None))
    r9 = a.cek_satu_obat("Paracetamol 500mg!!!", 50, 10, jauh, simpan=False)
    hasil.append(test("9. Normalisasi nama bersih", r9["nama_obat"] == "paracetamol 500mg"))
    r10 = a.cek_satu_obat("Cetirizine", 50, 10, "31/12/2027", simpan=False)
    hasil.append(test("10. Format 31/12/2027 diterima", r10["sisa_hari_expired"] is not None and r10["sisa_hari_expired"] > 0))
    r11 = a.cek_satu_obat("Cetirizine", 50, 10, "ngawur", simpan=False)
    hasil.append(test("11. Tanggal tidak valid tidak crash", r11 is not None and len(r11["masalah"]) >= 1))
    ring = a.cek_banyak_obat([
        {"nama": "Paracetamol", "stok": 50, "stok_minimal": 10, "expired": jauh, "harga": 5000},
        {"nama": "Oralit", "stok": 0, "stok_minimal": 10, "expired": jauh, "harga": 3000},
    ], simpan=False)
    hasil.append(test("12. Ringkasan banyak obat jalan", ring["total_obat_dicek"] == 2 and ring["total_expired"] == 0 and "oralit" in ring["daftar_perlu_tindakan"]))
    hasil.append(test("13. Disclaimer ada", "apoteker" in r1["disclaimer"].lower() and "musnahkan" in r1["disclaimer"].lower()))
    hasil.append(test("14. Config terload", a.batas_menipis_default == 10 and len(a.obat_wajib) >= 3))
    hasil.append(test("15. Nilai stok benar", r1["nilai_stok"] == 250000))

    lulus = sum(hasil)
    print(f"\nHASIL: {lulus}/{len(hasil)} lulus")
    if lulus == len(hasil):
        print("🎉 SEMUA TEST LULUS!")
    else:
        print("⚠️ Ada test gagal, cek di atas.")
        sys.exit(1)
