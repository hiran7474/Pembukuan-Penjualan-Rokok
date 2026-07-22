import streamlit as st
import pandas as pd
from datetime import datetime

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Pencatatan Stok & Bagi Hasil Toko",
    page_icon="📦",
    layout="wide"
)

# --- INITIALIZE DATABASE (SESSION STATE) ---
if "stok_df" not in st.session_state:
    st.session_state.stok_df = pd.DataFrame([
        {"Kode": "BRG001", "Nama Barang": "Kopi Arabika 250g", "Kategori": "Bahan Baku", "Stok Awal": 50, "Satuan": "Pcs", "Harga Beli": 35000, "Harga Jual": 50000},
        {"Kode": "BRG002", "Nama Barang": "Susu UHT 1L", "Kategori": "Bahan Baku", "Stok Awal": 30, "Satuan": "Karton", "Harga Beli": 18000, "Harga Jual": 24000},
        {"Kode": "BRG003", "Nama Barang": "Sirup Vanilla 700ml", "Kategori": "Bahan Baku", "Stok Awal": 15, "Satuan": "Botol", "Harga Beli": 85000, "Harga Jual": 110000},
        {"Kode": "BRG004", "Nama Barang": "Paper Cup 12oz", "Kategori": "Kemasan", "Stok Awal": 200, "Satuan": "Pcs", "Harga Beli": 500, "Harga Jual": 1000},
    ])

if "restok_df" not in st.session_state:
    st.session_state.restok_df = pd.DataFrame([
        {"Tanggal": "2026-07-01", "Kode": "BRG001", "Jumlah Restok": 20, "Keterangan": "Supplier A"},
        {"Tanggal": "2026-07-02", "Kode": "BRG002", "Jumlah Restok": 15, "Keterangan": "Supplier B"},
    ])

if "keluar_df" not in st.session_state:
    st.session_state.keluar_df = pd.DataFrame([
        {"Tanggal": "2026-07-03", "Kode": "BRG001", "Jumlah Keluar": 12, "Keterangan": "Penjualan Harian"},
        {"Tanggal": "2026-07-03", "Kode": "BRG002", "Jumlah Keluar": 10, "Keterangan": "Penjualan Harian"},
    ])

# --- RUMUS OTOMATIS HITUNG STOK & FINANSIAL ---
def get_dashboard_data():
    df_stok = st.session_state.stok_df.copy()
    
    restok_sum = st.session_state.restok_df.groupby("Kode")["Jumlah Restok"].sum().reset_index() if not st.session_state.restok_df.empty else pd.DataFrame(columns=["Kode", "Jumlah Restok"])
    keluar_sum = st.session_state.keluar_df.groupby("Kode")["Jumlah Keluar"].sum().reset_index() if not st.session_state.keluar_df.empty else pd.DataFrame(columns=["Kode", "Jumlah Keluar"])
        
    df_merged = pd.merge(df_stok, restok_sum, on="Kode", how="left").fillna({"Jumlah Restok": 0})
    df_merged = pd.merge(df_merged, keluar_sum, on="Kode", how="left").fillna({"Jumlah Keluar": 0})
    
    df_merged["Total Restok"] = df_merged["Jumlah Restok"].astype(int)
    df_merged["Total Keluar"] = df_merged["Jumlah Keluar"].astype(int)
    df_merged["Sisa Stok"] = (df_merged["Stok Awal"] + df_merged["Total Restok"]) - df_merged["Total Keluar"]
    
    # Hitung finansial barang keluar (penjualan terrealisasi)
    df_merged["Modal Terjual (HPP)"] = df_merged["Total Keluar"] * df_merged["Harga Beli"]
    df_merged["Omset Penjualan"] = df_merged["Total Keluar"] * df_merged["Harga Jual"]
    df_merged["Laba Kotor Terjual"] = df_merged["Omset Penjualan"] - df_merged["Modal Terjual (HPP)"]
    
    # Hitung nilai sisa stok di gudang
    df_merged["Total Nilai Beli"] = df_merged["Sisa Stok"] * df_merged["Harga Beli"]
    df_merged["Total Nilai Jual"] = df_merged["Sisa Stok"] * df_merged["Harga Jual"]
    
    return df_merged

