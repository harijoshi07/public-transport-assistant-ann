"""Live bus position on the stored Kalanki–Koteshwor corridor."""

import math

from django.utils import timezone
from geopy.distance import geodesic

from hardware_app.models import BackupGPSData, DeviceID, RealTimeUpdate
from routeplot_app.api.views import _is_passenger_stop
from routeplot_app.eta_service import current_hour, predict_segment_minutes, speed_for_hour
from routeplot_app.models import RouteInfo, RouteStationInfo

STALE_SECONDS = 30
ON_CORRIDOR_METERS = 450
REPLAY_STEP_KM = 0.95

_CORRIDOR = None
_REPLAYS = {}


def _as_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def ensure_device(device_ident, route_pk=None):
    """Resolve a tracker. A provided route pk is stored on the device."""
    dev_num = _as_int(device_ident)
    if dev_num is None:
        return None

    route = None
    route_pk = _as_int(route_pk)
    if route_pk is not None:
        route = RouteInfo.objects.filter(pk=route_pk).first()

    dev = DeviceID.objects.filter(device_id=dev_num).first() or DeviceID.objects.filter(pk=dev_num).first()
    if dev is None:
        return DeviceID.objects.create(
            device_id=dev_num,
            device_name=f"Bus-{dev_num:02d}",
            route_id=route,
        )

    changed = []
    if route is not None and dev.route_id_id != route.pk:
        dev.route_id = route
        changed.append("route_id")
    generic = {"Bus Device", f"Bus-{dev_num}"}
    if dev.device_name in generic:
        dev.device_name = f"Bus-{dev_num:02d}"
        changed.append("device_name")
    if changed:
        dev.save(update_fields=changed)
    return dev


def record_fix(device, latitude, longitude):
    """Keep a single current row per device and append the history table."""
    lat = float(latitude)
    lng = float(longitude)
    rows = list(
        RealTimeUpdate.objects.filter(current_device_id=device).order_by("-current_timestamp", "-pk")
    )
    if rows:
        current = rows[0]
        current.current_latitude = lat
        current.current_longitude = lng
        current.save()
        extra_ids = [row.pk for row in rows[1:]]
        if extra_ids:
            RealTimeUpdate.objects.filter(pk__in=extra_ids).delete()
    else:
        current = RealTimeUpdate.objects.create(
            current_device_id=device,
            current_latitude=lat,
            current_longitude=lng,
        )
    BackupGPSData.objects.create(
        backup_device_id=device,
        backup_latitude=lat,
        backup_longitude=lng,
    )
    return current


def _xy(lat, lng, lat0):
    return (
        lat * 110540.0,
        lng * 111320.0 * math.cos(math.radians(lat0)),
    )


def _point_at(shape, cumulative_km, distance_km):
    if distance_km <= 0:
        return shape[0]
    if distance_km >= cumulative_km[-1]:
        return shape[-1]
    for index in range(len(cumulative_km) - 1):
        start_km = cumulative_km[index]
        end_km = cumulative_km[index + 1]
        if start_km <= distance_km <= end_km:
            span = end_km - start_km
            blend = 0.0 if span <= 1e-6 else (distance_km - start_km) / span
            start = shape[index]
            end = shape[index + 1]
            return [
                start[0] + blend * (end[0] - start[0]),
                start[1] + blend * (end[1] - start[1]),
            ]
    return shape[-1]


def _resample(shape, cumulative_km, step_km):
    if not shape:
        return []
    total = cumulative_km[-1]
    distances = [0.0]
    cursor = step_km
    while cursor < total - (step_km * 0.35):
        distances.append(cursor)
        cursor += step_km
    if total > 0:
        distances.append(total)
    return [_point_at(shape, cumulative_km, distance) for distance in distances]


