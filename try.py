import streamlit as st
import os
import json
from datetime import datetime

USERS_FILE = "users.json"
FILES_FILE = "files.json"

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f)

def load_files():
    if os.path.exists(FILES_FILE):
        with open(FILES_FILE, "r") as f:
            return json.load(f)
    return []

def save_files(files):
    with open(FILES_FILE, "w") as f:
        json.dump(files, f)

def register_user():
    st.title("Employee Database Portal - Register")
    username = st.text_input("Username", key="register_username")
    password = st.text_input("Password", type="password", key="register_password")
    
    if st.button("Register"):
        users = load_users()
        
        if username in users:
            st.warning("Username already exists! Try a different one.")
        else:
            users[username] = {"password": password}
            save_users(users)
            st.success("Registration successful! Please log in.")
            st.session_state['username'] = username
            return True
    return False

def login_user():
    st.title("Employee Database Portal - Login")
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")
    
    if st.button("Login"):
        users = load_users()
        
        if username in users and users[username]["password"] == password:
            st.session_state['username'] = username
            st.success(f"Welcome {username}!")
            return True
        else:
            st.error("Invalid credentials!")
    return False

def upload_files():
    st.title("Upload File(s)")
    uploaded_files = st.file_uploader("Choose files", accept_multiple_files=True)
    
    if uploaded_files:
        current_user = st.session_state.get('username', None)
        if not current_user:
            st.warning("You must be logged in to upload files.")
            return
        
        files = load_files()
        for file in uploaded_files:
            file_metadata = {
                "name": file.name,
                "upload_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "uploaded_by": current_user,
                "downloaded_by": None,
                "download_date": None
            }
            files.append(file_metadata)
            
            with open(f"uploaded_files/{file.name}", "wb") as f:
                f.write(file.getbuffer())
        
        save_files(files)
        st.success("Files uploaded successfully!")

def view_files():
    st.title("My Files")
    current_user = st.session_state.get('username', None)
    if not current_user:
        st.warning("You must be logged in to view files.")
        return
    
    files = load_files()
    user_files = [f for f in files if f["uploaded_by"] == current_user]
    
    if user_files:
        for file_metadata in user_files:
            st.write(f"**{file_metadata['name']}**")
            st.write(f"Uploaded on: {file_metadata['upload_date']}")
            st.write(f"Downloaded by: {file_metadata['downloaded_by'] or 'N/A'}")
            download_button = st.download_button(
                label="Download",
                data=open(f"uploaded_files/{file_metadata['name']}", "rb").read(),
                file_name=file_metadata['name'],
                mime="application/octet-stream"
            )
            
            if download_button:
                file_metadata["download_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                file_metadata["downloaded_by"] = current_user
                save_files(files)
                st.success(f"File {file_metadata['name']} downloaded successfully!")

    else:
        st.write("No files uploaded yet.")

def inject_css():
    css = """
    <style>
    body {
        background-color: #f0f8ff; /* Light blue background */
        font-family: 'Arial', sans-serif;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 5px;
        padding: 10px 20px;
        border: none;
        cursor: pointer;
        font-size: 16px;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    h1, h2, h3 {
        color: #2e4a7d; /* Dark blue for titles */
        text-align: center;
    }
    .stFileUploader {
        border: 2px dashed #4CAF50;
        padding: 20px;
        margin: 20px;
        border-radius: 10px;
    }
    .stFileUploader>div {
        text-align: center;
    }
    .stRadio>div>label {
        font-size: 18px;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

def inject_js():
    js_code = """
    <script>
    document.addEventListener('DOMContentLoaded', function() {
        document.documentElement.style.scrollBehavior = "smooth"; // Smooth scroll
    });
    </script>
    """
    st.markdown(js_code, unsafe_allow_html=True)

def main():
    if 'username' not in st.session_state:
        st.session_state['username'] = None
    
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Home", "Register", "Login", "Upload Files", "View My Files"])

    inject_css()
    inject_js()
    
    if page == "Home":
        st.title("Employee Database Portal")
        st.write("Please register or login to continue.")
    
    elif page == "Register":
        if register_user():
            st.experimental_user()
    
    elif page == "Login":
        if login_user():
            st.experimental_user()
    
    elif page == "Upload Files":
        if st.session_state['username']:
            upload_files()
        else:
            st.warning("You must be logged in to upload files.")
    
    elif page == "View My Files":
        if st.session_state['username']:
            view_files()
        else:
            st.warning("You must be logged in to view files.")
    
    # Logout button
    if st.sidebar.button("Logout"):
        st.session_state['username'] = None
        st.success("You have logged out successfully!")
        st.experimental_user()

if __name__ == "__main__":
    if not os.path.exists("uploaded_files"):
        os.mkdir("uploaded_files")
    
    main()


