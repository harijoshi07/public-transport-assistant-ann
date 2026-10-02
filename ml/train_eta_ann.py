"""
Public Transportation Assistance using Artificial Neural Network
ETA (Estimated Time of Arrival) Prediction Model Training Pipeline

Institution: IOE Thapathali Campus, Tribhuvan University
Supervisor: Er. Kiran Chandra Dahal
Date: March 2024

Model Architecture (Section 5.2.3 of Project Report):
  - Input Layer: 10 normalized features
  - Hidden Layer 1: Dense(64, ReLU) + Dropout(0.3)
  - Hidden Layer 2: Dense(32, ReLU) + Dropout(0.3)
  - Output Layer: Dense(1, Linear) -> Predicted Travel Time
  - Loss: Mean Absolute Error (MAE)
  - Optimizer: Adam
  - Evaluation: MAE, MSE, RMSE, MAPE, R^2 Score
"""

import os
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

def build_eta_model(input_dim=10):
    """Constructs the feedforward artificial neural network architecture."""
    model = keras.Sequential([
        layers.Input(shape=(input_dim,), name="input_features"),
        layers.Dense(64, activation="relu", name="dense_64"),
        layers.Dropout(0.3, name="dropout_1"),
        layers.Dense(32, activation="relu", name="dense_32"),
        layers.Dropout(0.3, name="dropout_2"),
        layers.Dense(1, activation="linear", name="output_travel_time")
    ], name="ETA_Neural_Network")
    
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=0.001),
        loss="mean_absolute_error",
        metrics=["mae", "mse"]
    )
    return model

def calculate_mape(y_true, y_pred):
    """Calculates Mean Absolute Percentage Error (MAPE)."""
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    non_zero = y_true != 0
    return np.mean(np.abs((y_true[non_zero] - y_pred[non_zero]) / y_true[non_zero])) * 100

def generate_synthetic_features(n_samples=5000):
    """
    Generates representative synthetic training data matching the distribution
    of Kathmandu public transit corridors (for standalone reproducibility).
    """
    np.random.seed(42)
    # Features: current_station_id, next_station_id, hour, distance_km, speed_kmh,
    #           congestion_index, day_of_week, elevation_delta, weather_factor, stops_remaining
    current_station = np.random.randint(1, 150, n_samples)
    next_station = current_station + np.random.randint(1, 4, n_samples)
    hour = np.random.randint(6, 21, n_samples)
    distance_km = np.random.uniform(0.5, 8.0, n_samples)
    speed_kmh = np.random.uniform(10.0, 45.0, n_samples)
    congestion = np.where((hour >= 9) & (hour <= 11) | (hour >= 17) & (hour <= 19), 1.6, 1.0)
    day_of_week = np.random.randint(0, 7, n_samples)
    elevation_delta = np.random.uniform(-50, 50, n_samples)
    weather_factor = np.random.uniform(1.0, 1.2, n_samples)
    stops_remaining = np.random.randint(1, 20, n_samples)

    # Physical baseline transit time (minutes) + residual delay
    travel_time_mins = (distance_km / speed_kmh) * 60 * congestion * weather_factor + np.random.normal(0, 0.5, n_samples)
    travel_time_mins = np.maximum(travel_time_mins, 1.0)

    features = np.column_stack([
        current_station, next_station, hour, distance_km, speed_kmh,
        congestion, day_of_week, elevation_delta, weather_factor, stops_remaining
    ])
    return features, travel_time_mins

def main():
    print("=" * 65)
    print(" Public Transportation Assistance - ANN ETA Model Training")
    print("=" * 65)

    data_path = os.path.join(os.path.dirname(__file__), "..", "data", "average_travel_time_negative_dir.csv")
    
    if not (os.path.exists(data_path) and os.path.getsize(data_path) > 1000):
        raise FileNotFoundError(
            f"Training data not found at {data_path}. "
            "generate_synthetic_features() is for smoke tests only and is not used for any reported score."
        )
    print(f"[*] Loading transit training dataset from: {data_path}")
    df = pd.read_csv(data_path)
    # Select numeric feature columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    X = df[numeric_cols[:-1]].values
    y = df[numeric_cols[-1]].values

    # Feature scaling (Min-Max normalization)
    scaler_X = MinMaxScaler()
    scaler_y = MinMaxScaler()

    X_scaled = scaler_X.fit_transform(X)
    y_scaled = scaler_y.fit_transform(y.reshape(-1, 1)).flatten()

    # 80:20 Train-Test split
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y_scaled, test_size=0.20, random_state=42
    )

    print(f"[*] Training samples: {X_train.shape[0]} | Testing samples: {X_test.shape[0]}")
    print("[*] Building ANN architecture: [Input: 10] -> [Dense: 64] -> [Dense: 32] -> [Dense: 1]")
    
    model = build_eta_model(input_dim=X_train.shape[1])
    model.summary()

    print("\n[*] Training for 100 epochs (Batch size: 64)...")
    history = model.fit(
        X_train, y_train,
        validation_split=0.1,
        epochs=100,
        batch_size=64,
        verbose=1
    )

    # Predictions & Evaluation on held-out test set
    y_pred = model.predict(X_test).flatten()

    mae = mean_absolute_error(y_test, y_pred)
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    mape = calculate_mape(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    print("\n" + "=" * 65)
    print(" MODEL PERFORMANCE & ERROR ANALYSIS (Held-Out 20% Test Set)")
    print("=" * 65)
    print(f" Mean Absolute Error (MAE)        : {mae:.6f}")
    print(f" Mean Squared Error (MSE)         : {mse:.8f}")
    print(f" Root Mean Squared Error (RMSE)   : {rmse:.6f}")
    print(f" Mean Absolute Percentage (MAPE)  : {mape:.2f}%")
    print(f" Coefficient of Determination (R2): {r2:.4f}")
    print("=" * 65)

    # Save model weights and configuration
    save_dir = os.path.join(os.path.dirname(__file__), "weights")
    os.makedirs(save_dir, exist_ok=True)
    model_save_path = os.path.join(save_dir, "eta_ann_model.keras")
    model.save(model_save_path)
    print(f"[*] Trained model successfully exported to: {model_save_path}\n")

if __name__ == "__main__":
    main()
