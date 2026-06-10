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

DATA_DIR.mkdir(exist_ok=True)
UPLOAD_DIR.mkdir(exist_ok=True)

st.set_page_config(
    page_title="KMS PT. Bank XYZ",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #111827 40%, #1e293b 100%);
        color: #f8fafc;
    }

    section[data-testid="stSidebar"] {
        background: rgba(15, 23, 42, 0.96);
        border-right: 1px solid rgba(148, 163, 184, 0.18);
    }

    section[data-testid="stSidebar"] * {
        color: #e5e7eb;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1500px;
    }

    .hero-card {
        padding: 1.8rem 2rem;
        border-radius: 28px;
        background: linear-gradient(135deg, rgba(37, 99, 235, .20), rgba(14, 165, 233, .10));
        border: 1px solid rgba(148, 163, 184, .22);
        box-shadow: 0 24px 80px rgba(0, 0, 0, .25);
        margin-bottom: 1.2rem;
    }

    .hero-kicker {
        color: #93c5fd;
        font-size: .82rem;
        font-weight: 700;
        letter-spacing: .12em;
        text-transform: uppercase;
        margin-bottom: .35rem;
    }

    .hero-title {
        font-size: 2.25rem;
        line-height: 1.15;
        font-weight: 850;
        color: #ffffff;
        margin-bottom: .5rem;
    }

    .hero-subtitle {
        max-width: 980px;
        color: #cbd5e1;
        font-size: 1rem;
        line-height: 1.7;
    }

    .section-title {
        font-size: 1.45rem;
        font-weight: 800;
        color: #ffffff;
        margin: 1rem 0 .25rem 0;
    }

    .section-subtitle {
        color: #94a3b8;
        font-size: .95rem;
        line-height: 1.65;
        margin-bottom: 1rem;
    }

    .glass-card {
        padding: 1.1rem 1.2rem;
        border-radius: 22px;
        background: rgba(15, 23, 42, .72);
        border: 1px solid rgba(148, 163, 184, .18);
        box-shadow: 0 18px 50px rgba(0, 0, 0, .20);
        margin-bottom: 1rem;
    }

    .metric-card {
        padding: 1.15rem 1.15rem;
        border-radius: 22px;
        background: linear-gradient(135deg, rgba(30, 41, 59, .95), rgba(15, 23, 42, .92));
        border: 1px solid rgba(148, 163, 184, .18);
        min-height: 130px;
        box-shadow: 0 16px 45px rgba(0, 0, 0, .20);
    }

    .metric-label {
        color: #94a3b8;
        font-size: .86rem;
        font-weight: 600;
        margin-bottom: .35rem;
    }

    .metric-value {
        color: #ffffff;
        font-size: 2.15rem;
        font-weight: 850;
        line-height: 1;
        margin-bottom: .4rem;
    }

    .metric-note {
        color: #64748b;
        font-size: .82rem;
    }

    .seci-badge {
        display: inline-block;
        padding: .32rem .7rem;
        border-radius: 999px;
        background: rgba(59, 130, 246, .18);
        color: #93c5fd;
        border: 1px solid rgba(147, 197, 253, .24);
        font-size: .78rem;
        font-weight: 700;
        margin-bottom: .6rem;
    }

    .expert-card, .knowledge-card {
        padding: 1.15rem 1.2rem;
        border-radius: 22px;
        background: rgba(15, 23, 42, .74);
        border: 1px solid rgba(148, 163, 184, .20);
        box-shadow: 0 18px 45px rgba(0, 0, 0, .18);
        margin-bottom: .85rem;
    }

    .card-title {
        font-size: 1.08rem;
        font-weight: 780;
        color: #ffffff;
        margin-bottom: .25rem;
    }

    .muted {
        color: #94a3b8;
        font-size: .9rem;
        line-height: 1.55;
    }

    .pill {
        display: inline-block;
        padding: .28rem .62rem;
        border-radius: 999px;
        background: rgba(14, 165, 233, .12);
        color: #7dd3fc;
        border: 1px solid rgba(125, 211, 252, .20);
        font-size: .78rem;
        font-weight: 700;
        margin-right: .35rem;
    }

    .status-approved {
        background: rgba(34, 197, 94, .12);
        color: #86efac;
        border: 1px solid rgba(134, 239, 172, .22);
    }

    .status-pending {
        background: rgba(245, 158, 11, .12);
        color: #fcd34d;
        border: 1px solid rgba(252, 211, 77, .22);
    }

    div[data-testid="stMetricValue"] {
        color: #ffffff;
    }

    .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] > div {
        border-radius: 14px !important;
        border-color: rgba(148, 163, 184, .25) !important;
    }

    .stButton button, .stDownloadButton button, .stFormSubmitButton button {
        border-radius: 14px !important;
        border: 1px solid rgba(147, 197, 253, .26) !important;
        background: linear-gradient(135deg, #2563eb, #0ea5e9) !important;
        color: #ffffff !important;
        font-weight: 750 !important;
        min-height: 2.8rem;
    }

    .stButton button:hover, .stDownloadButton button:hover, .stFormSubmitButton button:hover {
        border: 1px solid rgba(191, 219, 254, .60) !important;
        filter: brightness(1.08);
    }

    div[data-testid="stDataFrame"] {
        border-radius: 18px;
        overflow: hidden;
        border: 1px solid rgba(148, 163, 184, .18);
    }

    .login-wrap {
        max-width: 560px;
        margin: 7vh auto 0 auto;
        padding: 2rem;
        border-radius: 28px;
        background: rgba(15, 23, 42, .84);
        border: 1px solid rgba(148, 163, 184, .20);
        box-shadow: 0 32px 100px rgba(0, 0, 0, .35);
    }

    .login-logo {
        width: 64px;
        height: 64px;
        border-radius: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(135deg, #2563eb, #0ea5e9);
        font-size: 1.8rem;
        margin-bottom: 1rem;
    }

    .login-title {
        font-size: 1.85rem;
        font-weight: 850;
        color: #ffffff;
        margin-bottom: .35rem;
    }

    .login-subtitle {
        color: #94a3b8;
        line-height: 1.6;
        margin-bottom: 1rem;
    }

    hr {
        border-color: rgba(148, 163, 184, .18) !important;
    }

    #MainMenu, footer, header {visibility: hidden;}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def ensure_demo_data() -> None:
    if not USERS_FILE.exists():
        demo_hash = hash_password("admin123")
        users = pd.DataFrame([
            ["admin", demo_hash, "Admin", "Admin", "Teknologi Informasi", "Knowledge Management dan Sistem Informasi", "admin@bankxyz.local"],
            ["budi.santoso", demo_hash, "Budi Santoso", "Knowledge Manager", "Operasional", "SOP Operasional, Manajemen Risiko, dan Knowledge Governance", "budi@bankxyz.local"],
            ["siti.aminah", demo_hash, "Siti Aminah", "Knowledge Worker", "Kredit", "Analisis Kredit, Agunan, dan Penanganan Kredit Bermasalah", "siti@bankxyz.local"],
            ["rizky.pratama", demo_hash, "Rizky Pratama", "Knowledge Worker", "Layanan", "Layanan Nasabah, Frontliner, dan Operasional Cabang", "rizky@bankxyz.local"],
        ], columns=["username", "password_hash", "nama", "role", "unit", "keahlian", "kontak"])
        users.to_csv(USERS_FILE, index=False)

    if not KNOWLEDGE_FILE.exists():
        rows = [
            ["KMS-001", "2025-09-12 09:10:00", "siti.aminah", "Kredit", "Validasi Agunan Tanah Girik", "Pegawai junior sering belum memahami dokumen pendukung yang dibutuhkan saat nasabah mengajukan kredit dengan agunan tanah girik.", "Lakukan verifikasi surat tanah, riwayat kepemilikan, surat keterangan kelurahan, bukti pembayaran PBB, serta validasi lapangan sebelum proses analisis kredit dilanjutkan.", "", "Approved"],
            ["KMS-002", "2025-09-13 10:20:00", "budi.santoso", "Operasional", "Penanganan Selisih Kas Harian", "Teller menemukan selisih kas pada akhir hari dan belum mengetahui langkah eskalasi yang sesuai.", "Lakukan rekonsiliasi transaksi, cocokkan jurnal teller, periksa bukti fisik, laporkan ke supervisor, lalu dokumentasikan kronologi pada sistem internal.", "", "Approved"],
            ["KMS-003", "2025-09-14 14:00:00", "rizky.pratama", "Layanan", "Penanganan Nasabah Komplain Kartu ATM", "Nasabah datang ke cabang karena kartu ATM tertelan dan meminta penyelesaian cepat.", "Verifikasi identitas nasabah, cek status kartu, lakukan pemblokiran jika diperlukan, arahkan penggantian kartu sesuai SOP, dan catat tiket layanan.", "", "Approved"],
            ["KMS-004", "2025-09-15 11:15:00", "siti.aminah", "Compliance", "Validasi Dokumen KYC Nasabah Baru", "Dokumen calon nasabah belum lengkap dan berpotensi menimbulkan risiko kepatuhan.", "Pastikan identitas, alamat, pekerjaan, sumber dana, dan profil risiko telah lengkap. Jika ada data meragukan, lakukan enhanced due diligence sebelum pembukaan rekening.", "", "Approved"],
        ]
        df = pd.DataFrame(rows, columns=["knowledge_id", "timestamp", "username", "kategori", "judul", "masalah", "solusi", "file_path", "status"])
        df.to_csv(KNOWLEDGE_FILE, index=False)


def load_users() -> pd.DataFrame:
    ensure_demo_data()
    if not USERS_FILE.exists():
        return pd.DataFrame(columns=["username", "password_hash", "nama", "role", "unit", "keahlian", "kontak"])
    return pd.read_csv(USERS_FILE).fillna("")


def load_knowledge() -> pd.DataFrame:
    ensure_demo_data()
    if not KNOWLEDGE_FILE.exists():
        return pd.DataFrame(columns=[
            "knowledge_id", "timestamp", "username", "kategori", "judul", "masalah", "solusi", "file_path", "status"
        ])
    df = pd.read_csv(KNOWLEDGE_FILE).fillna("")
    for col in ["knowledge_id", "timestamp", "username", "kategori", "judul", "masalah", "solusi", "file_path", "status"]:
        if col not in df.columns:
            df[col] = ""
    return df


def save_knowledge(df: pd.DataFrame) -> None:
    df.to_csv(KNOWLEDGE_FILE, index=False)


def next_knowledge_id(df: pd.DataFrame) -> str:
    if df.empty or "knowledge_id" not in df.columns:
        return "KMS-001"
    nums = []
    for value in df["knowledge_id"].astype(str):
        try:
            nums.append(int(value.split("-")[-1]))
        except Exception:
            pass
    return f"KMS-{(max(nums) + 1 if nums else 1):03d}"


def authenticate(username: str, password: str):
    username = username.strip()
    password = password.strip()

    # Login demo langsung agar prototipe tesis mudah diuji.
    if username == "admin" and password == "admin123":
        return {
            "username": "admin",
            "password_hash": "",
            "nama": "Admin",
            "role": "Admin",
            "unit": "Teknologi Informasi",
            "keahlian": "Knowledge Management dan Sistem Informasi",
            "kontak": "admin@bankxyz.local",
        }

    users = load_users()
    if users.empty:
        return None

    match = users[
        (users["username"].astype(str).str.strip() == username) &
        (users["password_hash"].astype(str).str.strip() == hash_password(password))
    ]
    if match.empty:
        return None
    return match.iloc[0].to_dict()


def render_hero(kicker: str, title: str, subtitle: str) -> None:
    st.markdown(
        f"""
        <div class="hero-card">
            <div class="hero-kicker">{kicker}</div>
            <div class="hero-title">{title}</div>
            <div class="hero-subtitle">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metric(label: str, value, note: str = "") -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def require_login():
    if "user" not in st.session_state:
        st.session_state.user = None

    if st.session_state.user:
        return st.session_state.user

    _, mid, _ = st.columns([1, 1.05, 1])
    with mid:
        st.markdown(
            """
            <div class="login-wrap">
                <div class="login-logo">📚</div>
                <div class="login-title">KMS PT. Bank XYZ</div>
                <div class="login-subtitle">
                    Sistem Manajemen Pengetahuan berbasis model SECI untuk mendukung transfer pengetahuan,
                    retensi aset intelektual, dan pembelajaran mandiri pegawai.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        with st.form("login_form"):
            username = st.text_input("Username", value="admin")
            password = st.text_input("Password", type="password", value="")
            submitted = st.form_submit_button("Masuk ke Sistem", use_container_width=True)
        st.info("Demo login: admin / admin123")
        if submitted:
            user = authenticate(username, password)
            if user:
                st.session_state.user = user
                st.rerun()
            else:
                st.error("Username atau password salah!")
    st.stop()


def sidebar(user):
    st.sidebar.markdown("## 📚 KMS Bank XYZ")
    st.sidebar.caption("Knowledge Management System")
    st.sidebar.divider()
    st.sidebar.markdown(f"### Halo, {user['nama']}")
    st.sidebar.caption(f"{user['role']} • {user['unit']}")
    st.sidebar.divider()

    menu = st.sidebar.radio(
        "Navigasi Model SECI",
        [
            "1. Socialization - Direktori Ahli",
            "2. Externalization - Input Pengetahuan",
            "3. Combination - Dashboard Pengetahuan",
            "4. Internalization - Cari Solusi",
            "5. Kelola Konten",
            "6. Tentang Sistem",
        ],
    )
    st.sidebar.divider()
    st.sidebar.caption("Prototype for Master Thesis")
    if st.sidebar.button("Keluar", use_container_width=True):
        st.session_state.user = None
        st.rerun()
    return menu


def page_dashboard():
    render_hero(
        "SECI MODE 03 • COMBINATION",
        "Implementasi Combination melalui Dashboard Pengetahuan",
        "Data pengetahuan eksplisit yang telah tersimpan digabungkan, dikelompokkan, dan divisualisasikan menjadi informasi statistik agar manajemen dapat memantau kontribusi pengetahuan, kategori masalah, serta aktivitas berbagi pengetahuan dalam organisasi.",
    )

    df = load_knowledge()
    approved = df[df["status"].astype(str).str.lower() == "approved"] if not df.empty else df

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_metric("Total Pengetahuan", len(df), "Semua konten dalam repositori")
    with c2:
        render_metric("Konten Approved", len(approved), "Konten tervalidasi")
    with c3:
        render_metric("Kategori Aktif", approved["kategori"].nunique() if not approved.empty else 0, "Unit/topik pengetahuan")
    with c4:
        render_metric("Kontributor", approved["username"].nunique() if not approved.empty else 0, "Pegawai yang berbagi")

    st.markdown('<div class="section-title">Visualisasi Basis Pengetahuan</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Dashboard ini memperlihatkan proses kombinasi data menjadi informasi yang mudah dianalisis oleh Knowledge Manager.</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("Distribusi Kategori")
        if approved.empty:
            st.warning("Belum ada data approved.")
        else:
            category_count = approved.groupby("kategori").size().reset_index(name="jumlah")
            if px:
                fig = px.pie(category_count, names="kategori", values="jumlah", hole=0.48)
                fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font_color="#e5e7eb",
                    legend_title_text="Kategori",
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.bar_chart(category_count.set_index("kategori"))
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("Kontribusi per Pegawai")
        if approved.empty:
            st.warning("Belum ada data approved.")
        else:
            author_count = approved.groupby("username").size().reset_index(name="jumlah").sort_values("jumlah", ascending=False)
            if px:
                fig = px.bar(author_count, x="username", y="jumlah", text="jumlah")
                fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font_color="#e5e7eb",
                    xaxis_title="Kontributor",
                    yaxis_title="Jumlah Konten",
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.bar_chart(author_count.set_index("username"))
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title">Data Pengetahuan Terbaru</div>', unsafe_allow_html=True)
    if approved.empty:
        st.info("Belum ada data pengetahuan yang disetujui.")
    else:
        display_cols = ["knowledge_id", "timestamp", "kategori", "judul", "username", "status"]
        st.dataframe(approved.sort_values("timestamp", ascending=False)[display_cols], use_container_width=True, hide_index=True)


def page_search():
    render_hero(
        "SECI MODE 04 • INTERNALIZATION",
        "Implementasi Internalization melalui Pencarian Solusi",
        "Pegawai dapat mempelajari pengetahuan eksplisit yang tersimpan di repositori melalui fitur pencarian. Pengetahuan yang dibaca, dipahami, dan diterapkan dalam pekerjaan harian akan berubah menjadi kompetensi tacit baru pada individu.",
    )

    df = load_knowledge()
    df = df[df["status"].astype(str).str.lower() == "approved"] if not df.empty else df

    col1, col2 = st.columns([2.2, 1])
    keyword = col1.text_input("Kata kunci pencarian", placeholder="Contoh: kredit macet, KYC, selisih kas, kartu ATM")
    categories = ["Semua"] + sorted(df["kategori"].dropna().unique().tolist()) if not df.empty else ["Semua"]
    category = col2.selectbox("Kategori", categories)

    result = df.copy()
    if category != "Semua":
        result = result[result["kategori"] == category]
    if keyword:
        key = keyword.lower().strip()
        mask = (
            result["judul"].astype(str).str.lower().str.contains(key, na=False)
            | result["masalah"].astype(str).str.lower().str.contains(key, na=False)
            | result["solusi"].astype(str).str.lower().str.contains(key, na=False)
            | result["kategori"].astype(str).str.lower().str.contains(key, na=False)
        )
        result = result[mask]

    st.markdown(f'<span class="pill">{len(result)} hasil ditemukan</span>', unsafe_allow_html=True)
    st.write("")

    if result.empty:
        st.warning("Data tidak ditemukan. Coba gunakan kata kunci lain atau pilih kategori Semua.")
        return

    for _, row in result.sort_values("timestamp", ascending=False).iterrows():
        st.markdown(
            f"""
            <div class="knowledge-card">
                <span class="pill">{row['kategori']}</span>
                <span class="pill status-approved">{row['status']}</span>
                <div class="card-title" style="margin-top:.8rem;">{row['judul']}</div>
                <div class="muted">ID {row['knowledge_id']} • Ditulis oleh {row['username']} • {row['timestamp']}</div>
                <hr>
                <p><b>Deskripsi Masalah</b><br>{row['masalah']}</p>
                <p><b>Solusi / Langkah Penyelesaian</b><br>{row['solusi']}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if row.get("file_path") and os.path.exists(row["file_path"]):
            with open(row["file_path"], "rb") as file:
                st.download_button("Unduh Lampiran", file, file_name=os.path.basename(row["file_path"]), key=f"download_{row['knowledge_id']}")


def page_input(user):
    render_hero(
        "SECI MODE 02 • EXTERNALIZATION",
        "Implementasi Externalization melalui Input Pengetahuan",
        "Fitur ini memfasilitasi pegawai untuk mengubah pengalaman tacit, best practice, dan solusi kasus operasional menjadi pengetahuan eksplisit yang terdokumentasi secara terstruktur dalam repositori organisasi.",
    )

    with st.form("knowledge_form", clear_on_submit=True):
        st.markdown('<div class="section-title">Formulir Dokumentasi Pengetahuan</div>', unsafe_allow_html=True)
        col1, col2 = st.columns([1, 1])
        with col1:
            kategori = st.selectbox("Kategori", ["Kredit", "Operasional", "Compliance", "Layanan", "HR", "Teknologi Informasi"])
            judul = st.text_input("Judul Pengetahuan", placeholder="Contoh: Penanganan selisih kas harian")
        with col2:
            upload = st.file_uploader("Lampiran Pendukung", type=["pdf", "docx", "xlsx", "png", "jpg", "jpeg"])
            st.caption("Lampiran bersifat opsional untuk mendukung validasi pengetahuan.")
        masalah = st.text_area("Deskripsi Masalah", height=140, placeholder="Jelaskan konteks masalah, kondisi, dan dampaknya terhadap pekerjaan.")
        solusi = st.text_area("Solusi / Langkah Penyelesaian", height=170, placeholder="Tuliskan langkah penyelesaian yang dapat dipelajari dan digunakan ulang oleh pegawai lain.")
        submitted = st.form_submit_button("Simpan Pengetahuan", use_container_width=True)

    if submitted:
        if not judul.strip() or not masalah.strip() or not solusi.strip():
            st.warning("Mohon lengkapi judul, deskripsi masalah, dan solusi.")
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
            st.success("Pengetahuan berhasil disimpan dan langsung berstatus Approved.")


def page_experts():
    render_hero(
        "SECI MODE 01 • SOCIALIZATION",
        "Implementasi Socialization melalui Direktori Ahli",
        "Fitur Direktori Ahli berfungsi sebagai Expert Locator yang mempertemukan pegawai pencari pengetahuan dengan Subject Matter Expert. Mekanisme ini mendukung berbagi pengalaman tacit melalui mentoring, diskusi, dan konsultasi langsung.",
    )

    users = load_users()
    experts = users[users["role"].isin(["Knowledge Manager", "Knowledge Worker", "Admin"])]
    keyword = st.text_input("Cari ahli berdasarkan nama, unit, atau keahlian", placeholder="Contoh: kredit, operasional, compliance")
    if keyword:
        key = keyword.lower().strip()
        experts = experts[
            experts["nama"].astype(str).str.lower().str.contains(key, na=False)
            | experts["unit"].astype(str).str.lower().str.contains(key, na=False)
            | experts["keahlian"].astype(str).str.lower().str.contains(key, na=False)
        ]

    cols = st.columns(2)
    for idx, (_, row) in enumerate(experts.iterrows()):
        with cols[idx % 2]:
            st.markdown(
                f"""
                <div class="expert-card">
                    <span class="pill">{row['role']}</span>
                    <div class="card-title" style="margin-top:.8rem;">{row['nama']}</div>
                    <div class="muted">Unit: {row['unit']}</div>
                    <hr>
                    <p><b>Bidang Keahlian</b><br>{row['keahlian']}</p>
                    <p><b>Kontak</b><br>{row['kontak']}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )


def page_manage(user):
    render_hero(
        "KNOWLEDGE GOVERNANCE",
        "Validasi dan Pengelolaan Konten Pengetahuan",
        "Menu ini digunakan oleh Admin atau Knowledge Manager untuk menjaga kualitas basis pengetahuan melalui proses approval, rejection, dan penghapusan konten yang tidak relevan.",
    )

    if user["role"] not in ["Admin", "Knowledge Manager"]:
        st.error("Menu ini hanya dapat diakses oleh Admin atau Knowledge Manager.")
        return

    df = load_knowledge()
    if df.empty:
        st.info("Belum ada konten.")
        return

    display_cols = ["knowledge_id", "timestamp", "username", "kategori", "judul", "status"]
    st.dataframe(df.sort_values("timestamp", ascending=False)[display_cols], use_container_width=True, hide_index=True)

    col1, col2 = st.columns([1, 1])
    with col1:
        selected = st.selectbox("Pilih ID konten", df["knowledge_id"].tolist())
    with col2:
        action = st.radio("Aksi", ["Approve", "Reject", "Delete"], horizontal=True)

    if st.button("Proses Konten", use_container_width=True):
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
    render_hero(
        "MASTER THESIS PROTOTYPE",
        "Tentang Sistem Manajemen Pengetahuan PT. Bank XYZ",
        "Prototipe ini dikembangkan sebagai artefak penelitian Magister Sistem Informasi dengan pendekatan Design Science Research dan pengembangan cepat berbasis Python Streamlit.",
    )

    st.markdown('<div class="section-title">Pemetaan Fitur terhadap Model SECI</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="glass-card">
            <p><span class="seci-badge">Socialization</span><br>Direktori Ahli untuk menemukan mentor atau Subject Matter Expert.</p>
            <p><span class="seci-badge">Externalization</span><br>Input Pengetahuan untuk mendokumentasikan pengalaman tacit menjadi pengetahuan eksplisit.</p>
            <p><span class="seci-badge">Combination</span><br>Dashboard Pengetahuan untuk menggabungkan data menjadi informasi statistik.</p>
            <p><span class="seci-badge">Internalization</span><br>Cari Solusi untuk mendukung pembelajaran mandiri pegawai.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="section-title">Teknologi Pengembangan</div>', unsafe_allow_html=True)
    st.write("Python, Streamlit, Pandas, Plotly, CSV flat-file database, dan mekanisme autentikasi sederhana untuk prototipe awal.")


def main():
    user = require_login()
    menu = sidebar(user)

    if menu.startswith("1."):
        page_experts()
    elif menu.startswith("2."):
        page_input(user)
    elif menu.startswith("3."):
        page_dashboard()
    elif menu.startswith("4."):
        page_search()
    elif menu.startswith("5."):
        page_manage(user)
    elif menu.startswith("6."):
        page_about()


if __name__ == "__main__":
    main()
