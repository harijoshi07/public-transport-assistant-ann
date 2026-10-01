"""Train the ETA network on updated_eta_dataset_BA.csv and save it for Django."""

import json
import os

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import MinMaxScaler

FEATURES = ["curr_stop", "next_stop", "hour", "distance_km", "speed_kmh"]
TARGET = "travel_time_min"


def main():
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    csv_path = os.path.join(root, "data", "updated_eta_dataset_BA.csv")
    out_dir = os.path.join(os.path.dirname(__file__), "weights")
    os.makedirs(out_dir, exist_ok=True)

    df = pd.read_csv(csv_path)
    df = df[
        df["speed_kmh"].between(1, 80)
        & df["travel_time_min"].between(0.4, 90)
        & df["distance_km"].between(0.05, 15)
    ].copy()
    print(f"rows after cleaning: {len(df)}")

    X = df[FEATURES].to_numpy(dtype=float)
    y = df[TARGET].to_numpy(dtype=float)
    scaler_x = MinMaxScaler()
    scaler_y = MinMaxScaler()
    x_scaled = scaler_x.fit_transform(X)
    y_scaled = scaler_y.fit_transform(y.reshape(-1, 1)).ravel()

    x_train, x_test, y_train, y_test = train_test_split(
        x_scaled, y_scaled, test_size=0.2, random_state=42
    )

    model = MLPRegressor(
        hidden_layer_sizes=(64, 32),
        activation="relu",
        solver="adam",
        learning_rate_init=0.001,
        batch_size=256,
        max_iter=40,
        early_stopping=True,
        validation_fraction=0.1,
        n_iter_no_change=6,
        random_state=42,
    )
    model.fit(x_train, y_train)

    pred_scaled = model.predict(x_test).reshape(-1, 1)
    pred_min = scaler_y.inverse_transform(pred_scaled).ravel()
    actual_min = scaler_y.inverse_transform(y_test.reshape(-1, 1)).ravel()
    mae = float(mean_absolute_error(actual_min, pred_min))
    r2 = float(r2_score(actual_min, pred_min))
    mape = float(mean_absolute_percentage_error(actual_min, pred_min) * 100)
    print(f"holdout MAE {mae:.2f} min | MAPE {mape:.1f}% | R2 {r2:.3f}")

    speed_by_hour = {
        int(hour): float(value)
        for hour, value in df.groupby("hour")["speed_kmh"].median().items()
    }
    bundle = {
        "model": model,
        "scaler_x": scaler_x,
        "scaler_y": scaler_y,
        "features": FEATURES,
        "speed_by_hour": speed_by_hour,
        "default_speed": float(df["speed_kmh"].median()),
        "metrics": {"mae_min": round(mae, 2), "mape": round(mape, 1), "r2": round(r2, 3)},
    }
    out_path = os.path.join(out_dir, "eta_ann.joblib")
    joblib.dump(bundle, out_path)
    with open(os.path.join(out_dir, "eta_metrics.json"), "w", encoding="utf-8") as handle:
        json.dump(bundle["metrics"], handle, indent=2)
    print("saved", out_path)

    sample = np.array([[10, 9, 9, 1.0, 15.0]], dtype=float)
    sample = np.clip(sample, scaler_x.data_min_, scaler_x.data_max_)
    minutes = scaler_y.inverse_transform(model.predict(scaler_x.transform(sample)).reshape(-1, 1))[0, 0]
    print(f"sample 1.0 km at 15 km/h, hour 9 -> {minutes:.1f} min")


if __name__ == "__main__":
    main()
