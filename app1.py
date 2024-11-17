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
from dotenv import load_dotenv
from auth import Authenticator

# Set the page configuration
st.set_page_config(page_title="Hydrate Event Detection App", layout="wide")

# Load environment variables
load_dotenv()

# Email credentials
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")

# Load the trained LSTM model
MODEL_PATH = "lstm_model.h5"  # Path to your retrained model
lstm_model = load_model(MODEL_PATH)

# Authentication setup
allowed_users = os.getenv("ALLOWED_USERS").split(",")
authenticator = Authenticator(
    allowed_users=allowed_users,
    token_key=os.getenv("TOKEN_KEY"),
    secret_path="client_secret.json",
    redirect_uri="http://localhost:8501",
)

# Check if user is authenticated
authenticator.check_auth()
authenticator.login()

st.title("Hydrate Event Detection and Prediction")

# Only proceed if logged in
if st.session_state.get("connected"):
    # Welcome message
    st.write(f"Welcome, {st.session_state['user_info'].get('email')}!")

    # Logout button
    if st.button("Log out"):
        authenticator.logout()

    # File upload setup
    UPLOAD_FOLDER = "./uploaded_files"
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    def preprocess_dummy_data(df):
        df['Inj Gas Meter Volume Setpoint'] = df['Inj Gas Meter Volume Setpoint'].fillna(method='ffill').fillna(method='bfill')
        df['Inj Gas Valve Percent Open'] = df['Inj Gas Valve Percent Open'].fillna(method='ffill').fillna(method='bfill')
        df['Volume Deviation'] = df['Inj Gas Meter Volume Setpoint'] - df['Inj Gas Meter Volume Instantaneous']
        epsilon = 1e-5
        df['Valve Efficiency'] = df['Inj Gas Meter Volume Instantaneous'] / (df['Inj Gas Valve Percent Open'] + epsilon)
        return df.dropna()

    def plot_hydrate_events(df, title="Hydrate Events"):
        fig, ax = plt.subplots(figsize=(15, 10))
        ax.plot(df['Time'], df['Volume Deviation'], label='Volume Deviation', color='blue', alpha=0.7)
        ax.plot(df['Time'], df['Valve Efficiency'], label='Valve Efficiency', color='orange', linestyle='--')
        hydrate_events = df[df['Predictions'] == 1]
        ax.scatter(hydrate_events['Time'], hydrate_events['Volume Deviation'], color='red', label='Hydrate Events', marker='x', s=100)
        ax.set_title(title, fontsize=14)
        ax.set_xlabel('Time', fontsize=12)
        ax.set_ylabel('Metrics', fontsize=12)
        ax.legend()
        ax.grid()
        plt.tight_layout()
        return fig

    def send_email_with_attachments(recipient_email, subject, body, file_paths):
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        for file_path in file_paths:
            if os.path.exists(file_path):
                with open(file_path, "rb") as attachment:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(attachment.read())
                    encoders.encode_base64(part)
                    part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(file_path)}")
                    msg.attach(part)
            else:
                st.error(f"File not found: {file_path}")
                return

        try:
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login(SENDER_EMAIL, SENDER_PASSWORD)
                server.sendmail(SENDER_EMAIL, recipient_email, msg.as_string())
            st.success("Email sent successfully!")
        except Exception as e:
            st.error(f"Failed to send email: {e}")

    st.subheader("Upload and Analyze Your File")
    uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)
            st.write("Raw Data:")
            st.dataframe(df)

            # Preprocess the data
            processed_data = preprocess_dummy_data(df)
            st.write("Processed Data:")
            st.dataframe(processed_data)

            # Predict hydrate events
            X_dummy = processed_data[['Volume Deviation', 'Valve Efficiency']].values
            timesteps = 1
            features = X_dummy.shape[1]
            X_dummy_lstm = X_dummy.reshape((X_dummy.shape[0], timesteps, features))
            predictions = lstm_model.predict(X_dummy_lstm)
            processed_data['Predictions'] = (predictions > 0.5).astype(int)
            st.write("Data with Predictions:")
            st.dataframe(processed_data)

            # spike_data = processed_data[processed_data['Predictions'] == 1]
            timeArray = []
            start_time = None
            start_index = None

            for index, row in processed_data.iterrows():
                if row['Predictions'] == 1:
                    if start_time is None:
                        # Start a new range
                        start_time = row['Time']
                        start_index = index
                else:
                    if start_time is not None:
                        # End the current range
                        end_time = processed_data.loc[index - 1, 'Time']
                        end_index = index - 1
                        timeArray.append([[start_time, end_time], [start_index, end_index]])
                        start_time = None
                        start_index = None

            # Handle the case where the last row is part of a range
            if start_time is not None:
                end_time = processed_data.iloc[-1]['Time']
                end_index = processed_data.index[-1]
                timeArray.append([[start_time, end_time], [start_index, end_index]])

            # Join into a coherent string
            result_strings = []
            for time_range, index_range in timeArray:
                if time_range[0] == time_range[1]:  # Single time
                    result_strings.append(f"At {time_range[0]} (Index {index_range[0]})")
                else:  # Time range
                    result_strings.append(
                        f"From {time_range[0]} to {time_range[1]} (Indices {index_range[0]}-{index_range[1]})"
                    )

            final_string = " || ".join(result_strings)

            st.write(f"Hydrate Events @: {final_string}")
            # Save processed data
            processed_file_path = os.path.join(UPLOAD_FOLDER, "processed_data.csv")
            processed_data.to_csv(processed_file_path, index=False)
            st.success(f"Processed data saved to `{processed_file_path}`")

            # Save only spike data (hydrate events)
            spike_data = processed_data[processed_data['Predictions'] == 1]
            spike_file_path = os.path.join(UPLOAD_FOLDER, "predictions.csv")
            spike_data.to_csv(spike_file_path, index=False)
            st.success(f"Spike data (hydrate events) saved to `{spike_file_path}`")

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
            logged_in_user_email = st.session_state['user_info'].get('email')
            if st.button("Send Email"):
                send_email_with_attachments(
                    recipient_email=logged_in_user_email,
                    subject="Hydrate Events Predictions",
                    body="Attached are the processed data and predictions for hydrate events (spikes only).",
                    file_paths=[processed_file_path, spike_file_path]
                )
        except Exception as e:
            st.error(f"Error processing file: {e}")
else:
    st.warning("You must be logged in to upload and analyze files.")
