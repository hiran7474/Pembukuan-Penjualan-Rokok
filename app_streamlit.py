import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# ---------------------------------------------------------
# SETUP HALAMAN
# ---------------------------------------------------------
st.set_page_config(page_title="Pembukuan Penjualan Rokok", layout="wide")

# Inisialisasi Koneksi Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    # Ambil data terbaru dari Google Sheets
    df = conn.read(ttl=0)
    
    if df is None or df.empty:
        return pd.DataFrame(columns=[
            "Kode", "Nama Barang", "Kategori", "Harga Beli", 
            "Harga Jual", "Stok Awal", "Total Restok", "Total Keluar", "Satuan"
        ])
    
    numeric_cols = ["Harga Beli", "Harga Jual", "Stok Awal", "Total Restok", "Total Keluar"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
            
    return df

def save_data(df_to_save):
    # Simpan/update data kembali ke Google Sheets
    conn.update(data=df_to_save)
    st.cache_data.clear()

# Load Data
try:
    df_barang = load_data()
except Exception as e:
    st.error(f"Gagal terhubung ke Google Sheets. Pastikan Baris 1 di Google Sheet berisi nama kolom header. Error: {e}")
    st.stop()

df = df_barang.copy()

# ---------------------------------------------------------
# KALKULASI FINANSIAL & STOK
# ---------------------------------------------------------
if not df.empty and "Stok Awal" in df.columns:
    df["Sisa Stok"] = df["Stok Awal"] + df["Total Restok"] - df["Total Keluar"]
    df["Total Omset"] = df["Total Keluar"] * df["Harga Jual"]
    df["Total HPP (Modal)"] = df["Total Keluar"] * df["Harga Beli"]
    df["Laba Kotor Total"] = df["Total Omset"] - df["Total HPP (Modal)"]

    total_cash_omset = df["Total Omset"].sum()
    total_modal_hpp = df["Total HPP (Modal)"].sum()
    total_laba_kotor = df["Laba Kotor Total"].sum()

    bagi_hasil = total_laba_kotor * 0.50
    setoran_pemilik = total_modal_hpp + bagi_hasil
    bagian_pengelola = bagi_hasil
else:
    total_cash_omset = total_modal_hpp = total_laba_kotor = 0
    bagi_hasil = setoran_pemilik = bagian_pengelola = 0

# ---------------------------------------------------------
# SIDEBAR MENU
# ---------------------------------------------------------
st.sidebar.title("📦 Menu Utama")

fitur = st.sidebar.radio(
    "Pilih Fitur:",
    [
        "📊 Dashboard & Laporan Setoran", 
        "➕ Restok (Barang Masuk)", 
        "🛒 Penjualan (Barang Keluar)", 
        "⚙️ Kelola Master Barang", 
        "🛠️ Edit / Hapus Barang & Reset"
    ]
)

st.sidebar.markdown("---")
st.sidebar.caption("👨‍💻 **Pengelola:** Hiran © 2026")

# ---------------------------------------------------------
# 1. HALAMAN DASHBOARD
# ---------------------------------------------------------
if fitur == "📊 Dashboard & Laporan Setoran":
    
    st.subheader("💰 Ringkasan Uang Penjualan Terkumpul")
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Cash Omset Penjualan", f"Rp {total_cash_omset:,.0f}".replace(",", "."))
    m2.metric("Pengembalian Modal (HPP)", f"Rp {total_modal_hpp:,.0f}".replace(",", "."))
    m3.metric("Total Laba Bersih/Kotor", f"Rp {total_laba_kotor:,.0f}".replace(",", "."))
    
    st.markdown("---")
    
    st.subheader("🤝 Rincian Pembagian Setoran & Profit (50:50)")
    r1, r2, r3 = st.columns(3)
    r1.metric("🏦 SETORAN KE PEMILIK MODAL", f"Rp {setoran_pemilik:,.0f}".replace(",", "."))
    r2.metric("👤 Bagi Hasil Pemilik (50%)", f"Rp {bagi_hasil:,.0f}".replace(",", "."))
    r3.metric("🧑‍💼 Bagi Hasil Pengelola (50%)", f"Rp {bagian_pengelola:,.0f}".replace(",", "."))
    
    st.info(
        f"💡 **Penjelasan Kas:** Dari total uang tunai terkumpul (Rp {total_cash_omset:,.0f}), "
        f"sebesar **Rp {setoran_pemilik:,.0f}** disetorkan ke Pemilik Modal "
        f"(Pengembalian Modal Rp {total_modal_hpp:,.0f} + 50% Laba Rp {bagi_hasil:,.0f}). "
        f"Pengelola mengantongi **Rp {bagian_pengelola:,.0f}**.".replace(",", ".")
    )
    
    st.markdown("---")
    
    st.subheader("📋 Laporan Detail Stok & Penjualan Per Produk")
    
    if not df.empty:
        tabel_tampil = df[[
            "Kode", "Nama Barang", "Kategori", "Harga Beli", "Harga Jual", 
            "Stok Awal", "Total Restok", "Total Keluar", "Sisa Stok", 
            "Total Omset", "Total HPP (Modal)", "Laba Kotor Total", "Satuan"
        ]].copy()
        
        tabel_formatted = tabel_tampil.copy()
        for col in ["Harga Beli", "Harga Jual", "Total Omset", "Total HPP (Modal)", "Laba Kotor Total"]:
            tabel_formatted[col] = tabel_formatted[col].apply(lambda x: f"Rp {x:,.0f}".replace(",", "."))
        
        st.dataframe(tabel_formatted, use_container_width=True)
        
        csv_data = tabel_tampil.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Unduh Laporan Stok & Keuangan (CSV)",
            data=csv_data,
            file_name='Laporan_Pembukuan_Rokok.csv',
            mime='text/csv',
        )
    else:
        st.warning("Belum ada data barang di Google Sheets.")

