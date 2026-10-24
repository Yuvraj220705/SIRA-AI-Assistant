import streamlit as st
import os
import pandas as pd
import time
import bcrypt

# ─────────────────────────────────────────────────────────────────────────────
# IMPORTANT NOTE ON STORAGE
# Users are stored in a local CSV file. This is intentional for simplicity and
# zero-cost hosting, but has two key limitations:
#   1. Passwords are bcrypt-hashed (secure), but the file itself is NOT
#      suitable for high-security production use.
#   2. On Streamlit Community Cloud (free tier) the filesystem is ephemeral —
#      user accounts created after deployment will be lost on container restart.
# For a persistent, production-grade solution, migrate to a free-tier database
# such as Supabase (PostgreSQL) or MongoDB Atlas.
# ─────────────────────────────────────────────────────────────────────────────

USERS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "users.csv")
COLUMNS = ["username", "email", "gender", "password_hash"]

if not os.path.exists(USERS_FILE):
    pd.DataFrame(columns=COLUMNS).to_csv(USERS_FILE, index=False)

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False


def _hash_password(plain: str) -> str:
    """Return a bcrypt hash of the given password."""
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def _verify_password(plain: str, hashed: str) -> bool:
    """Return True if plain matches the stored bcrypt hash."""
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False


def load_user() -> pd.DataFrame:
    """Load users CSV, creating it with correct columns if absent or empty."""
    if not os.path.exists(USERS_FILE):
        return pd.DataFrame(columns=COLUMNS)
    try:
        df = pd.read_csv(USERS_FILE)
        # Back-compat: old rows may have a plain 'password' column
        if "password" in df.columns and "password_hash" not in df.columns:
            df = df.rename(columns={"password": "password_hash"})
        return df
    except Exception:
        return pd.DataFrame(columns=COLUMNS)


def save_user(username: str, email: str, gender: str, password_hash: str) -> None:
    """Append a new user row to the CSV."""
    users = load_user()
    new_row = pd.DataFrame(
        [[username, email, gender, password_hash]], columns=COLUMNS
    )
    users = pd.concat([users, new_row], ignore_index=True)
    users.to_csv(USERS_FILE, index=False)


