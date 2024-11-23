# Hydrate Event Prediction with LSTM

This project predicts hydrate events in gas pipelines based on sensor data using a machine learning pipeline, primarily utilizing an LSTM (Long Short-Term Memory) architecture. The dataset contains time-series data, including parameters such as volume deviation, valve efficiency, and hydrate predictions.

---

## Table of Contents

- [Introduction](#introduction)
- [Dataset Description](#dataset-description)
- [Approach](#approach)
- [Model Architecture](#model-architecture)
- [Results and Validation](#results-and-validation)
- [Installation and Setup](#installation-and-setup)
- [Usage](#usage)
- [Future Enhancements](#future-enhancements)
- [Acknowledgments](#acknowledgments)

---

## Introduction

Hydrate events in gas pipelines can lead to disruptions and inefficiencies in operations. This project uses machine learning, specifically an LSTM model, to predict these events based on sensor readings. The model provides both numerical predictions and graphical visualization of hydrate events.

---

## Dataset Description

The dataset consists of time-series data collected from gas pipeline sensors. Key features include:

- **Time**: Timestamp of the observation.
- **Inj Gas Meter Volume Instantaneous**: Measured gas volume.
- **Inj Gas Meter Volume Setpoint**: Target gas volume.
- **Inj Gas Valve Percent Open**: Percentage of valve openness.
- **Volume Deviation**: Difference between measured and target gas volumes.
- **Valve Efficiency**: Efficiency of the valve based on the measured flow rate.
- **Hydrate_Flag / Hydrate_Predicted**: Indicator for hydrate events (binary: 0 or 1).

---

## Approach

1. **Data Preprocessing**:
   - Cleaned missing values with interpolation and forward/backward filling.
   - Computed derived features like `Volume Deviation` and `Valve Efficiency`.
   - Balanced the dataset to handle class imbalance.

2. **Model Training**:
   - Used an LSTM model for temporal dependency analysis.
   - Computed class weights to handle imbalance during training.
   - Split the data into training and testing sets, stratified by the hydrate events.

3. **Validation**:
   - Evaluated model performance using metrics such as accuracy, precision, recall, F1-score, and confusion matrix.
   - Visualized hydrate events with time-series plots.

4. **Dummy Data Generation**:
   - Created dummy datasets to simulate hydrate events for testing and validation.

---

## Model Architecture

The LSTM model consists of:
- **Input Layer**: Processes time-series data (e.g., `Volume Deviation`, `Valve Efficiency`).
- **Hidden Layers**:
  - Multiple LSTM layers with ReLU activation for learning temporal dependencies.
  - Dropout layers for regularization.
- **Output Layer**: A dense layer with sigmoid activation for binary classification.

Example architecture:
```plaintext
LSTM(128) → Dropout(0.2) → LSTM(64) → Dropout(0.2) → Dense(1, activation='sigmoid')