# ---------------------------------------------------------
# 2. RESTOK (BARANG MASUK)
# ---------------------------------------------------------
elif fitur == "➕ Restok (Barang Masuk)":
    st.title("➕ Input Restok Barang Masuk")
    if not df.empty and "Nama Barang" in df.columns:
        pilihan_barang = st.selectbox("Pilih Barang:", df["Nama Barang"].tolist())
        jumlah_masuk = st.number_input("Jumlah Masuk (Bungkus):", min_value=1, step=1)
        
        if st.button("Simpan Restok"):
            idx = df[df["Nama Barang"] == pilihan_barang].index[0]
            df.at[idx, "Total Restok"] += jumlah_masuk
            
            save_data(df[["Kode", "Nama Barang", "Kategori", "Harga Beli", "Harga Jual", "Stok Awal", "Total Restok", "Total Keluar", "Satuan"]])
            st.success(f"Berhasil menambahkan restok {jumlah_masuk} Bungkus untuk {pilihan_barang}!")
            st.rerun()
    else:
        st.warning("Belum ada data barang di Google Sheets.")

# ---------------------------------------------------------
# 3. PENJUALAN (BARANG KELUAR)
# ---------------------------------------------------------
elif fitur == "🛒 Penjualan (Barang Keluar)":
    st.title("🛒 Input Penjualan Barang Keluar")
    if not df.empty and "Nama Barang" in df.columns:
        pilihan_barang = st.selectbox("Pilih Barang:", df["Nama Barang"].tolist())
        jumlah_keluar = st.number_input("Jumlah Keluar / Terjual (Bungkus):", min_value=1, step=1)
        
        if st.button("Simpan Penjualan"):
            idx = df[df["Nama Barang"] == pilihan_barang].index[0]
            df.at[idx, "Total Keluar"] += jumlah_keluar
            
            save_data(df[["Kode", "Nama Barang", "Kategori", "Harga Beli", "Harga Jual", "Stok Awal", "Total Restok", "Total Keluar", "Satuan"]])
            st.success(f"Berhasil mencatat penjualan {jumlah_keluar} Bungkus untuk {pilihan_barang}!")
            st.rerun()
    else:
        st.warning("Belum ada data barang di Google Sheets.")

# ---------------------------------------------------------
# 4. KELOLA MASTER BARANG
# ---------------------------------------------------------
elif fitur == "⚙️ Kelola Master Barang":
    st.title("⚙️ Tambah Master Barang Baru")
    with st.form("form_barang_baru"):
        kode = st.text_input("Kode Barang:", value=f"BRG00{len(df)+1}")
        nama = st.text_input("Nama Barang:")
        kategori = st.selectbox("Kategori:", ["Rokok Filter", "Rokok Kretek", "Rokok Putih", "Lainnya"])
        harga_beli = st.number_input("Harga Beli Modal (per Bungkus):", min_value=0, step=1000, format="%d")
        harga_jual = st.number_input("Harga Jual (per Bungkus):", min_value=0, step=1000, format="%d")
        stok_awal = st.number_input("Stok Awal (Bungkus):", min_value=0, step=1)
        satuan = st.text_input("Satuan:", value="Bungkus")
        
        submitted = st.form_submit_button("Tambah Barang Ke Google Sheets")
        if submitted:
            if not nama:
                st.error("Nama Barang tidak boleh kosong!")
            else:
                baris_baru = {
                    "Kode": kode, "Nama Barang": nama, "Kategori": kategori, 
                    "Harga Beli": harga_beli, "Harga Jual": harga_jual, 
                    "Stok Awal": stok_awal, "Total Restok": 0, "Total Keluar": 0, "Satuan": satuan
                }
                df_update = pd.concat([df, pd.DataFrame([baris_baru])], ignore_index=True)
                save_data(df_update[["Kode", "Nama Barang", "Kategori", "Harga Beli", "Harga Jual", "Stok Awal", "Total Restok", "Total Keluar", "Satuan"]])
                st.success(f"Barang {nama} berhasil ditambahkan!")
                st.rerun()

