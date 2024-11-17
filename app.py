import streamlit as st
import pandas as pd
import os

import os
import streamlit as st
from dotenv import load_dotenv
from auth import Authenticator

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

load_dotenv()

# emails of users that are allowed to login
allowed_users = os.getenv("ALLOWED_USERS").split(",")

st.title("Streamlit Google Auth")

authenticator = Authenticator(
    allowed_users=allowed_users,
    token_key=os.getenv("TOKEN_KEY"),
    secret_path="client_secret.json",
    redirect_uri="http://localhost:8501",
)
authenticator.check_auth()
authenticator.login()

# show content that requires login
if st.session_state["connected"]:
    st.write(f"welcome! {st.session_state['user_info'].get('email')}")
    if st.button("Log out"):
        authenticator.logout()

if not st.session_state["connected"]:
    st.write("you have to log in first ...")

# Set up a folder to store uploaded files
UPLOAD_FOLDER = "./"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Streamlit App
st.title("CSV File Uploader and Storage")

def send_email(to_email, subject, message):
    sender_email = "eognotifications@gmail.com"
    sender_password = "pihy bwrp kbpl clcd"

    # Set up the email content
    msg = MIMEText(message)
    msg["From"] = sender_email
    msg["To"] = to_email
    msg["Subject"] = subject

    try:
        # Set up the server
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        return "Email sent successfully!"
    except Exception as e:
        return f"Failed to send email: {e}"

# File uploader widget
uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_file:
    try:
        # Read the uploaded CSV file
        df = pd.read_csv(uploaded_file)
        
        # Display the contents of the CSV file
        st.write("File Preview:")
        st.dataframe(df)
        
        # Save the file to the UPLOAD_FOLDER
        file_path = os.path.join(UPLOAD_FOLDER, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        response = send_email(st.session_state['user_info'].get('email'), 'URGENT: Hydate Detected', 'Our system has detected a potential hydrate formation. Please check Hydrate Detector more details.')
        st.success(response)
        
        st.success(f"File successfully uploaded and saved as `{uploaded_file.name}` in `{UPLOAD_FOLDER}`")
    except Exception as e:
        st.error(f"Error processing file: {e}")

