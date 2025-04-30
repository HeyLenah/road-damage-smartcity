import streamlit as st
from PIL import Image
import tempfile
import os
import json
import pickle
import requests
from glob import glob
import base64
import io

# File paths for persistence
USER_DB_FILE = "users.json"
HISTORY_FILE = "history.pkl"

# API URL
API_URL = "http://127.0.0.1:8000/predict"  # Replace with your real API server!

# Load and Save functions
def load_user_db():
    if os.path.exists(USER_DB_FILE):
        with open(USER_DB_FILE, "r") as f:
            return json.load(f)
    return {}

def save_user_db(db):
    with open(USER_DB_FILE, "w") as f:
        json.dump(db, f)

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "rb") as f:
            return pickle.load(f)
    return {}

def save_history(history):
    with open(HISTORY_FILE, "wb") as f:
        pickle.dump(history, f)

# Setup
st.set_page_config(page_title="Thabat", layout="centered")
st.markdown("""
    <style>
        /* Page background */
        .stApp {
            background-color: #1A1A1A;
        }

        /* Sidebar and header */
        section[data-testid="stSidebar"] {
            background-color: #1A1A1A !important;
        }

        .block-container {
            background-color: #1A1A1A;
        }

        /* Input fields */
        input, textarea {
            background-color: #1A1A1A !important;
            color: #EEEEEF !important;
            border: 1px solid #ccc !important;
            border-radius: 6px;
        }

        /* File uploader - Dark background and text color fix */
        div[data-testid="stFileUploader"] {
            background-color: #2b2b2b !important;  /* Dark background for file upload */
            border: 1px solid #ccc !important;
            border-radius: 8px !important;
            padding: 10px !important;
            color: #EEEEEF !important;  /* White text */
        }
        div[data-testid="stFileUploader"] label {
            color: #EEEEEF !important;  /* White text for the label */
        }

        div[data-testid="stFileUploader"] .css-1v3fvcr {
            color: #EEEEEF !important;  /* Ensures text inside the file uploader is white */
        }

        /* Buttons */
        button {
            background-color: #1A1A1A !important;
            color: #EEEEEF !important;
            border: 1px solid #ccc !important;
            border-radius: 8px !important;
            padding: 10px 20px !important;
            font-weight: 500 !important;
            transition: 0.3s ease-in-out;
        }
        button:hover {
            background-color: #E0E0E0 !important;
            color: #111 !important;
        }

        /* Tabs */
        div[data-baseweb="tab-list"] {
            background-color: #1A1A1A !important;
        }

        div[data-baseweb="tab"] {
            background-color: #1A1A1A !important;
            color: #EEEEEF !important;
            border-bottom: 2px solid transparent;
            padding: 8px 16px;
            font-weight: normal;
        }

        div[data-baseweb="tab"]:hover {
            background-color: #E0E0E0 !important;
        }

        div[data-baseweb="tab"][aria-selected="true"] {
            background-color: #1A1A1A !important;
            border-bottom: 3px solid #999 !important;
            font-weight: bold !important;
            color: #EEEEEF !important;
        }

        /* Alert boxes */
        .stAlert {
            background-color: #E9E7E3 !important;
            color: #EEEEEF !important;
        }

        /* Text and labels */
        h1, h2, h3, h4, h5, p, span, label {
            color: #EEEEEF !important;
        }
        label {
            font-weight: bold !important;
        }
    </style>
""", unsafe_allow_html=True)



# Initialize state with persistent data
if "user_db" not in st.session_state:
    st.session_state.user_db = load_user_db()

if "history" not in st.session_state:
    st.session_state.history = load_history()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

if "page" not in st.session_state:
    st.session_state.page = "Home"

def send_image_to_api(image_path):
    with open(image_path, "rb") as image_file:
        files = {"file": image_file}
        response = requests.post(API_URL, files=files)

    if response.status_code == 200:
        response_json = response.json()
        pothole_detected = response_json.get("pothole_detected", False)
        num_potholes = response_json.get("num_potholes", 0)
        img_str = response_json.get("image", None)

    # If an image is returned, display it
    if img_str:
        image = Image.open(io.BytesIO(base64.b64decode(img_str)))
        st.image(image, use_container_width=True)

        st.markdown('<p style="color:#eeeeef;">Processed Image with Potholes Detected</p>', unsafe_allow_html=True)

        return pothole_detected, num_potholes
    else:
        st.markdown('<p style="color:#eeeeef;">❌ Failed to get prediction from API.</p>', unsafe_allow_html=True)
        return None


# Page selector
page = st.sidebar.selectbox("Select a Page", ["Home", "Demo", "History"], index=["Home", "Demo", "History"].index(st.session_state.page))

