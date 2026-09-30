# Artificial Neural Network (ANN) for Arrival Time (ETA) Prediction

This module contains the training architecture and performance evaluation pipeline for the **Estimated Time of Arrival (ETA)** prediction model.

---

## 1. Network Architecture

As specified in **Section 5.2.3** of the Project Report, the model is a multi-layer feedforward dense neural network:

```
[ Input Layer: 10 Features ]
             │
             ▼
   Dense(64, ReLU)
             │
             ▼
       Dropout(0.3)
             │
             ▼
   Dense(32, ReLU)
             │
             ▼
       Dropout(0.3)
             │
             ▼
  [ Output: Dense(1, Linear) ]  ──►  Predicted Travel Time (Normalized)
```

### Input Features:
1. `current_station_id`: Numerical ID of departure station
2. `next_station_id`: Numerical ID of target bus stop
3. `hour_of_day`: Time of day (6 to 21) capturing temporal traffic patterns
4. `distance_km`: Network road distance computed via Graphhopper
5. `speed_kmh`: Historical and instant GPS telemetry speed
6. `congestion_index`: Peak vs. non-peak categorization
7. `day_of_week`: Day index (Sunday to Saturday)
8. `elevation_delta`: Elevation difference between stations
9. `weather_factor`: Meteorological coefficient
10. `stops_remaining`: Count of stops remaining along the transit corridor

---

## 2. Training Parameters

| Hyperparameter | Value | Description |
|----------------|-------|-------------|
| **Framework** | TensorFlow / Keras | Core deep learning library |
| **Optimizer** | Adam | Adaptive moment estimation |
| **Loss Function** | Mean Absolute Error (MAE) | Robust to transit outlier delays |
| **Epochs** | 100 | Training iterations |
| **Batch Size** | 64 | Gradient update sample size |
| **Train/Test Split** | 80% / 20% | Maintained test set distribution |
| **Regularization** | Dropout (0.3) | Prevents overfitting to corridor clusters |

---

## 3. Experimental Results (Held-Out 20% Test Set)

Results from **Table 6-1** of the Project Report:

| Metric | Measured Value | Interpretation |
|--------|----------------|----------------|
| **Coefficient of Determination ($R^2$)** | **0.965** (0.96506) | Model explains 96.5% of variance in travel time |
| **Mean Absolute Percentage Error (MAPE)** | **6.74%** | Average prediction deviation from actual time |
| **Mean Absolute Error (MAE)** | **0.000673** | Normalized units error on held-out test data |
| **Root Mean Squared Error (RMSE)** | **0.001937** | Low variance and penalty on large outliers |
| **Mean Squared Error (MSE)** | **$3.75 \times 10^{-6}$** | Rapid convergence during training |

---

## 4. How to Train the Model

```bash
# Install ML dependencies
pip install tensorflow scikit-learn pandas numpy

# Run training pipeline
python ml/train_eta_ann.py
```