# --- NAVIGATION SIDEBAR ---
st.sidebar.title("📦 Menu Utama")
menu = st.sidebar.radio(
    "Pilih Fitur:",
    [
        "📊 Dashboard & Laporan Setoran", 
        "➕ Restok (Barang Masuk)", 
        "➖ Penjualan (Barang Keluar)", 
        "⚙️ Kelola Master Barang",
        "🧹 Hapus/Edit Riwayat & Reset"
    ]
)

# --- MENU 1: DASHBOARD ---
if menu == "📊 Dashboard & Laporan Setoran":
    st.title("📊 Laporan Realtime Penjualan & Setoran Bagi Hasil (50:50)")
    df_dashboard = get_dashboard_data()
    
    # Summary Keuangan Penjualan Terrealisasi
    total_omset = df_dashboard["Omset Penjualan"].sum()
    total_hpp_terjual = df_dashboard["Modal Terjual (HPP)"].sum()
    total_laba_kotor = df_dashboard["Laba Kotor Terjual"].sum()
    
    # Pembagian Bagi Hasil
    bagian_laba_pemilik = total_laba_kotor * 0.50
    bagian_laba_pengelola = total_laba_kotor * 0.50
    total_setoran_pemilik = total_hpp_terjual + bagian_laba_pemilik
    
    st.subheader("💰 Ringkasan Uang Penjualan Terkumpul")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Cash Omset Penjualan", f"Rp {total_omset:,.0f}")
    col2.metric("Pengembalian Modal (HPP)", f"Rp {total_hpp_terjual:,.0f}")
    col3.metric("Total Laba Bersih/Kotor", f"Rp {total_laba_kotor:,.0f}")
    
    st.markdown("---")
    st.subheader("🤝 Rincian Pembagian Setoran & Profit (50:50)")
    
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("🏦 SETORAN KE PEMILIK MODAL", f"Rp {total_setoran_pemilik:,.0f}", help="Modal HPP Barang Terjual + 50% Laba")
    col_b.metric("👤 Bagi Hasil Pemilik (50%)", f"Rp {bagian_laba_pemilik:,.0f}")
    col_c.metric("🧑‍💼 Bagi Hasil Pengelola (50%)", f"Rp {bagian_laba_pengelola:,.0f}")
    
    st.info(f"💡 **Penjelasan Kas:** Dari total uang tunai terkumpul (Rp {total_omset:,.0f}), sebesar **Rp {total_setoran_pemilik:,.0f}** disetorkan ke Pemilik Modal (Pengembalian Modal Rp {total_hpp_terjual:,.0f} + 50% Laba Rp {bagian_laba_pemilik:,.0f}). Pengelola mengantongi **Rp {bagian_laba_pengelola:,.0f}**.")
    
    st.markdown("---")
    st.subheader("📋 Laporan Detail Stok & Penjualan Per Produk")
    
    display_df = df_dashboard.copy()
    display_df["Harga Beli"] = display_df["Harga Beli"].apply(lambda x: f"Rp {x:,.0f}")
    display_df["Harga Jual"] = display_df["Harga Jual"].apply(lambda x: f"Rp {x:,.0f}")
    display_df["Omset Penjualan"] = display_df["Omset Penjualan"].apply(lambda x: f"Rp {x:,.0f}")
    display_df["Laba Kotor Terjual"] = display_df["Laba Kotor Terjual"].apply(lambda x: f"Rp {x:,.0f}")
    
    st.dataframe(
        display_df[["Kode", "Nama Barang", "Sisa Stok", "Satuan", "Total Keluar", "Harga Beli", "Harga Jual", "Omset Penjualan", "Laba Kotor Terjual"]], 
        use_container_width=True
    )

