import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from tensorflow.keras.models import load_model
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import smtplib
import os

# Load the trained LSTM model
MODEL_PATH = "lstm_model.h5"  # Replace with your saved model file path
lstm_model = load_model(MODEL_PATH)

# Function to preprocess data
def preprocess_dummy_data(df):
    # Fill missing values
    df['Inj Gas Meter Volume Setpoint'] = df['Inj Gas Meter Volume Setpoint'].fillna(method='ffill').fillna(method='bfill')
    df['Inj Gas Valve Percent Open'] = df['Inj Gas Valve Percent Open'].fillna(method='ffill').fillna(method='bfill')

    # Calculate derived features
    df['Volume Deviation'] = df['Inj Gas Meter Volume Setpoint'] - df['Inj Gas Meter Volume Instantaneous']
    epsilon = 1e-5  # Small value to prevent division by zero
    df['Valve Efficiency'] = df['Inj Gas Meter Volume Instantaneous'] / (df['Inj Gas Valve Percent Open'] + epsilon)

    # Drop rows with any remaining NaN values
    df = df.dropna()
    return df

# Function to plot hydrate events
def plot_hydrate_events(df, title="Hydrate Events"):
    fig, ax = plt.subplots(figsize=(15, 10))
    
    # Plot Volume Deviation
    ax.plot(df['Time'], df['Volume Deviation'], label='Volume Deviation', color='blue', alpha=0.7)
    
    # Plot Valve Efficiency
    ax.plot(df['Time'], df['Valve Efficiency'], label='Valve Efficiency', color='orange', linestyle='--')
    
    # Highlight hydrate events
    hydrate_events = df[df['Predictions'] == 1]
    ax.scatter(hydrate_events['Time'], hydrate_events['Volume Deviation'], color='red', label='Hydrate Events', marker='x', s=100)
    
    # Add titles and labels
    ax.set_title(f"{title}", fontsize=14)
    ax.set_xlabel('Time', fontsize=12)
    ax.set_ylabel('Metrics', fontsize=12)
    ax.legend()
    ax.grid()
    plt.tight_layout()
    return fig

# Function to send email with CSV attachment
def send_email_with_csv(sender_email, sender_password, recipient_email, subject, body, file_path):
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    if os.path.exists(file_path):
        with open(file_path, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(file_path)}")
        msg.attach(part)
    else:
        st.error("Error: File not found.")
        return

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
        st.success("Email sent successfully.")
    except Exception as e:
        st.error(f"Failed to send email: {e}")

# Streamlit app
st.title("Hydrate Events Detection and Prediction")

# File upload
uploaded_file = st.file_uploader("Upload a CSV file", type="csv")
if uploaded_file:
    raw_data = pd.read_csv(uploaded_file)
    st.write("Raw Data:")
    st.dataframe(raw_data)

    # Preprocess data
    processed_data = preprocess_dummy_data(raw_data)
    st.write("Processed Data:")
    st.dataframe(processed_data)

    # Make predictions
    X_dummy = processed_data[['Volume Deviation', 'Valve Efficiency']].values
    timesteps = 1  # Match the timesteps used in training
    features = X_dummy.shape[1]
    X_dummy_lstm = X_dummy.reshape((X_dummy.shape[0], timesteps, features))
    predictions = lstm_model.predict(X_dummy_lstm)
    processed_data['Predictions'] = (predictions > 0.5).astype(int)
    st.write("Data with Predictions:")
    st.dataframe(processed_data)

    # Save predictions
    saved_file_path = "predictions.csv"
    processed_data.to_csv(saved_file_path, index=False)
    st.success(f"Predictions saved to {saved_file_path}")

    # Plot hydrate events
    if st.button("Plot Hydrate Events"):
        if 'Time' in processed_data.columns:
            processed_data['Time'] = pd.to_datetime(processed_data['Time'])
            fig = plot_hydrate_events(processed_data, title="Hydrate Events in Dataset")
            st.pyplot(fig)
        else:
            st.error("'Time' column not found in the dataset.")

    # Email predictions
    st.subheader("Send Predictions via Email")
    sender_email = st.text_input("Your Email")
    sender_password = st.text_input("Your Email Password", type="password")
    recipient_email = st.text_input("Recipient Email")
    subject = st.text_input("Email Subject", value="Hydrate Events Predictions")
    body = st.text_area("Email Body", value="Please find the attached predictions.")
    if st.button("Send Email"):
        send_email_with_csv(sender_email, sender_password, recipient_email, subject, body, saved_file_path)