def _load_corridor():
    route = (
        RouteInfo.objects.filter(route_english_name__icontains="Kalanki")
        .filter(route_english_name__icontains="Koteshwor")
        .filter(route_english_name__icontains="Ratnapark")
        .order_by("id")
        .first()
    )
    if route is None:
        return None

    rows = list(
        RouteStationInfo.objects.filter(route_info=route)
        .select_related("station_info")
        .order_by("station_order")
    )
    origin_order = None
    dest_order = None
    origin_name = "Kalanki"
    dest_name = "Koteshwor"
    for row in rows:
        name = (row.station_info.station_english_name or "").strip()
        if origin_order is None and name.lower() == "kalanki":
            origin_order = row.station_order
            origin_name = name
            continue
        if origin_order is not None and row.station_order > origin_order:
            lowered = name.lower()
            if "koteshwor" in lowered or "koteshwar" in lowered:
                dest_order = row.station_order
                dest_name = name
                break
    if origin_order is None or dest_order is None:
        return None

    selected = [row for row in rows if origin_order <= row.station_order <= dest_order]
    shape = []
    last = None
    for row in selected:
        station = row.station_info
        if station.station_latitude is None or station.station_longitude is None:
            continue
        point = [round(float(station.station_latitude), 6), round(float(station.station_longitude), 6)]
        if point == last:
            continue
        shape.append(point)
        last = point
    if len(shape) < 2:
        return None

    cumulative = [0.0]
    for start, end in zip(shape, shape[1:]):
        cumulative.append(cumulative[-1] + geodesic(start, end).km)

    stops = []
    last_key = None
    for row in selected:
        station = row.station_info
        if not _is_passenger_stop(station):
            continue
        key = (station.station_id, (station.station_english_name or "").strip())
        if key == last_key:
            continue
        last_key = key
        if station.station_latitude is None or station.station_longitude is None:
            continue
        point = [float(station.station_latitude), float(station.station_longitude)]
        along = _snap(point[0], point[1], shape, cumulative)["along_km"]
        stops.append({
            "name": (station.station_english_name or "").strip(),
            "lat": round(point[0], 6),
            "lng": round(point[1], 6),
            "km": round(along, 3),
            "index": len(stops) + 1,
        })

    return {
        "route_pk": route.pk,
        "route_id": route.route_id,
        "route_name": route.route_english_name,
        "origin": origin_name,
        "destination": dest_name,
        "length_km": round(cumulative[-1], 2),
        "shape": shape,
        "cumulative_km": cumulative,
        "stops": stops,
        "replay_path": [
            [round(point[0], 6), round(point[1], 6)]
            for point in _resample(shape, cumulative, REPLAY_STEP_KM)
        ],
    }


def get_corridor():
    global _CORRIDOR
    if _CORRIDOR is None:
        _CORRIDOR = _load_corridor()
    return _CORRIDOR


def _clean_shape(raw):
    shape = []
    last = None
    if not isinstance(raw, list):
        return shape
    for item in raw[:500]:
        if not isinstance(item, (list, tuple)) or len(item) < 2:
            continue
        try:
            point = [round(float(item[0]), 6), round(float(item[1]), 6)]
        except (TypeError, ValueError):
            continue
        if point == last:
            continue
        shape.append(point)
        last = point
    return shape


def _cumulative_km(shape):
    cumulative = [0.0]
    for start, end in zip(shape, shape[1:]):
        cumulative.append(cumulative[-1] + geodesic(start, end).km)
    return cumulative


def build_trip_corridor(origin, destination, route_pk, shape, stops):
    """Build a replay corridor from the trip currently shown on the map."""
    shape = _clean_shape(shape)
    if len(shape) < 2:
        return None
    cumulative = _cumulative_km(shape)
    origin_name = (origin or "Start").strip() or "Start"
    dest_name = (destination or "End").strip() or "End"
    route_pk = _as_int(route_pk)
    route_public = None
    if route_pk is not None:
        route = RouteInfo.objects.filter(pk=route_pk).first()
        if route is None:
            route_pk = None
        else:
            route_public = route.route_id

    built_stops = []
    if isinstance(stops, list):
        for item in stops[:80]:
            if not isinstance(item, dict):
                continue
            name = str(item.get("name") or "").strip()
            try:
                lat = float(item.get("lat"))
                lng = float(item.get("lng"))
            except (TypeError, ValueError):
                continue
            if not name:
                continue
            along = _snap(lat, lng, shape, cumulative)["along_km"]
            built_stops.append({
                "name": name,
                "lat": round(lat, 6),
                "lng": round(lng, 6),
                "km": along,
            })
    built_stops.sort(key=lambda stop: stop["km"])
    deduped = []
    for stop in built_stops:
        if deduped and abs(deduped[-1]["km"] - stop["km"]) < 0.02 and deduped[-1]["name"] == stop["name"]:
            continue
        deduped.append(stop)
    if len(deduped) < 2:
        deduped = [
            {"name": origin_name, "lat": shape[0][0], "lng": shape[0][1], "km": 0.0},
            {"name": dest_name, "lat": shape[-1][0], "lng": shape[-1][1], "km": cumulative[-1]},
        ]
    for index, stop in enumerate(deduped, start=1):
        stop["index"] = index
        stop["km"] = round(stop["km"], 3)

    return {
        "route_pk": route_pk,
        "route_id": route_public,
        "route_name": f"{origin_name} → {dest_name}",
        "origin": origin_name,
        "destination": dest_name,
        "length_km": round(cumulative[-1], 2),
        "shape": shape,
        "cumulative_km": cumulative,
        "stops": deduped,
        "replay_path": [
            [round(point[0], 6), round(point[1], 6)]
            for point in _resample(shape, cumulative, REPLAY_STEP_KM)
        ],
        "source": "trip",
    }


