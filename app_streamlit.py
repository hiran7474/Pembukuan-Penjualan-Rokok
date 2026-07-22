import streamlit as st
import pandas as pd

# Page config biar rapi & lebar
st.set_page_config(page_title="Pembukuan Rokok", layout="wide")

# ---------------------------------------------------------
# 1. DATABASE & SESSION STATE
# ---------------------------------------------------------
if 'df_barang' not in st.session_state:
    st.session_state.df_barang = pd.DataFrame([
        {"Kode": "BRG001", "Nama Barang": "Sampoerna Mild 16", "Kategori": "Rokok Filter", "Harga Beli": 28000, "Harga Jual": 31000, "Stok Awal": 50, "Total Restok": 20, "Total Keluar": 12, "Satuan": "Slop"},
        {"Kode": "BRG002", "Nama Barang": "Gudang Garam Surya 12", "Kategori": "Rokok Filter", "Harga Beli": 22000, "Harga Jual": 24500, "Stok Awal": 30, "Total Restok": 15, "Total Keluar": 10, "Satuan": "Slop"},
        {"Kode": "BRG003", "Nama Barang": "Djarum Super 12", "Kategori": "Rokok Filter", "Harga Beli": 21000, "Harga Jual": 23500, "Stok Awal": 15, "Total Restok": 0, "Total Keluar": 0, "Satuan": "Slop"},
        {"Kode": "BRG004", "Nama Barang": "Dji Sam Soe 234 12", "Kategori": "Rokok Kretek", "Harga Beli": 20000, "Harga Jual": 22000, "Stok Awal": 40, "Total Restok": 0, "Total Keluar": 0, "Satuan": "Slop"}
    ])

df = st.session_state.df_barang.copy()

# ---------------------------------------------------------
# 2. KALKULASI FINANSIAL & STOK
# ---------------------------------------------------------
df["Sisa Stok"] = df["Stok Awal"] + df["Total Restok"] - df["Total Keluar"]
df["Total Omset"] = df["Total Keluar"] * df["Harga Jual"]
df["Total HPP (Modal)"] = df["Total Keluar"] * df["Harga Beli"]
df["Laba Kotor Total"] = df["Total Omset"] - df["Total HPP (Modal)"]

total_jenis = len(df)
total_restok = df["Total Restok"].sum()
total_keluar = df["Total Keluar"].sum()
stok_menipis = len(df[df["Sisa Stok"] <= 10])

total_cash_omset = df["Total Omset"].sum()
total_modal_hpp = df["Total HPP (Modal)"].sum()
total_laba_kotor = df["Laba Kotor Total"].sum()

# Pembagian Keuangan 50:50
bagi_hasil = total_laba_kotor * 0.50
setoran_pemilik = total_modal_hpp + bagi_hasil
bagian_pengelola = bagi_hasil

# ---------------------------------------------------------
# 3. SIDEBAR MENU
# ---------------------------------------------------------
st.sidebar.title("📦 Menu Utama")

fitur = st.sidebar.radio(
    "Pilih Fitur:",
    [
        "📊 Dashboard & Laporan Setoran", 
        "➕ Restok (Barang Masuk)", 
        "🛒 Penjualan (Barang Keluar)", 
        "⚙️ Kelola Master Barang", 
        "🧹 Hapus/Edit Riwayat & Reset"
    ]
)

# ---------------------------------------------------------
# 4. HALAMAN DASHBOARD & LAPORAN
# ---------------------------------------------------------
if fitur == "📊 Dashboard & Laporan Setoran":
    
    # --- RINGKASAN UANG PENJUALAN ---
    st.subheader("💰 Ringkasan Uang Penjualan Terkumpul")
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Cash Omset Penjualan", f"Rp {total_cash_omset:,.0f}".replace(",", "."))
    m2.metric("Pengembalian Modal (HPP)", f"Rp {total_modal_hpp:,.0f}".replace(",", "."))
    m3.metric("Total Laba Bersih/Kotor", f"Rp {total_laba_kotor:,.0f}".replace(",", "."))
    
    st.markdown("---")
    
    # --- RINCIAN PEMBAGIAN SETORAN ---
    st.subheader("🤝 Rincian Pembagian Setoran & Profit (50:50)")
    r1, r2, r3 = st.columns(3)
    r1.metric("🏦 SETORAN KE PEMILIK MODAL", f"Rp {setoran_pemilik:,.0f}".replace(",", "."))
    r2.metric("👤 Bagi Hasil Pemilik (50%)", f"Rp {bagi_hasil:,.0f}".replace(",", "."))
    r3.metric("🧑‍💼 Bagi Hasil Pengelola (50%)", f"Rp {bagian_pengelola:,.0f}".replace(",", "."))
    
    # Kotak Penjelasan Kas (Biru)
    st.info(
        f"💡 **Penjelasan Kas:** Dari total uang tunai terkumpul (Rp {total_cash_omset:,.0f}), "
        f"sebesar **Rp {setoran_pemilik:,.0f}** disetorkan ke Pemilik Modal "
        f"(Pengembalian Modal Rp {total_modal_hpp:,.0f} + 50% Laba Rp {bagi_hasil:,.0f}). "
        f"Pengelola mengantongi **Rp {bagian_pengelola:,.0f}**.".replace(",", ".")
    )
    
    st.markdown("---")
    
    # --- LAPORAN DETAIL TABEL ---
    st.subheader("📋 Laporan Detail Stok & Penjualan Per Produk")
    
    tabel_tampil = df[[
        "Kode", "Nama Barang", "Kategori", "Harga Beli", "Harga Jual", 
        "Stok Awal", "Total Restok", "Total Keluar", "Sisa Stok", 
        "Total Omset", "Total HPP (Modal)", "Laba Kotor Total", "Satuan"
    ]]
    
    st.dataframe(tabel_tampil, use_container_width=True)
    
    # Tombol Unduh File
    csv_data = tabel_tampil.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Unduh Laporan Stok & Keuangan (CSV / Excel)",
        data=csv_data,
        file_name='Laporan_Pembukuan_Rokok.csv',
        mime='text/csv',
    )