# ---------------------------------------------------------
# 5. EDIT, HAPUS & RESET
# ---------------------------------------------------------
elif fitur == "🛠️ Edit / Hapus Barang & Reset":
    st.title("🛠️ Pengelolaan Data Barang & Reset")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "✏️ Edit Master Barang", 
        "🔄 Koreksi Penjualan & Restok", 
        "🗑️ Hapus Barang", 
        "🧹 Reset Transaksi"
    ])
    
    # EDIT MASTER
    with tab1:
        st.subheader("✏️ Edit Detail & Harga Barang")
        if not df.empty and "Nama Barang" in df.columns:
            pilih_edit = st.selectbox("Pilih Barang yang Ingin Di-edit:", df["Nama Barang"].tolist(), key="select_edit")
            idx = df[df["Nama Barang"] == pilih_edit].index[0]
            row = df.loc[idx]
            
            with st.form("form_edit_barang"):
                edit_kode = st.text_input("Kode Barang:", value=row["Kode"])
                edit_nama = st.text_input("Nama Barang:", value=row["Nama Barang"])
                edit_kat = st.selectbox("Kategori:", ["Rokok Filter", "Rokok Kretek", "Rokok Putih", "Lainnya"], index=0)
                edit_hb = st.number_input("Harga Beli Modal:", min_value=0, value=int(row["Harga Beli"]), step=1000)
                edit_hj = st.number_input("Harga Jual:", min_value=0, value=int(row["Harga Jual"]), step=1000)
                edit_sa = st.number_input("Stok Awal (Bungkus):", min_value=0, value=int(row["Stok Awal"]), step=1)
                edit_sat = st.text_input("Satuan:", value=row["Satuan"])
                
                simpan_edit = st.form_submit_button("Simpan Perubahan")
                if simpan_edit:
                    df.at[idx, "Kode"] = edit_kode
                    df.at[idx, "Nama Barang"] = edit_nama
                    df.at[idx, "Kategori"] = edit_kat
                    df.at[idx, "Harga Beli"] = edit_hb
                    df.at[idx, "Harga Jual"] = edit_hj
                    df.at[idx, "Stok Awal"] = edit_sa
                    df.at[idx, "Satuan"] = edit_sat
                    save_data(df[["Kode", "Nama Barang", "Kategori", "Harga Beli", "Harga Jual", "Stok Awal", "Total Restok", "Total Keluar", "Satuan"]])
                    st.success(f"Data {edit_nama} berhasil diperbarui!")
                    st.rerun()

    # KOREKSI TRANSAKSI
    with tab2:
        st.subheader("🔄 Koreksi Total Penjualan & Restok")
        if not df.empty and "Nama Barang" in df.columns:
            pilih_koreksi = st.selectbox("Pilih Barang yang Ingin Dikoreksi:", df["Nama Barang"].tolist(), key="select_koreksi")
            idx_k = df[df["Nama Barang"] == pilih_koreksi].index[0]
            row_k = df.loc[idx_k]
            
            with st.form("form_koreksi_transaksi"):
                kor_restok = st.number_input("Total Restok (Bungkus):", min_value=0, value=int(row_k["Total Restok"]), step=1)
                kor_keluar = st.number_input("Total Terjual (Bungkus):", min_value=0, value=int(row_k["Total Keluar"]), step=1)
                
                simpan_koreksi = st.form_submit_button("Simpan Koreksi")
                if simpan_koreksi:
                    df.at[idx_k, "Total Restok"] = kor_restok
                    df.at[idx_k, "Total Keluar"] = kor_keluar
                    save_data(df[["Kode", "Nama Barang", "Kategori", "Harga Beli", "Harga Jual", "Stok Awal", "Total Restok", "Total Keluar", "Satuan"]])
                    st.success(f"Koreksi transaksi {row_k['Nama Barang']} berhasil disimpan!")
                    st.rerun()

    # HAPUS BARANG
    with tab3:
        st.subheader("🗑️ Hapus Barang dari Sistem")
        if not df.empty and "Nama Barang" in df.columns:
            pilih_hapus = st.selectbox("Pilih Barang yang Ingin Dihapus:", df["Nama Barang"].tolist(), key="select_hapus")
            if st.button("❌ Hapus Barang Ini", type="primary"):
                df = df[df["Nama Barang"] != pilih_hapus].reset_index(drop=True)
                save_data(df[["Kode", "Nama Barang", "Kategori", "Harga Beli", "Harga Jual", "Stok Awal", "Total Restok", "Total Keluar", "Satuan"]])
                st.success(f"Barang {pilih_hapus} berhasil dihapus!")
                st.rerun()

    # RESET TRANSAKSI
    with tab4:
        st.subheader("🧹 Reset Angka Transaksi")
        if st.button("Reset Semua Transaksi Penjualan & Restok"):
            df["Total Restok"] = 0
            df["Total Keluar"] = 0
            save_data(df[["Kode", "Nama Barang", "Kategori", "Harga Beli", "Harga Jual", "Stok Awal", "Total Restok", "Total Keluar", "Satuan"]])
            st.success("Semua angka penjualan & restok berhasil di-reset ke 0!")
            st.rerun()