def set_trip_replay(replay_id, corridor):
    if len(_REPLAYS) > 12:
        _REPLAYS.pop(next(iter(_REPLAYS)))
    _REPLAYS[replay_id] = corridor


def clear_trip_replay(replay_id):
    _REPLAYS.pop(replay_id, None)


def _snap(lat, lng, shape, cumulative_km):
    lat0 = shape[0][0]
    px, py = _xy(lat, lng, lat0)
    best = None
    for index in range(len(shape) - 1):
        ax, ay = _xy(shape[index][0], shape[index][1], lat0)
        bx, by = _xy(shape[index + 1][0], shape[index + 1][1], lat0)
        dx, dy = bx - ax, by - ay
        length_sq = dx * dx + dy * dy
        if length_sq <= 1:
            blend = 0.0
        else:
            blend = ((px - ax) * dx + (py - ay) * dy) / length_sq
            blend = max(0.0, min(1.0, blend))
        cx, cy = ax + blend * dx, ay + blend * dy
        distance_m = math.hypot(px - cx, py - cy)
        along = cumulative_km[index] + blend * (cumulative_km[index + 1] - cumulative_km[index])
        if best is None or distance_m < best[0]:
            best = (
                distance_m,
                along,
                shape[index][0] + blend * (shape[index + 1][0] - shape[index][0]),
                shape[index][1] + blend * (shape[index + 1][1] - shape[index][1]),
            )
    return {
        "distance_m": best[0],
        "along_km": best[1],
        "lat": best[2],
        "lng": best[3],
    }


def _traveled(shape, cumulative_km, along_km):
    points = []
    for index, point in enumerate(shape):
        if cumulative_km[index] < along_km - 1e-4:
            points.append(point)
        else:
            break
    snapped = _point_at(shape, cumulative_km, along_km)
    snapped = [round(snapped[0], 6), round(snapped[1], 6)]
    if not points or points[-1] != snapped:
        points.append(snapped)
    return points


def _minutes(distance_km, from_index, to_index, hour, speed):
    if distance_km < 0.08:
        return 0.0
    return predict_segment_minutes(from_index, to_index, hour, distance_km, speed)


def _display_minutes(value):
    if value <= 0.4:
        return 0
    return max(1, int(round(value)))


def _etas(along_km, stops, hour, speed):
    if not stops:
        return None, None, None, None
    end = stops[-1]
    if along_km >= end["km"] - 0.08:
        return end["name"], 0, end["name"], 0

    next_index = 0
    while next_index < len(stops) and stops[next_index]["km"] <= along_km + 0.03:
        next_index += 1
    if next_index >= len(stops):
        return end["name"], 0, end["name"], 0

    previous_index = stops[next_index - 1]["index"] if next_index else 1
    cursor_km = along_km
    next_minutes = None
    total = 0.0
    next_name = stops[next_index]["name"]
    for stop in stops[next_index:]:
        hop_km = max(0.0, stop["km"] - cursor_km)
        hop_minutes = _minutes(hop_km, previous_index, stop["index"], hour, speed)
        if next_minutes is None:
            next_minutes = hop_minutes
        total += hop_minutes
        cursor_km = stop["km"]
        previous_index = stop["index"]
    return next_name, _display_minutes(next_minutes or 0), end["name"], _display_minutes(total)


