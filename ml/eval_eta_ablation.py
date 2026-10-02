"""Score the ETA network without the speed leak.

Rows: physics baseline, full model, no speed, speed replaced by the hour median.
Uses the same cleaning, 80/20 split (random_state=42) and settings as export_eta_model.py.
"""
import os

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import MinMaxScaler

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
df = pd.read_csv(os.path.join(ROOT, "data", "updated_eta_dataset_BA.csv"))
df = df[
    df["speed_kmh"].between(1, 80)
    & df["travel_time_min"].between(0.4, 90)
    & df["distance_km"].between(0.05, 15)
].copy()

FULL = ["curr_stop", "next_stop", "hour", "distance_km", "speed_kmh"]
NO_SPEED = ["curr_stop", "next_stop", "hour", "distance_km"]
TARGET = "travel_time_min"

train, test = train_test_split(df, test_size=0.2, random_state=42)


def scores(actual, pred):
    return (
        mean_absolute_error(actual, pred),
        mean_absolute_percentage_error(actual, pred) * 100,
        r2_score(actual, pred),
    )


def fit_and_score(features, test_frame):
    sx, sy = MinMaxScaler(), MinMaxScaler()
    x_train = sx.fit_transform(train[features])
    y_train = sy.fit_transform(train[[TARGET]]).ravel()
    model = MLPRegressor(
        hidden_layer_sizes=(64, 32), activation="relu", solver="adam",
        learning_rate_init=0.001, batch_size=256, max_iter=40,
        early_stopping=True, validation_fraction=0.1, n_iter_no_change=6,
        random_state=42,
    ).fit(x_train, y_train)
    pred = sy.inverse_transform(model.predict(sx.transform(test_frame[features])).reshape(-1, 1)).ravel()
    return scores(test_frame[TARGET].to_numpy(), pred)


rows = {}

# 1. Physics baseline: no model, just distance / speed.
baseline = test["distance_km"] / test["speed_kmh"] * 60
rows["distance / speed baseline"] = scores(test[TARGET].to_numpy(), baseline.to_numpy())

# 2. Full model, measured speed (what the README reports now).
rows["full model, measured speed"] = fit_and_score(FULL, test)

# 3. No speed input at all.
rows["no speed input"] = fit_and_score(NO_SPEED, test)

# 4. Speed replaced by the training-set median for that hour (what the app does at inference).
median_by_hour = train.groupby("hour")["speed_kmh"].median()
test_med = test.copy()
test_med["speed_kmh"] = test_med["hour"].map(median_by_hour).fillna(train["speed_kmh"].median())
rows["full model, hour-median speed at test"] = fit_and_score(FULL, test_med)

print(f"{'setting':42s} {'MAE (min)':>10s} {'MAPE %':>8s} {'R2':>7s}")
for name, (mae, mape, r2) in rows.items():
    print(f"{name:42s} {mae:10.2f} {mape:8.1f} {r2:7.3f}")