elif fitur == "➕ Restok (Barang Masuk)":
    st.title("➕ Input Restok Barang Masuk")
    pilihan_barang = st.selectbox("Pilih Barang:", df["Nama Barang"].tolist())
    jumlah_masuk = st.number_input("Jumlah Masuk (Slop):", min_value=1, step=1)
    
    if st.button("Simpan Restok"):
        idx = st.session_state.df_barang[st.session_state.df_barang["Nama Barang"] == pilihan_barang].index[0]
        st.session_state.df_barang.at[idx, "Total Restok"] += jumlah_masuk
        st.success(f"Berhasil menambahkan restok {jumlah_masuk} Slop untuk {pilihan_barang}!")
        st.rerun()

elif fitur == "🛒 Penjualan (Barang Keluar)":
    st.title("🛒 Input Penjualan Barang Keluar")
    pilihan_barang = st.selectbox("Pilih Barang:", df["Nama Barang"].tolist())
    jumlah_keluar = st.number_input("Jumlah Keluar / Terjual (Slop):", min_value=1, step=1)
    
    if st.button("Simpan Penjualan"):
        idx = st.session_state.df_barang[st.session_state.df_barang["Nama Barang"] == pilihan_barang].index[0]
        st.session_state.df_barang.at[idx, "Total Keluar"] += jumlah_keluar
        st.success(f"Berhasil mencatat penjualan {jumlah_keluar} Slop untuk {pilihan_barang}!")
        st.rerun()

elif fitur == "⚙️ Kelola Master Barang":
    st.title("⚙️ Kelola Master Barang Baru")
    with st.form("form_barang_baru"):
        kode = st.text_input("Kode Barang:", value=f"BRG00{len(df)+1}")
        nama = st.text_input("Nama Barang:")
        kategori = st.selectbox("Kategori:", ["Rokok Filter", "Rokok Kretek", "Rokok Putih", "Lainnya"])
        harga_beli = st.number_input("Harga Beli Modal (per Slop):", min_value=0, step=1000)
        harga_jual = st.number_input("Harga Jual (per Slop):", min_value=0, step=1000)
        stok_awal = st.number_input("Stok Awal:", min_value=0, step=1)
        satuan = st.text_input("Satuan:", value="Slop")
        
        submitted = st.form_submit_button("Tambah Barang")
        if submitted:
            baris_baru = {
                "Kode": kode, "Nama Barang": nama, "Kategori": kategori, 
                "Harga Beli": harga_beli, "Harga Jual": harga_jual, 
                "Stok Awal": stok_awal, "Total Restok": 0, "Total Keluar": 0, "Satuan": satuan
            }
            st.session_state.df_barang = pd.concat([st.session_state.df_barang, pd.DataFrame([baris_baru])], ignore_index=True)
            st.success(f"Barang {nama} berhasil ditambahkan!")
            st.rerun()

elif fitur == "🧹 Hapus/Edit Riwayat & Reset":
    st.title("🧹 Reset / Clear Data")
    st.warning("Gunakan fitur ini jika ingin mengosongkan/mereset angka penjualan.")
    if st.button("Reset Transaksi Penjualan & Restok"):
        st.session_state.df_barang["Total Restok"] = 0
        st.session_state.df_barang["Total Keluar"] = 0
        st.success("Semua angka penjualan & restok berhasil di-reset!")
        st.rerun()