def _speed_kmh(device, hour):
    fixes = list(
        BackupGPSData.objects.filter(backup_device_id=device).order_by("-backup_timestamp", "-pk")[:2]
    )
    fallback = round(speed_for_hour(hour), 1)
    if len(fixes) < 2:
        return fallback, "hour"
    newer, older = fixes[0], fixes[1]
    elapsed = (newer.backup_timestamp - older.backup_timestamp).total_seconds()
    if elapsed < 1 or elapsed > 120:
        return fallback, "hour"
    distance_km = geodesic(
        (newer.backup_latitude, newer.backup_longitude),
        (older.backup_latitude, older.backup_longitude),
    ).km
    inferred = distance_km / (elapsed / 3600.0)
    if inferred < 5 or inferred > 70:
        return fallback, "hour"
    return round(inferred, 1), "gps"


def _describe_bus(row, corridor):
    device = row.current_device_id
    age = max(0, int((timezone.now() - row.current_timestamp).total_seconds()))
    hour = current_hour()
    speed, speed_source = _speed_kmh(device, hour)
    payload = {
        "device_id": device.device_id,
        "name": device.device_name,
        "route_pk": device.route_id_id,
        "lat": round(float(row.current_latitude), 6),
        "lng": round(float(row.current_longitude), 6),
        "age_seconds": age,
        "stale": age > STALE_SECONDS,
        "speed_kmh": speed,
        "speed_source": speed_source,
        "on_corridor": False,
        "snapped_lat": None,
        "snapped_lng": None,
        "along_km": None,
        "next_stop": None,
        "eta_next_min": None,
        "end_stop": None,
        "eta_end_min": None,
        "traveled": [],
    }
    if corridor is None:
        return payload

    snap = _snap(row.current_latitude, row.current_longitude, corridor["shape"], corridor["cumulative_km"])
    assigned = device.route_id_id == corridor["route_pk"]
    if snap["distance_m"] > ON_CORRIDOR_METERS and not assigned:
        return None
    on_line = snap["distance_m"] <= ON_CORRIDOR_METERS
    payload["on_corridor"] = on_line
    if not on_line:
        return payload

    payload["snapped_lat"] = round(snap["lat"], 6)
    payload["snapped_lng"] = round(snap["lng"], 6)
    payload["along_km"] = round(snap["along_km"], 3)
    payload["traveled"] = _traveled(corridor["shape"], corridor["cumulative_km"], snap["along_km"])
    next_stop, eta_next, end_stop, eta_end = _etas(snap["along_km"], corridor["stops"], hour, speed)
    payload["next_stop"] = next_stop
    payload["eta_next_min"] = eta_next
    payload["end_stop"] = end_stop
    payload["eta_end_min"] = eta_end
    return payload


def live_payload(replay_id=None):
    override = _REPLAYS.get(replay_id) if replay_id else None
    corridor = override or get_corridor()
    public = None
    if corridor is not None:
        public = {
            "source": corridor.get("source") or ("trip" if override else "default"),
            "route_pk": corridor["route_pk"],
            "route_id": corridor["route_id"],
            "route_name": corridor["route_name"],
            "origin": corridor["origin"],
            "destination": corridor["destination"],
            "length_km": corridor["length_km"],
            "shape": corridor["shape"],
            "stops": [
                {"name": stop["name"], "lat": stop["lat"], "lng": stop["lng"], "km": stop["km"]}
                for stop in corridor["stops"]
            ],
            "replay_path": corridor["replay_path"],
        }

    buses = []
    seen = set()
    rows = (
        RealTimeUpdate.objects.select_related("current_device_id")
        .order_by("-current_timestamp", "-pk")
    )
    for row in rows:
        device_pk = row.current_device_id_id
        if device_pk in seen:
            continue
        seen.add(device_pk)
        described = _describe_bus(row, corridor)
        if described is None:
            continue
        if override is not None and not described.get("on_corridor"):
            continue
        buses.append(described)
    return {"corridor": public, "buses": buses}
