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
SERVICE_URL = "https://image-thabat-652749443637.europe-west1.run.app"  # Ensure this is correct and accessible!

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
        /* Customize your CSS styles */
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
    try:
        # Open the image and send it to the API
        with open(image_path, "rb") as image_file:
            files = {"file": image_file}
            response = requests.post(SERVICE_URL, files=files)

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
            st.markdown('<p style="color:#eeeeef;">❌ Failed to get prediction from API. Status code: {}</p>'.format(response.status_code), unsafe_allow_html=True)
            return None, 0  # Return a default value when the API fails
    except Exception as e:
        st.markdown(f'<p style="color:#eeeeef;">❌ An error occurred: {str(e)}</p>', unsafe_allow_html=True)
        return None, 0  # Return a default value in case of an error


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
        logo_path = os.path.join(os.path.dirname(__file__), "logo.jpg")
        logo = Image.open(logo_path)
        st.image(logo, width=1000)
        st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""Your introduction text here...""", unsafe_allow_html=True)

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
