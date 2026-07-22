import streamlit as st
import pandas as pd

# Page config
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
        "🛠️ Edit / Hapus Barang & Reset"
    ]
)

# ---------------------------------------------------------
# 4. HALAMAN DASHBOARD & LAPORAN
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
    
    tabel_tampil = df[[
        "Kode", "Nama Barang", "Kategori", "Harga Beli", "Harga Jual", 
        "Stok Awal", "Total Restok", "Total Keluar", "Sisa Stok", 
        "Total Omset", "Total HPP (Modal)", "Laba Kotor Total", "Satuan"
    ]]
    
    st.dataframe(tabel_tampil, use_container_width=True)
    
    csv_data = tabel_tampil.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Unduh Laporan Stok & Keuangan (CSV / Excel)",
        data=csv_data,
        file_name='Laporan_Pembukuan_Rokok.csv',
        mime='text/csv',
    )

elif fitur == "➕ Restok (Barang Masuk)":
    st.title("➕ Input Restok Barang Masuk")
    if len(df) > 0:
        pilihan_barang = st.selectbox("Pilih Barang:", df["Nama Barang"].tolist())
        jumlah_masuk = st.number_input("Jumlah Masuk (Slop):", min_value=1, step=1)
        
        if st.button("Simpan Restok"):
            idx = st.session_state.df_barang[st.session_state.df_barang["Nama Barang"] == pilihan_barang].index[0]
            st.session_state.df_barang.at[idx, "Total Restok"] += jumlah_masuk
            st.success(f"Berhasil menambahkan restok {jumlah_masuk} Slop untuk {pilihan_barang}!")
            st.rerun()
    else:
        st.warning("Belum ada data barang.")

elif fitur == "🛒 Penjualan (Barang Keluar)":
    st.title("🛒 Input Penjualan Barang Keluar")
    if len(df) > 0:
        pilihan_barang = st.selectbox("Pilih Barang:", df["Nama Barang"].tolist())
        jumlah_keluar = st.number_input("Jumlah Keluar / Terjual (Slop):", min_value=1, step=1)
        
        if st.button("Simpan Penjualan"):
            idx = st.session_state.df_barang[st.session_state.df_barang["Nama Barang"] == pilihan_barang].index[0]
            st.session_state.df_barang.at[idx, "Total Keluar"] += jumlah_keluar
            st.success(f"Berhasil mencatat penjualan {jumlah_keluar} Slop untuk {pilihan_barang}!")
            st.rerun()
    else:
        st.warning("Belum ada data barang.")

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

# ---------------------------------------------------------
# 5. FITUR EDIT, HAPUS & RESET
# ---------------------------------------------------------
elif fitur == "🛠️ Edit / Hapus Barang & Reset":
    st.title("🛠️ Pengelolaan Data Barang & Reset")
    
    tab1, tab2, tab3 = st.tabs(["✏️ Edit Data Barang", "🗑️ Hapus Barang", "🧹 Reset Transaksi"])
    
    # --- TAB 1: EDIT BARANG ---
    with tab1:
        st.subheader("✏️ Edit Detail & Harga Barang")
        if len(df) > 0:
            pilih_edit = st.selectbox("Pilih Barang yang Ingin Di-edit:", df["Nama Barang"].tolist(), key="select_edit")
            idx = st.session_state.df_barang[st.session_state.df_barang["Nama Barang"] == pilih_edit].index[0]
            row = st.session_state.df_barang.loc[idx]
            
            with st.form("form_edit_barang"):
                edit_nama = st.text_input("Nama Barang:", value=row["Nama Barang"])
                edit_kat = st.selectbox("Kategori:", ["Rokok Filter", "Rokok Kretek", "Rokok Putih", "Lainnya"], index=["Rokok Filter", "Rokok Kretek", "Rokok Putih", "Lainnya"].index(row["Kategori"]) if row["Kategori"] in ["Rokok Filter", "Rokok Kretek", "Rokok Putih", "Lainnya"] else 0)
                edit_hb = st.number_input("Harga Beli (Modal):", min_value=0, value=int(row["Harga Beli"]), step=1000)
                edit_hj = st.number_input("Harga Jual:", min_value=0, value=int(row["Harga Jual"]), step=1000)
                edit_sa = st.number_input("Stok Awal:", min_value=0, value=int(row["Stok Awal"]), step=1)
                
                simpan_edit = st.form_submit_button("Simpan Perubahan")
                if simpan_edit:
                    st.session_state.df_barang.at[idx, "Nama Barang"] = edit_nama
                    st.session_state.df_barang.at[idx, "Kategori"] = edit_kat
                    st.session_state.df_barang.at[idx, "Harga Beli"] = edit_hb
                    st.session_state.df_barang.at[idx, "Harga Jual"] = edit_hj
                    st.session_state.df_barang.at[idx, "Stok Awal"] = edit_sa
                    st.success(f"Data barang {edit_nama} berhasil diperbarui!")
                    st.rerun()
        else:
            st.info("Tidak ada data barang untuk di-edit.")
            
    # --- TAB 2: HAPUS BARANG ---
    with tab2:
        st.subheader("🗑️ Hapus Barang dari Sistem")
        if len(df) > 0:
            pilih_hapus = st.selectbox("Pilih Barang yang Ingin Dihapus:", df["Nama Barang"].tolist(), key="select_hapus")
            if st.button("❌ Hapus Barang Ini", type="primary"):
                st.session_state.df_barang = st.session_state.df_barang[st.session_state.df_barang["Nama Barang"] != pilih_hapus].reset_index(drop=True)
                st.success(f"Barang {pilih_hapus} telah berhasil dihapus!")
                st.rerun()
        else:
            st.info("Tidak ada data barang untuk dihapus.")
            
    # --- TAB 3: RESET TRANSAKSI ---
    with tab3:
        st.subheader("🧹 Reset Angka Transaksi")
        st.warning("Fitur ini akan mengosongkan angka Restok dan Penjualan menjadi 0 tanpa menghapus daftar barangnya.")
        if st.button("Reset Semua Transaksi Penjualan & Restok"):
            st.session_state.df_barang["Total Restok"] = 0
            st.session_state.df_barang["Total Keluar"] = 0
            st.success("Semua angka penjualan & restok berhasil di-reset ke 0!")
            st.rerun()