def signup_page():
    # ── Styling ───────────────────────────────────────────────────────────────
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
        
        * {
            font-family: 'Poppins', sans-serif;
        }
        
        /* Background */
        .stApp {
            background: linear-gradient(135deg, #0f2027 0%, #203a43 25%, #2c5364 50%, #1a365d 75%, #0f172a 100%) !important;
            background-size: 400% 400%;
            animation: gradientShift 15s ease infinite;
        }
        
        /* FIX ALL WHITE SPACES */
        [data-testid="stAppViewContainer"] {
            background: transparent !important;
        }
        
        [data-testid="stHeader"] {
            background: linear-gradient(135deg, #0f2027 0%, #203a43 100%) !important;
        }
        
        [data-testid="stToolbar"] {
            background: linear-gradient(135deg, #0f2027 0%, #203a43 100%) !important;
        }
        
        [data-testid="collapsedControl"] {
            background: linear-gradient(135deg, #0f2027 0%, #203a43 100%) !important;
        }
        
        [data-testid="stDecoration"] {
            background: linear-gradient(135deg, #0f2027 0%, #203a43 100%) !important;
        }
        
        .main .block-container {
            background: transparent !important;
        }
        
        .main > div:first-child {
            background: transparent !important;
            padding-top: 10px;
        }
        
        .main > div:last-child {
            background: transparent !important;
            padding-bottom: 10px;
        }
        
        [data-testid="stVerticalBlock"] {
            background: transparent !important;
        }
        
        [data-testid="stVerticalBlockBorderWrapper"] {
            background: transparent !important;
        }
        
        [data-testid="stHorizontalBlock"] {
            background: transparent !important;
        }
        
        @keyframes gradientShift {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        
        /* Form container */
        .signup-container {
            max-width: 500px;
            margin: 0 auto;
            padding: 40px;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 30px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
            animation: fadeInUp 0.8s ease-out;
        }
        
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        /* Header animation */
        .signup-header {
            text-align: center;
            margin-bottom: 30px;
            animation: fadeInDown 0.8s ease-out;
        }
        
        @keyframes fadeInDown {
            from {
                opacity: 0;
                transform: translateY(-30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .signup-header h1 {
            color: white;
            font-size: 36px;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
        }
        
        .signup-header p {
            color: rgba(255, 255, 255, 0.9);
            font-size: 16px;
        }
        
        /* Input fields */
        .stTextInput > div > div > input,
        .stSelectbox > div > div > select {
            background: rgba(255, 255, 255, 0.2) !important;
            border: 2px solid rgba(255, 255, 255, 0.3) !important;
            border-radius: 15px !important;
            color: black !important;
            padding: 12px 20px !important;
            font-size: 16px !important;
            transition: all 0.3s ease !important;
        }
        
        .stTextInput > div > div > input:focus,
        .stSelectbox > div > div > select:focus {
            border-color: rgba(255, 255, 255, 0.6) !important;
            box-shadow: 0 0 20px rgba(255, 255, 255, 0.3) !important;
            background: rgba(255, 255, 255, 0.25) !important;
        }
        
        .stTextInput > div > div > input::placeholder {
            color: rgb(49, 51, 63) !important;
        }
        
        /* Labels */
        .stTextInput > label,
        .stSelectbox > label {
            color: white !important;
            font-weight: 600 !important;
            font-size: 14px !important;
            margin-bottom: 8px !important;
        }
        
        /* Submit button */
        .stButton > button {
            width: 100%;
            height: 55px;
            font-size: 18px;
            font-weight: 600;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 20px;
            box-shadow: 0 4px 15px 0 rgba(116, 79, 168, 0.5);
            transition: all 0.3s ease;
            margin-top: 20px;
        }
        
        .stButton > button:hover {
            transform: translateY(-3px);
            box-shadow: 0 6px 20px 0 rgba(116, 79, 168, 0.7);
            background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
        }
        
        /* Success/Error messages */
        .stAlert {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            animation: slideIn 0.5s ease-out;
        }
        
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateX(-20px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }
        
        /* Back to home link */
        .back-link {
            text-align: center;
            margin-top: 20px;
            color: white;
            font-size: 14px;
        }
        
        .back-link a {
            color: rgba(255, 255, 255, 0.9);
            text-decoration: none;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        
        .back-link a:hover {
            color: white;
            text-shadow: 0 0 10px rgba(255, 255, 255, 0.8);
        }
        
        /* Icon animation */
        @keyframes bounce {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-10px); }
        }
        
        .icon-bounce {
            display: inline-block;
            animation: bounce 2s ease-in-out infinite;
        }
        </style>
    """, unsafe_allow_html=True)

    # Center the form
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("""
            <div class="signup-header">
                <div class="icon-bounce">✨</div>
                <h1>Create Account</h1>
                <p>Join Ruby AI and start your journey</p>
            </div>
        """, unsafe_allow_html=True)

        with st.form("reg-form"):
            username = st.text_input("👤 Username", placeholder="Enter your username")
            email = st.text_input("📧 Email", placeholder="your.email@example.com")
            gender = st.selectbox("⚧ Gender", ["Male", "Female", "Other"])
            password = st.text_input("🔒 Password", type="password", placeholder="Enter a secure password")

            signup_btn = st.form_submit_button("🚀 Create Account")

            if signup_btn:
                if not username or not email or not password:
                    st.error("⚠️ Please fill all required fields")
                    return

                users = load_user()

                if username in users["username"].astype(str).values:
                    st.error("❌ Username already exists!")
                else:
                    hashed = _hash_password(password)
                    save_user(username, email, gender, hashed)
                    st.session_state.gender = gender
                    st.success("✅ Registered successfully! Redirecting to login...")
                    time.sleep(2)
                    st.session_state.page = "Login"
                    st.rerun()

        # Back to home link
        st.markdown("""
            <div class="back-link">
                Already have an account? 
            </div>
        """, unsafe_allow_html=True)

        if st.button("← Back to Login", use_container_width=True):
            st.session_state.page = "Login"
            st.rerun()