# --- MENU 2: RESTOK ---
elif menu == "➕ Restok (Barang Masuk)":
    st.title("➕ Restok / Barang Masuk")
    df_dashboard = get_dashboard_data()
    
    if df_dashboard.empty:
        st.warning("Belum ada barang di database.")
    else:
        with st.form("form_restok", clear_on_submit=True):
            col_a, col_b = st.columns(2)
            pilihan_barang = col_a.selectbox("Pilih Barang", options=df_dashboard["Kode"].tolist(), format_func=lambda x: f"{x} - {df_dashboard[df_dashboard['Kode']==x]['Nama Barang'].values[0]}")
            tgl = col_b.date_input("Tanggal Restok", datetime.now())
            
            col_c, col_d = st.columns(2)
            jumlah = col_c.number_input("Jumlah Restok", min_value=1, value=10)
            ket = col_d.text_input("Keterangan / Supplier", value="Supplier Utama")
            
            if st.form_submit_button("💾 Simpan Restok"):
                new_row = pd.DataFrame([{"Tanggal": str(tgl), "Kode": pilihan_barang, "Jumlah Restok": jumlah, "Keterangan": ket}])
                st.session_state.restok_df = pd.concat([st.session_state.restok_df, new_row], ignore_index=True)
                st.success(f"✅ Berhasil menambah restok {jumlah} unit!")
                st.rerun()

        st.subheader("📜 Riwayat Restok Terakhir")
        st.dataframe(st.session_state.restok_df, use_container_width=True)

# --- MENU 3: BARANG KELUAR ---
elif menu == "➖ Penjualan (Barang Keluar)":
    st.title("➖ Penjualan / Barang Keluar")
    df_dashboard = get_dashboard_data()
    
    if df_dashboard.empty:
        st.warning("Belum ada barang di database!")
    else:
        with st.form("form_keluar", clear_on_submit=True):
            col_a, col_b = st.columns(2)
            pilihan_barang = col_a.selectbox("Pilih Barang", options=df_dashboard["Kode"].tolist(), format_func=lambda x: f"{x} - {df_dashboard[df_dashboard['Kode']==x]['Nama Barang'].values[0]} (Sisa: {df_dashboard[df_dashboard['Kode']==x]['Sisa Stok'].values[0]})")
            tgl = col_b.date_input("Tanggal Keluar", datetime.now())
            
            col_c, col_d = st.columns(2)
            jumlah = col_c.number_input("Jumlah Keluar", min_value=1, value=1)
            ket = col_d.text_input("Keterangan", value="Penjualan Harian")
            
            if st.form_submit_button("💾 Catat Penjualan"):
                sisa_saat_ini = df_dashboard[df_dashboard["Kode"] == pilihan_barang]["Sisa Stok"].values[0]
                if jumlah > sisa_saat_ini:
                    st.error(f"❌ Stok tidak cukup! Sisa stok hanya {sisa_saat_ini}.")
                else:
                    new_row = pd.DataFrame([{"Tanggal": str(tgl), "Kode": pilihan_barang, "Jumlah Keluar": jumlah, "Keterangan": ket}])
                    st.session_state.keluar_df = pd.concat([st.session_state.keluar_df, new_row], ignore_index=True)
                    st.success(f"✅ Berhasil mencatat penjualan {jumlah} unit!")
                    st.rerun()

        st.subheader("📜 Riwayat Keluar Terakhir")
        st.dataframe(st.session_state.keluar_df, use_container_width=True)

