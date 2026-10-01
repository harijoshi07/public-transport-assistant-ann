"""Load the ETA network trained on data/updated_eta_dataset_BA.csv."""

import os
from datetime import datetime

import joblib
import numpy as np
from django.conf import settings

_BUNDLE = None
_LOADED = False


def _weights_path():
    return os.path.abspath(os.path.join(settings.BASE_DIR, "..", "ml", "weights", "eta_ann.joblib"))


def load_bundle():
    global _BUNDLE, _LOADED
    if _LOADED:
        return _BUNDLE
    _LOADED = True
    path = _weights_path()
    if os.path.exists(path):
        _BUNDLE = joblib.load(path)
    return _BUNDLE


def metrics():
    bundle = load_bundle()
    if not bundle:
        return None
    return bundle.get("metrics")


def speed_for_hour(hour):
    bundle = load_bundle()
    if not bundle:
        return 15.0
    table = bundle.get("speed_by_hour") or {}
    if hour in table:
        return float(table[hour])
    return float(bundle.get("default_speed") or 15.0)


def predict_segment_minutes(curr_stop, next_stop, hour, distance_km, speed_kmh):
    """Minutes for one hop. Stop indexes are clipped into the training range."""
    distance_km = max(float(distance_km), 0.05)
    speed_kmh = max(float(speed_kmh), 5.0)
    bundle = load_bundle()
    if not bundle:
        return (distance_km / speed_kmh) * 60.0

    features = np.array([[curr_stop, next_stop, hour, distance_km, speed_kmh]], dtype=float)
    scaler_x = bundle["scaler_x"]
    features = np.clip(features, scaler_x.data_min_, scaler_x.data_max_)
    scaled = scaler_x.transform(features)
    predicted = bundle["model"].predict(scaled).reshape(-1, 1)
    minutes = float(bundle["scaler_y"].inverse_transform(predicted)[0, 0])
    return max(0.4, minutes)


def current_hour():
    return datetime.now().hour
