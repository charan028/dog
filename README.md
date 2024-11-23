# Hydrate Event Predictor 🚀

Hydrate Event Predictor is a machine learning-powered tool designed to detect and predict hydrate events in gas pipelines. This solution helps pipeline operators identify potential hydrate formations early, minimizing inefficiencies, delays, and costly shutdowns.

---

## 💡 Problem Statement

Hydrate formations in gas pipelines can lead to severe operational challenges, including:
- Increased downtime and maintenance costs
- Risk of equipment damage
- Inefficient gas flow operations

Pipeline operators need an intelligent solution to predict and act on hydrate formation events using sensor data.

---

## 🤖 Solution Overview

Hydrate Event Predictor leverages **time-series data** from gas pipeline sensors to detect hydrate formation patterns. The key features include:
- Analysis of critical metrics like `Volume Deviation` and `Valve Efficiency`
- Predictions powered by **LSTM Neural Networks**
- Visualization of hydrate events in real-time for quick decision-making

---

## 🛠️ Technologies Used

- **LSTM Neural Networks**: For processing and analyzing time-series data.
- **FastAPI**: For building a seamless backend API to serve predictions.
- **Pandas, NumPy, and Matplotlib**: For data preprocessing, analysis, and visualization.
- **MongoDB**: To store and manage pipeline sensor data.
- **Python**: Core programming language for development.

---

## ⚙️ Features

1. **Hydrate Event Detection**  
   - Identifies patterns signaling hydrate formations.  

2. **Real-Time Visualization**  
   - Interactive plots to monitor `Volume Deviation`, `Valve Efficiency`, and other critical metrics.  

3. **Imbalanced Data Handling**  
   - Tackles the challenge of predicting rare hydrate events using class balancing techniques.  

4. **Adaptable Framework**  
   - Works with both real-world and dummy datasets.  

---

## 🧪 Dataset

The dataset includes time-series data from gas pipeline sensors with features like:
- `Inj Gas Meter Volume Instantaneous`
- `Inj Gas Meter Volume Setpoint`
- `Inj Gas Valve Percent Open`
- `Volume Deviation`
- `Valve Efficiency`

Example:
```plaintext
Time                  | Inj Gas Meter Volume Instantaneous | Inj Gas Meter Volume Setpoint | Inj Gas Valve Percent Open | Volume Deviation | Valve Efficiency
2024-11-01 00:00:00  | 120.5                              | 130.0                         | 75.0                      | -9.5             | 1.6
2024-11-01 00:05:00  | 121.0                              | 130.0                         | 74.0                      | -9.0             | 1.64
```

## Installation
```
git clone https://github.com/your-username/hydrate-event-predictor.git
cd hydrate-event-predictor
```
## Install Dependencies

```
pip install -r requirements.txt
```
## Run the Application
```
streamlit run app1.py
```