# --- MENU 4: MANAJEMEN MASTER BARANG ---
elif menu == "⚙️ Kelola Master Barang":
    st.title("⚙️ Kelola Master Barang & Harga")
    
    tab1, tab2, tab3 = st.tabs(["🆕 Tambah Barang Baru", "✏️ Edit Barang & Harga", "🗑️ Hapus Barang"])
    
    with tab1:
        st.subheader("Tambah Barang Baru + Harga")
        with st.form("form_tambah_barang", clear_on_submit=True):
            col1, col2 = st.columns(2)
            kode = col1.text_input("Kode Barang (Misal: BRG005)").upper().strip()
            nama = col2.text_input("Nama Barang")
            
            col3, col4, col5 = st.columns(3)
            kategori = col3.selectbox("Kategori", ["Bahan Baku", "Kemasan", "Produk Jadi", "Lainnya"])
            stok_awal = col4.number_input("Stok Awal", min_value=0, value=10)
            satuan = col5.text_input("Satuan", value="Pcs")
            
            col6, col7 = st.columns(2)
            harga_beli = col6.number_input("Harga Beli / Modal (Rp)", min_value=0, value=10000, step=500)
            harga_jual = col7.number_input("Harga Jual (Rp)", min_value=0, value=15000, step=500)
            
            if st.form_submit_button("➕ Simpan Barang Baru"):
                if not kode or not nama:
                    st.warning("⚠️ Kode dan Nama Barang tidak boleh kosong!")
                elif kode in st.session_state.stok_df["Kode"].values:
                    st.error("❌ Kode barang sudah digunakan!")
                else:
                    new_item = pd.DataFrame([{
                        "Kode": kode, 
                        "Nama Barang": nama, 
                        "Kategori": kategori, 
                        "Stok Awal": stok_awal, 
                        "Satuan": satuan,
                        "Harga Beli": harga_beli,
                        "Harga Jual": harga_jual
                    }])
                    st.session_state.stok_df = pd.concat([st.session_state.stok_df, new_item], ignore_index=True)
                    st.success(f"✅ Barang '{nama}' ({kode}) berhasil ditambahkan!")
                    st.rerun()

    with tab2:
        st.subheader("Edit Data Barang & Harga")
        if st.session_state.stok_df.empty:
            st.info("Tidak ada barang untuk di-edit.")
        else:
            pilihan_edit = st.selectbox("Pilih Barang yang Ingin Di-edit", options=st.session_state.stok_df["Kode"].tolist(), format_func=lambda x: f"{x} - {st.session_state.stok_df[st.session_state.stok_df['Kode']==x]['Nama Barang'].values[0]}")
            data_lama = st.session_state.stok_df[st.session_state.stok_df["Kode"] == pilihan_edit].iloc[0]
            
            with st.form("form_edit_barang"):
                col_e1, col_e2 = st.columns(2)
                nama_baru = col_e1.text_input("Nama Barang Baru", value=data_lama["Nama Barang"])
                kategori_baru = col_e2.text_input("Kategori Baru", value=data_lama["Kategori"])
                
                col_e3, col_e4 = st.columns(2)
                stok_awal_baru = col_e3.number_input("Stok Awal", min_value=0, value=int(data_lama["Stok Awal"]))
                satuan_baru = col_e4.text_input("Satuan Baru", value=data_lama["Satuan"])
                
                col_e5, col_e6 = st.columns(2)
                harga_beli_baru = col_e5.number_input("Harga Beli (Rp)", min_value=0, value=int(data_lama["Harga Beli"]), step=500)
                harga_jual_baru = col_e6.number_input("Harga Jual (Rp)", min_value=0, value=int(data_lama["Harga Jual"]), step=500)
                
                if st.form_submit_button("💾 Update Data & Harga"):
                    idx = st.session_state.stok_df[st.session_state.stok_df["Kode"] == pilihan_edit].index[0]
                    st.session_state.stok_df.loc[idx, "Nama Barang"] = nama_baru
                    st.session_state.stok_df.loc[idx, "Kategori"] = kategori_baru
                    st.session_state.stok_df.loc[idx, "Stok Awal"] = stok_awal_baru
                    st.session_state.stok_df.loc[idx, "Satuan"] = satuan_baru
                    st.session_state.stok_df.loc[idx, "Harga Beli"] = harga_beli_baru
                    st.session_state.stok_df.loc[idx, "Harga Jual"] = harga_jual_baru
                    
                    st.success(f"✅ Data & Harga barang {pilihan_edit} berhasil di-update!")
                    st.rerun()

    with tab3:
        st.subheader("Hapus Barang dari Sistem")
        if st.session_state.stok_df.empty:
            st.info("Tidak ada barang untuk dihapus.")
        else:
            pilihan_hapus = st.selectbox("Pilih Barang yang Ingin Dihapus", options=st.session_state.stok_df["Kode"].tolist(), format_func=lambda x: f"{x} - {st.session_state.stok_df[st.session_state.stok_df['Kode']==x]['Nama Barang'].values[0]}", key="hapus_select")
            
            if st.button("🗑️ Hapus Barang Ini", type="primary"):
                st.session_state.stok_df = st.session_state.stok_df[st.session_state.stok_df["Kode"] != pilihan_hapus].reset_index(drop=True)
                st.success(f"✅ Barang {pilihan_hapus} berhasil dihapus!")
                st.rerun()

