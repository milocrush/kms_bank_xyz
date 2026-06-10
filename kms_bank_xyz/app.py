import hashlib
import os
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

try:
    import plotly.express as px
except Exception:
    px = None

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = BASE_DIR / "uploads"
KNOWLEDGE_FILE = DATA_DIR / "knowledge_base.csv"
USERS_FILE = DATA_DIR / "users.csv"
UPLOAD_DIR.mkdir(exist_ok=True)

st.set_page_config(
    page_title="KMS Bank XYZ",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

CUSTOM_CSS = """
<style>
    .main-title {font-size: 2rem; font-weight: 800; margin-bottom: .2rem;}
    .subtitle {color: #64748b; margin-bottom: 1.2rem;}
    .kms-card {padding: 1rem; border-radius: 14px; border: 1px solid #e2e8f0; background: #ffffff; margin-bottom: .75rem;}
    .small-muted {color: #64748b; font-size: .9rem;}
    .metric-box {padding: 1rem; border-radius: 12px; background: #f8fafc; border: 1px solid #e2e8f0;}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def load_users() -> pd.DataFrame:
    if not USERS_FILE.exists():
        return pd.DataFrame(columns=["username", "password_hash", "nama", "role", "unit", "keahlian", "kontak"])
    return pd.read_csv(USERS_FILE).fillna("")


def load_knowledge() -> pd.DataFrame:
    if not KNOWLEDGE_FILE.exists():
        return pd.DataFrame(columns=[
            "knowledge_id", "timestamp", "username", "kategori", "judul", "masalah", "solusi", "file_path", "status"
        ])
    return pd.read_csv(KNOWLEDGE_FILE).fillna("")


def save_knowledge(df: pd.DataFrame) -> None:
    df.to_csv(KNOWLEDGE_FILE, index=False)


def next_knowledge_id(df: pd.DataFrame) -> str:
    if df.empty:
        return "KMS-001"
    nums = []
    for value in df["knowledge_id"].astype(str):
        try:
            nums.append(int(value.split("-")[-1]))
        except Exception:
            pass
    return f"KMS-{(max(nums) + 1 if nums else 1):03d}"


def authenticate(username: str, password: str):
    users = load_users()
    if users.empty:
        return None
    match = users[(users["username"] == username) & (users["password_hash"] == hash_password(password))]
    if match.empty:
        return None
    return match.iloc[0].to_dict()


def require_login():
    if "user" not in st.session_state:
        st.session_state.user = None

    if st.session_state.user:
        return st.session_state.user

    left, mid, right = st.columns([1, 1.2, 1])
    with mid:
        st.markdown('<div class="main-title">KMS Bank XYZ</div>', unsafe_allow_html=True)
        st.markdown('<div class="subtitle">Knowledge Management System berbasis SECI untuk mendukung transfer pengetahuan.</div>', unsafe_allow_html=True)
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="admin")
            password = st.text_input("Password", type="password", placeholder="admin123")
            submitted = st.form_submit_button("Masuk", use_container_width=True)
        st.info("Demo login: admin / admin123")
        if submitted:
            user = authenticate(username.strip(), password.strip())
            if user:
                st.session_state.user = user
                st.rerun()
            else:
                st.error("Username atau password salah!")
    st.stop()


def sidebar(user):
    st.sidebar.markdown(f"### Halo, {user['nama']}")
    st.sidebar.caption(f"{user['role']} • {user['unit']}")
    menu = st.sidebar.radio(
        "Menu",
        [
            "Dashboard Pengetahuan",
            "Cari Solusi",
            "Input Pengetahuan",
            "Direktori Ahli",
            "Kelola Konten",
            "Tentang Sistem",
        ],
    )
    st.sidebar.divider()
    if st.sidebar.button("Keluar", use_container_width=True):
        st.session_state.user = None
        st.rerun()
    return menu


def page_dashboard():
    st.markdown('<div class="main-title">Dashboard Pengetahuan</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Mode SECI: Combination. Data pengetahuan dikombinasikan menjadi informasi statistik untuk manajemen.</div>', unsafe_allow_html=True)
    df = load_knowledge()
    approved = df[df["status"].str.lower() == "approved"] if not df.empty else df

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Pengetahuan", len(df))
    c2.metric("Konten Approved", len(approved))
    c3.metric("Kategori", approved["kategori"].nunique() if not approved.empty else 0)
    c4.metric("Kontributor", approved["username"].nunique() if not approved.empty else 0)

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Distribusi Kategori")
        if approved.empty:
            st.warning("Belum ada data.")
        else:
            category_count = approved.groupby("kategori").size().reset_index(name="jumlah")
            if px:
                fig = px.pie(category_count, names="kategori", values="jumlah", hole=0.35)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.bar_chart(category_count.set_index("kategori"))
    with col2:
        st.subheader("Kontribusi per Pegawai")
        if approved.empty:
            st.warning("Belum ada data.")
        else:
            author_count = approved.groupby("username").size().reset_index(name="jumlah").sort_values("jumlah", ascending=False)
            if px:
                fig = px.bar(author_count, x="username", y="jumlah", text="jumlah")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.bar_chart(author_count.set_index("username"))

    st.subheader("Data Pengetahuan Terbaru")
    st.dataframe(approved.sort_values("timestamp", ascending=False), use_container_width=True, hide_index=True)


def page_search():
    st.markdown('<div class="main-title">Cari Solusi</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Mode SECI: Internalization. Pegawai belajar mandiri dari pengetahuan eksplisit yang tersimpan.</div>', unsafe_allow_html=True)
    df = load_knowledge()
    df = df[df["status"].str.lower() == "approved"] if not df.empty else df

    col1, col2 = st.columns([2, 1])
    keyword = col1.text_input("Kata kunci", placeholder="Contoh: kredit macet, KYC, selisih kas")
    categories = ["Semua"] + sorted(df["kategori"].dropna().unique().tolist()) if not df.empty else ["Semua"]
    category = col2.selectbox("Kategori", categories)

    result = df.copy()
    if category != "Semua":
        result = result[result["kategori"] == category]
    if keyword:
        key = keyword.lower()
        mask = (
            result["judul"].str.lower().str.contains(key, na=False)
            | result["masalah"].str.lower().str.contains(key, na=False)
            | result["solusi"].str.lower().str.contains(key, na=False)
            | result["kategori"].str.lower().str.contains(key, na=False)
        )
        result = result[mask]

    st.caption(f"Ditemukan {len(result)} hasil.")
    if result.empty:
        st.warning("Data tidak ditemukan. Coba gunakan kata kunci lain.")
        return

    for _, row in result.sort_values("timestamp", ascending=False).iterrows():
        with st.expander(f"{row['judul']} — {row['kategori']}"):
            st.markdown(f"**ID:** {row['knowledge_id']}")
            st.markdown(f"**Masalah:** {row['masalah']}")
            st.markdown(f"**Solusi:** {row['solusi']}")
            st.caption(f"Ditulis oleh {row['username']} pada {row['timestamp']}")
            if row.get("file_path") and os.path.exists(row["file_path"]):
                with open(row["file_path"], "rb") as file:
                    st.download_button("Unduh Lampiran", file, file_name=os.path.basename(row["file_path"]))


def page_input(user):
    st.markdown('<div class="main-title">Input Pengetahuan</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Mode SECI: Externalization. Pengalaman tacit pegawai dikodifikasi menjadi pengetahuan eksplisit.</div>', unsafe_allow_html=True)
    with st.form("knowledge_form", clear_on_submit=True):
        kategori = st.selectbox("Kategori", ["Kredit", "Operasional", "Compliance", "Layanan", "HR", "Teknologi Informasi"])
        judul = st.text_input("Judul Pengetahuan")
        masalah = st.text_area("Deskripsi Masalah", height=130)
        solusi = st.text_area("Solusi / Langkah Penyelesaian", height=160)
        upload = st.file_uploader("Lampiran Pendukung", type=["pdf", "docx", "xlsx", "png", "jpg", "jpeg"])
        submitted = st.form_submit_button("Simpan Pengetahuan", use_container_width=True)

    if submitted:
        if not judul.strip() or not masalah.strip() or not solusi.strip():
            st.warning("Mohon lengkapi judul, masalah, dan solusi.")
            return
        df = load_knowledge()
        knowledge_id = next_knowledge_id(df)
        file_path = ""
        if upload:
            safe_name = f"{knowledge_id}_{upload.name}".replace(" ", "_")
            file_path = str(UPLOAD_DIR / safe_name)
            with open(file_path, "wb") as f:
                f.write(upload.getbuffer())
        status = "Approved" if user["role"] == "Admin" else "Pending"
        new_row = {
            "knowledge_id": knowledge_id,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "username": user["username"],
            "kategori": kategori,
            "judul": judul.strip(),
            "masalah": masalah.strip(),
            "solusi": solusi.strip(),
            "file_path": file_path,
            "status": status,
        }
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        save_knowledge(df)
        if status == "Pending":
            st.success("Pengetahuan berhasil dikirim dan menunggu validasi Knowledge Manager.")
        else:
            st.success("Pengetahuan berhasil disimpan.")


def page_experts():
    st.markdown('<div class="main-title">Direktori Ahli</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Mode SECI: Socialization. Pegawai dapat menemukan mentor atau Subject Matter Expert yang relevan.</div>', unsafe_allow_html=True)
    users = load_users()
    experts = users[users["role"].isin(["Knowledge Manager", "Knowledge Worker", "Admin"])]
    keyword = st.text_input("Cari ahli berdasarkan nama, unit, atau keahlian")
    if keyword:
        key = keyword.lower()
        experts = experts[
            experts["nama"].str.lower().str.contains(key, na=False)
            | experts["unit"].str.lower().str.contains(key, na=False)
            | experts["keahlian"].str.lower().str.contains(key, na=False)
        ]
    for _, row in experts.iterrows():
        st.markdown(
            f"""
            <div class="kms-card">
                <h4>{row['nama']}</h4>
                <div class="small-muted">{row['role']} • {row['unit']}</div>
                <p><b>Keahlian:</b> {row['keahlian']}</p>
                <p><b>Kontak:</b> {row['kontak']}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


def page_manage(user):
    st.markdown('<div class="main-title">Kelola Konten</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Validasi konten untuk menjaga kualitas basis pengetahuan.</div>', unsafe_allow_html=True)
    if user["role"] not in ["Admin", "Knowledge Manager"]:
        st.error("Menu ini hanya dapat diakses oleh Admin atau Knowledge Manager.")
        return
    df = load_knowledge()
    if df.empty:
        st.info("Belum ada konten.")
        return

    st.dataframe(df.sort_values("timestamp", ascending=False), use_container_width=True, hide_index=True)
    selected = st.selectbox("Pilih ID konten", df["knowledge_id"].tolist())
    action = st.radio("Aksi", ["Approve", "Reject", "Delete"], horizontal=True)
    if st.button("Proses", use_container_width=True):
        if action == "Delete":
            df = df[df["knowledge_id"] != selected]
            save_knowledge(df)
            st.success("Konten berhasil dihapus.")
        else:
            df.loc[df["knowledge_id"] == selected, "status"] = "Approved" if action == "Approve" else "Rejected"
            save_knowledge(df)
            st.success(f"Status konten berhasil diubah menjadi {action}.")
        st.rerun()


def page_about():
    st.markdown('<div class="main-title">Tentang Sistem</div>', unsafe_allow_html=True)
    st.write(
        """
        Prototipe ini dibuat untuk mendukung tesis Magister Sistem Informasi dengan topik
        Strategi Pengembangan Sistem Manajemen Pengetahuan untuk Mendukung Transfer Pengetahuan pada PT. Bank XYZ.

        Pemetaan fitur terhadap model SECI:
        - Socialization: Direktori Ahli.
        - Externalization: Input Pengetahuan.
        - Combination: Dashboard Pengetahuan.
        - Internalization: Cari Solusi.

        Teknologi yang digunakan: Python, Streamlit, Pandas, Plotly, dan penyimpanan CSV sebagai prototipe awal.
        """
    )


def main():
    user = require_login()
    menu = sidebar(user)
    if menu == "Dashboard Pengetahuan":
        page_dashboard()
    elif menu == "Cari Solusi":
        page_search()
    elif menu == "Input Pengetahuan":
        page_input(user)
    elif menu == "Direktori Ahli":
        page_experts()
    elif menu == "Kelola Konten":
        page_manage(user)
    elif menu == "Tentang Sistem":
        page_about()


if __name__ == "__main__":
    main()