# Log out button
if st.session_state.logged_in:
    if st.sidebar.button("Log Out"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.page = "Home"
        st.rerun()

# Home/Login/Register Page
if page == "Home":
    # Make left column wider
    col1, col2, col3 = st.columns([5, 1, 1])  # col1 is now the widest

    with col1:
        st.image("logo.jpg", width=1000)
        st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
<div dir="rtl" style="text-align: right; font-size: 18px; line-height: 1.6;">
    <strong>خطوتك نحو طرق أكثر أمانًا</strong><br><br>
    في <strong>ثَبات</strong>، نستخدم الذكاء الاصطناعي للكشف المبكر عن الحفر، لصناعة طرق أكثر أمانًا واستقرارًا، دعمًا لمستقبل مدن ذكية مستدامة ضمن <strong>رؤية المملكة العربية السعودية 2030</strong>.<br><br>
    استكشف كيف تساهم التقنية في بناء مدن أكثر ذكاءً
</div>

---

**Your First Step Toward Safer Roads**

At **Thabat**, we leverage artificial intelligence to detect road potholes early, helping build safer and more stable roads while supporting the vision of sustainable smart cities as part of **Saudi Vision 2030**.

Discover how technology shapes smarter cities.

---
""", unsafe_allow_html=True)


    tab1, tab2 = st.tabs(["Login", "Create account"])

    with tab1:
        login_username = st.text_input("Username", key="login_user")
        login_password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login"):
            user = st.session_state.user_db.get(login_username)
            if user and user["password"] == login_password:
                st.success(f"Welcome back, {login_username}!")
                st.session_state.logged_in = True
                st.session_state.username = login_username
                st.session_state.page = "Demo"
                st.rerun()
            else:
                st.markdown('<p style="color:#1a1a1a;"> Invalid credentials.</p>', unsafe_allow_html=True)


    with tab2:
        signup_username = st.text_input("New Username", key="signup_user")
        signup_password = st.text_input("New Password", type="password", key="signup_pass")
        if st.button("Sign Up"):
            if signup_username in st.session_state.user_db:
                st.warning("Username already exists.")
            else:
                st.session_state.user_db[signup_username] = {"password": signup_password}
                save_user_db(st.session_state.user_db)
                st.success("Account created! Logging you in...")
                st.session_state.logged_in = True
                st.session_state.username = signup_username
                st.session_state.page = "Demo"
                st.rerun()
                    # Separator
    st.markdown("<hr>", unsafe_allow_html=True)
    # Contact Section
    st.markdown("### Connect With Us")

    team_members = {
        "Lenah Alrifai": "http://www.linkedin.com/in/lenah-alrifai",
        "Nawaf Alfuhaid": "https://www.linkedin.com/in/nawaf-alfuhaid/",
        "Deema Alluhayb": "https://www.linkedin.com/in/deema-alluhayb1/",
        "Abeer Al-Shahrani": "https://www.linkedin.com/in/abeer-al-shahrani-2210782b3/?utm_source=share&utm_campaign=share_via&utm_content=profile&utm_medium=ios_app",
        "Ghada Alzanbagi": "https://www.linkedin.com/in/ghada-alzanbagi-0b30542b4/"
    }

    linkedin_icon = "https://cdn-icons-png.flaticon.com/512/174/174857.png"
    icon_size = 20  # icon size in pixels


    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            f"""
            <div style="margin-bottom: 10px;">
                <a href="{team_members['Lenah Alrifai']}" target="_blank" style="text-decoration: none;">
                    <img src="{linkedin_icon}" width="{icon_size}" style="vertical-align: middle; margin-right: 8px;" />
                    <span style="font-size: 16px; vertical-align: middle;">Lenah Alrifai</span>
                </a>
            </div>
            <div style="margin-bottom: 10px;">
                <a href="{team_members['Nawaf Alfuhaid']}" target="_blank" style="text-decoration: none;">
                    <img src="{linkedin_icon}" width="{icon_size}" style="vertical-align: middle; margin-right: 8px;" />
                    <span style="font-size: 16px; vertical-align: middle;">Nawaf Alfuhaid</span>
                </a>
            </div>
        """,
        unsafe_allow_html=True)

    with col2:
        st.markdown(
            f"""
            <div style="margin-bottom: 10px;">
                <a href="{team_members['Deema Alluhayb']}" target="_blank" style="text-decoration: none;">
                    <img src="{linkedin_icon}" width="{icon_size}" style="vertical-align: middle; margin-right: 8px;" />
                    <span style="font-size: 16px; vertical-align: middle;">Deema Alluhayb</span>
                </a>
            </div>
            <div style="margin-bottom: 10px;">
                <a href="{team_members['Abeer Al-Shahrani']}" target="_blank" style="text-decoration: none;">
                    <img src="{linkedin_icon}" width="{icon_size}" style="vertical-align: middle; margin-right: 8px;" />
                    <span style="font-size: 16px; vertical-align: middle;">Abeer Al-Shahrani</span>
                </a>
            </div>
        """,
        unsafe_allow_html=True)

    with col3:
        st.markdown(
            f"""
            <div style="margin-bottom: 10px;">
                <a href="{team_members['Ghada Alzanbagi']}" target="_blank" style="text-decoration: none;">
                    <img src="{linkedin_icon}" width="{icon_size}" style="vertical-align: middle; margin-right: 8px;" />
                    <span style="font-size: 16px; vertical-align: middle;">Ghada Alzanbagi</span>
                </a>
            </div>
        """,
        unsafe_allow_html=True)


# Demo Page
elif page == "Demo":
    if not st.session_state.logged_in:
        st.markdown('<p style="color:#1a1a1a;"> 🔒Please log in to access this page.</p>', unsafe_allow_html=True)
    else:
        st.title("🕳️ Thabat Demo")


        # File uploader and demo page
        # Custom label
        # Add custom style to fix uploader background

        # Add custom style to fix uploader background
        # Custom CSS for file uploader style fix
        # Fix file uploader background and frame + make text visible
        st.markdown("""
        <style>
            .stFileUploader {
                background-color: #1A1A1A;
                color: white;
                border-radius: 10px;
                padding: 20px;
            }
            .stFileUploader input[type="file"] {
                color: white;
            }
        </style>
    """, unsafe_allow_html=True)

        # File uploader without label
        uploaded_file = st.file_uploader(label="", type=["jpg", "jpeg", "png"])
        if uploaded_file is not None:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
                temp_file.write(uploaded_file.getvalue())
                temp_img_path = temp_file.name


            with st.spinner("Sending image to server for analysis..."):
                pothole_found, num_potholes = send_image_to_api(temp_img_path)
                if pothole_found is not None:
                    if pothole_found:
                        st.markdown('<div style="background-color: #d3d3d3; color: red; padding: 10px; border-radius: 5px;">⚠️ Warning: Pothole Detected ❗</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div style="background-color: #d3d3d3; color: green; padding: 10px; border-radius: 5px;">✅ No potholes detected in Demo {idx+1} </div>', unsafe_allow_html=True)

                    # Save to history
                    st.session_state.history.setdefault(st.session_state.username, []).append({
                        "source": "Uploaded Image",
                        "potholes": pothole_found,
                        "image": temp_img_path
                    })
                    save_history(st.session_state.history)

        st.subheader("Or analyze a demo image:")

        demo_images_dir = "demo imgs"
        demo_image_paths = sorted(glob(os.path.join(demo_images_dir, "*.jpg")))

        cols = st.columns(5)
        for idx, path in enumerate(demo_image_paths[:10]):
            with cols[idx % 5]:
                if st.button(f"Analyze Demo {idx+1}"):
                    with st.spinner(f"Sending Demo {idx+1} to server..."):
                        pothole_found, num_potholes = send_image_to_api(path)
                        if pothole_found is not None:
                            if pothole_found:
                                st.markdown(f'<div style="background-color: #d3d3d3; color: red; padding: 10px; border-radius: 5px;">⚠️ Warning: Pothole Detected in Demo {idx+1}❗</div>', unsafe_allow_html=True)
                            else:
                                st.markdown(f'<div style="background-color: #d3d3d3; color: green; padding: 10px; border-radius: 5px;">✅ No potholes detected in Demo {idx+1} </div>', unsafe_allow_html=True)


                            # Save to history
                            st.session_state.history.setdefault(st.session_state.username, []).append({
                                "source": f"Demo Image {idx+1}",
                                "potholes": pothole_found,
                                "image": path
                            })
                            save_history(st.session_state.history)

# History Page
elif page == "History":
    if not st.session_state.logged_in:
        st.markdown('<p style="color:#1a1a1a;"> 🔒 Please log in to view your history.</p>', unsafe_allow_html=True)
    else:
        st.title("📜 Detection History")

        user_history = st.session_state.history.get(st.session_state.username, [])

        if user_history:
            for i, entry in enumerate(user_history[::-1]):
                st.markdown("---")
                st.subheader(entry['source'])

                if 'image' in entry:
                    st.image(entry['image'], caption=entry['source'], width=300)

                if entry['potholes']:
                    st.markdown('<p style="color:#1a1a1a;"> A Pothole Found🕳️!</p>', unsafe_allow_html=True)
                else:
                    st.markdown('<p style="color:#1a1a1a;"> ✅ No potholes detected.</p>', unsafe_allow_html=True)
        else:
            st.info("No detection history yet.")