# --- MENU 5: HAPUS RIWAYAT TRANSAKSI & RESET ---
elif menu == "🧹 Hapus/Edit Riwayat & Reset":
    st.title("🧹 Koreksi Transaksi & Reset Data")
    
    t1, t2, t3 = st.tabs(["❌ Hapus Transaksi Penjualan/Keluar", "❌ Hapus Transaksi Restok", "⚠️ Reset Semua Data"])
    
    # 1. HAPUS SALAH CATAT PENJUALAN
    with t1:
        st.subheader("Koreksi / Hapus Transaksi Barang Keluar")
        if st.session_state.keluar_df.empty:
            st.info("Belum ada transaksi penjualan.")
        else:
            st.write("Daftar Transaksi Barang Keluar Saat Ini:")
            st.dataframe(st.session_state.keluar_df, use_container_width=True)
            
            list_options = [f"Row {idx} | {row['Tanggal']} | Kode: {row['Kode']} | Keluar: {row['Jumlah Keluar']} | Ket: {row['Keterangan']}" for idx, row in st.session_state.keluar_df.iterrows()]
            selected_row = st.selectbox("Pilih transaksi yang keliru untuk dihapus:", options=list_options)
            
            if st.button("🗑️ Hapus Transaksi Keluar Ini", type="primary"):
                selected_idx = int(selected_row.split(" | ")[0].replace("Row ", ""))
                st.session_state.keluar_df = st.session_state.keluar_df.drop(selected_idx).reset_index(drop=True)
                st.success("✅ Transaksi berhasil dihapus! Sisa stok otomatis bertambah kembali.")
                st.rerun()
                
    # 2. HAPUS SALAH CATAT RESTOK
    with t2:
        st.subheader("Koreksi / Hapus Transaksi Restok")
        if st.session_state.restok_df.empty:
            st.info("Belum ada transaksi restok.")
        else:
            st.write("Daftar Transaksi Restok Saat Ini:")
            st.dataframe(st.session_state.restok_df, use_container_width=True)
            
            list_options_restok = [f"Row {idx} | {row['Tanggal']} | Kode: {row['Kode']} | Restok: {row['Jumlah Restok']} | Ket: {row['Keterangan']}" for idx, row in st.session_state.restok_df.iterrows()]
            selected_row_restok = st.selectbox("Pilih transaksi restok yang keliru untuk dihapus:", options=list_options_restok)
            
            if st.button("🗑️ Hapus Transaksi Restok Ini", type="primary"):
                selected_idx_r = int(selected_row_restok.split(" | ")[0].replace("Row ", ""))
                st.session_state.restok_df = st.session_state.restok_df.drop(selected_idx_r).reset_index(drop=True)
                st.success("✅ Transaksi restok berhasil dihapus! Sisa stok otomatis berkurang kembali.")
                st.rerun()
                
    # 3. RESET TOTAL
    with t3:
        st.subheader("⚠️ Reset Keseluruhan System")
        st.warning("Fitur ini akan menghapus seluruh data barang, riwayat restok, dan riwayat penjualan!")
        
        confirm = st.checkbox("Saya paham dan yakin ingin mengosongkan/reset seluruh data stok.")
        if confirm:
            if st.button("🚨 RESET SEMUA DATA", type="primary"):
                st.session_state.stok_df = pd.DataFrame(columns=["Kode", "Nama Barang", "Kategori", "Stok Awal", "Satuan", "Harga Beli", "Harga Jual"])
                st.session_state.restok_df = pd.DataFrame(columns=["Tanggal", "Kode", "Jumlah Restok", "Keterangan"])
                st.session_state.keluar_df = pd.DataFrame(columns=["Tanggal", "Kode", "Jumlah Keluar", "Keterangan"])
                st.success("💥 Seluruh data berhasil di-reset!")
                st.rerun()
