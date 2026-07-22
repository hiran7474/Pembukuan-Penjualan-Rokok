import streamlit as st
import pandas as pd

# ---------------------------------------------------------
# 1. INISIALISASI DATABASE & DATA DUMMY
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

# Pembagian Keuangan (Bagi Hasil 50%)
pengembalian_modal = total_modal_hpp
setoran_pemilik_modal = pengembalian_modal + (total_laba_kotor * 0.50)
bagian_pengelola = total_laba_kotor * 0.50

# ---------------------------------------------------------
# 3. SIDEBAR MENU
# ---------------------------------------------------------
st.sidebar.title("📦 Menu Pembukuan Rokok")

fitur = st.sidebar.radio(
    "Pilih Fitur:",
    ["📊 Dashboard & Laporan", "➕ Restok (Barang Masuk)", "🛒 Penjualan (Barang Keluar)", "🆕 Tambah Barang Baru"]
)

# ---------------------------------------------------------
# 4. HALAMAN UTAMA / DASHBOARD
# ---------------------------------------------------------
if fitur == "📊 Dashboard & Laporan":
    st.title("📋 Laporan Realtime Stok & Keuangan Toko Rokok")
    st.caption("Sistem Pembukuan Otomatis & Skema Bagi Hasil 50%")
    
    # KARTU STOK METRICS
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Jenis Barang", f"{total_jenis}")
    col2.metric("Total Restok Masuk", f"{total_restok} Slop")
    col3.metric("Total Barang Keluar", f"{total_keluar} Slop")
    col4.metric("Stok Menipis (<=10)", f"{stok_menipis}")
    
    st.markdown("---")
    
    # KARTU KEUANGAN METRICS
    st.subheader("💰 Ringkasan Kas & Bagi Hasil (50:50)")
    f1, f2, f3, f4 = st.columns(4)
    f1.metric("💵 Total Omset / Cash", f"Rp {total_cash_omset:,.0f}")
    f2.metric("📦 Modal Terjual (HPP)", f"Rp {total_modal_hpp:,.0f}")
    f3.metric("👑 Setoran Pemilik Modal", f"Rp {setoran_pemilik_modal:,.0f}", delta="Modal + 50% Profit")
    f4.metric("👨‍💼 Bagian Pengelola", f"Rp {bagian_pengelola:,.0f}", delta="50% Profit")
    
    st.markdown("---")
    
    # TABEL LAPORAN REALTIME
    st.subheader("📝 Laporan Realtime Stok & Profit per Barang")
    
    tabel_tampil = df[[
        "Kode", "Nama Barang", "Kategori", "Harga Beli", "Harga Jual", 
        "Stok Awal", "Total Restok", "Total Keluar", "Sisa Stok", 
        "Total Omset", "Total HPP (Modal)", "Laba Kotor Total", "Satuan"
    ]]
    
    st.dataframe(tabel_tampil, use_container_width=True)
    
    # 📥 FITUR TOMBOL DOWNLOAD FILE CSV / EXCEL
    st.write("### 📥 Unduh Laporan")
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

elif fitur == "🆕 Tambah Barang Baru":
    st.title("🆕 Tambah Master Barang Baru")
    with st.form("form_barang_baru"):
        kode = st.text_input("Kode Barang:", value=f"BRG00{len(df)+1}")
        nama = st.text_input("Nama Barang (Contoh: Magnum Filter):")
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
