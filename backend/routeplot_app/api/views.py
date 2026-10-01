import math
from collections import defaultdict

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework import generics 

from routeplot_app.models import StationInfo, RouteInfo, RouteStationInfo
from routeplot_app.api.seriaizers import StationInfoSerializer, RouteInfoSerializer, RouteStationInfoSerializer

from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

from routeplot_app.eta_service import current_hour, predict_segment_minutes, speed_for_hour, metrics as eta_metrics
 
#----------------------------------------------------------#

def search_stations_autocomplete(request):
    """Fast autocomplete endpoint for transit stops and landmarks with Transit App subtitles."""
    query = request.GET.get('q', '').strip()
    if len(query) < 1:
        return JsonResponse({'results': []})

    results = []
    seen = set()

    # 1. Local Database of 6,582 Kathmandu stations
    stations = StationInfo.objects.filter(
        station_english_name__icontains=query
    ).exclude(station_english_name='Route Point').values(
        'station_id', 'station_english_name', 'station_nepali_name', 'station_latitude', 'station_longitude'
    )[:10]

    for s in stations:
        clean_name = s['station_english_name'].strip()
        if clean_name.lower() not in seen:
            seen.add(clean_name.lower())
            nepali = (s.get('station_nepali_name') or '').strip()
            sub = f"{nepali}, Kathmandu, Bagmati Province, Nepal" if nepali else "Kathmandu, Bagmati Province, Nepal"
            results.append({
                'id': s['station_id'],
                'name': clean_name,
                'sub': sub,
                'lat': s['station_latitude'],
                'lng': s['station_longitude'],
            })

    # 2. Additional OpenStreetMap landmarks in Kathmandu
    if len(results) < 8:
        try:
            geolocator = Nominatim(user_agent="TransitAppKathmandu/2.0")
            places = geolocator.geocode(f"{query}, Kathmandu, Nepal", exactly_one=False, limit=6, timeout=3)
            for p in places or []:
                parts = [x.strip() for x in p.address.split(',')]
                p_name = parts[0]
                p_sub = ", ".join(parts[1:4]) if len(parts) > 1 else "Kathmandu, Nepal"
                if p_name.lower() not in seen:
                    seen.add(p_name.lower())
                    results.append({
                        'id': 0,
                        'name': p_name,
                        'sub': p_sub,
                        'lat': p.latitude,
                        'lng': p.longitude,
                    })
        except Exception:
            pass

    return JsonResponse({'results': results})


def _resolve_location_point(location_str, geolocator):
    """
    Resolves coordinates by checking local StationInfo database of 6,582 Kathmandu stops first.
    Falls back to external Nominatim geocoder for general landmarks.
    """
    clean = location_str.strip().replace(",", " ")
    if not clean:
        return None

    # 1. Local Database lookup (instant & 100% accurate for all bus stops)
    station = (
        StationInfo.objects.filter(station_english_name__iexact=clean).first()
        or StationInfo.objects.filter(station_english_name__icontains=clean).first()
    )
    if station:
        return (station.station_latitude, station.station_longitude, station.station_english_name)

    # 2. Check if input is a literal coordinate pair (lat, lng)
    if ',' in location_str or ';' in location_str:
        try:
            parts = location_str.replace(';', ',').split(',')
            return (float(parts[0].strip()), float(parts[1].strip()), location_str)
        except Exception:
            pass

    # 3. External Nominatim Geocoder for general landmarks (e.g. Civil Hospital, Baluwatar)
    try:
        loc = (
            geolocator.geocode(f"{clean}, Kathmandu, Nepal", timeout=5)
            or geolocator.geocode(f"{clean}, Nepal", timeout=5)
            or geolocator.geocode(clean, timeout=5)
        )
        if loc:
            return (loc.latitude, loc.longitude, clean)
    except Exception:
        pass

    return None


SHAPE_POINT_NAMES = {"route point", "o"}
WALK_KMH = 4.8


def _is_passenger_stop(station):
    english = (getattr(station, "station_english_name", None) or "").strip()
    nepali = (getattr(station, "station_nepali_name", None) or "").strip()
    if not english or english.lower() in SHAPE_POINT_NAMES:
        return False
    # Some shape vertices were stored with a clipped English label ("Rat") and the Nepali for route point.
    if "रुट पोइन्ट" in nepali or "रुटपोइन्ट" in nepali.replace(" ", ""):
        return False
    return True


def _short_place(name):
    text = (name or "").strip()
    for suffix in (" bus route point", " bus stop"):
        if text.lower().endswith(suffix):
            text = text[: -len(suffix)].strip()
    return text or (name or "").strip()


def _fare_npr(distance_km):
    if distance_km <= 5.0:
        return 20
    extra_km = distance_km - 5.0
    return 20 + int(math.ceil(extra_km / 5.0)) * 5


def _path_km(points):
    total = 0.0
    for start, end in zip(points, points[1:]):
        total += geodesic(start, end).km
    return total


def _nearest_candidates(point, stations, limit=8):
    ranked = sorted(
        stations,
        key=lambda station: geodesic(point, (station.station_latitude, station.station_longitude)).km,
    )
    return ranked[:limit]


def _stored_corridor(origin_stops, dest_stops):
    """Pick the stored route that serves both stops in order, with the shortest span."""
    origin_ids = [station.pk for station in origin_stops]
    dest_ids = [station.pk for station in dest_stops]
    origin_by_id = {station.pk: station for station in origin_stops}
    dest_by_id = {station.pk: station for station in dest_stops}

    origin_links = defaultdict(list)
    dest_links = defaultdict(list)
    for station_id, route_id, order in RouteStationInfo.objects.filter(
        station_info_id__in=origin_ids
    ).values_list("station_info_id", "route_info_id", "station_order"):
        origin_links[route_id].append((station_id, order))
    for station_id, route_id, order in RouteStationInfo.objects.filter(
        station_info_id__in=dest_ids
    ).values_list("station_info_id", "route_info_id", "station_order"):
        dest_links[route_id].append((station_id, order))

    origin_rank = {station.pk: index for index, station in enumerate(origin_stops)}
    dest_rank = {station.pk: index for index, station in enumerate(dest_stops)}
    best = None
    for route_id, origins in origin_links.items():
        destinations = dest_links.get(route_id)
        if not destinations:
            continue
        for origin_id, origin_order in origins:
            for dest_id, dest_order in destinations:
                if origin_order == dest_order:
                    continue
                forward = dest_order > origin_order
                span = abs(dest_order - origin_order)
                rank = (origin_rank[origin_id] + dest_rank[dest_id], 0 if forward else 1, span)
                if best is None or rank < best[0]:
                    best = (rank, route_id, origin_by_id[origin_id], dest_by_id[dest_id], origin_order, dest_order, forward)

    if best is None:
        return None

    _, route_id, origin_stop, dest_stop, origin_order, dest_order, forward = best
    low, high = min(origin_order, dest_order), max(origin_order, dest_order)
    rows = list(
        RouteStationInfo.objects.filter(
            route_info_id=route_id,
            station_order__gte=low,
            station_order__lte=high,
        ).select_related("station_info").order_by("station_order")
    )
    if not forward:
        rows.reverse()
    route = RouteInfo.objects.get(pk=route_id)
    return route, origin_stop, dest_stop, rows


def _rows_to_shape(rows):
    shape = []
    last = None
    for row in rows:
        station = row.station_info
        if station.station_latitude is None or station.station_longitude is None:
            continue
        point = [round(float(station.station_latitude), 6), round(float(station.station_longitude), 6)]
        if point == last:
            continue
        shape.append(point)
        last = point
    return shape


def _passenger_indexes(rows):
    indexes = []
    last_key = None
    for index, row in enumerate(rows):
        station = row.station_info
        if not _is_passenger_stop(station):
            continue
        key = (station.station_id, station.station_english_name)
        if key == last_key:
            continue
        last_key = key
        indexes.append(index)
    return indexes


def predict_eta(request):
    """Run the trained network for one hop. Used by the AI Model tab."""
    try:
        distance_km = float(request.GET.get("distance_km", "1"))
        speed_kmh = float(request.GET.get("speed_kmh", "15"))
        hour = int(request.GET.get("hour", current_hour()))
    except (TypeError, ValueError):
        return JsonResponse({"error": "Invalid ETA inputs."}, status=400)

    minutes = predict_segment_minutes(10, 9, hour, distance_km, speed_kmh)
    linear = (max(distance_km, 0.05) / max(speed_kmh, 5.0)) * 60.0
    payload = {
        "eta_min": round(minutes, 1),
        "linear_min": round(linear, 1),
        "metrics": eta_metrics(),
    }
    return JsonResponse(payload)


def nearest_station_info(request, userlocation, destlocation):
    """Geocodes origin and destination, identifies nearest transit stops, and computes fares."""
    geolocator = Nominatim(user_agent="PublicTransportAssistant/1.0")

    user_point = _resolve_location_point(userlocation, geolocator)
    dest_point = _resolve_location_point(destlocation, geolocator)

    # Retrieve all routes so the sidebar remains populated
    routes = RouteInfo.objects.all()
    routes_data = [
        {
            'route_id': item.id,
            'route_actual_id': item.route_id,
            'route_name': item.route_english_name,
            'route_start': item.start,
            'route_end': item.end,
        }
        for item in routes
    ]

    if not user_point:
        return render(request, 'home.html', {
            'error': f'Could not find coordinates for origin "{userlocation}". Please enter a recognized landmark or transit stop.',
            'routes_variable': routes_data,
        })

    if not dest_point:
        return render(request, 'home.html', {
            'error': f'Could not find coordinates for destination "{destlocation}". Please enter a recognized landmark or transit stop.',
            'routes_variable': routes_data,
        })

    user_location = (user_point[0], user_point[1])
    dest_location = (dest_point[0], dest_point[1])

    all_stations = list(StationInfo.objects.exclude(station_english_name='Route Point'))
    if not all_stations:
        all_stations = list(StationInfo.objects.all())

    try:
        origin_candidates = _nearest_candidates(user_location, all_stations)
        dest_candidates = _nearest_candidates(dest_location, all_stations)
        nearest_user_station = origin_candidates[0]
        nearest_dest_station = dest_candidates[0]
    except Exception:
        return render(request, 'home.html', {
            'error': 'Station data not found. Please ensure database seeders have run.',
            'routes_variable': routes_data,
        })

    corridor = _stored_corridor(origin_candidates, dest_candidates)
    hour = current_hour()
    speed = speed_for_hour(hour)
    trip_shape = []
    ride_stops = []
    stored_route_name = ""
    uses_stored_route = False
    bus_eta_min = 0.0

    if corridor:
        route, nearest_user_station, nearest_dest_station, rows = corridor
        uses_stored_route = True
        stored_route_name = route.route_english_name
        trip_shape = _rows_to_shape(rows)
        indexes = _passenger_indexes(rows)
        ride_stops = []
        for index in indexes:
            station = rows[index].station_info
            ride_stops.append({
                "name": (station.station_english_name or "").strip(),
                "lat": station.station_latitude,
                "lng": station.station_longitude,
            })
        for hop, (start_index, end_index) in enumerate(zip(indexes, indexes[1:]), start=1):
            segment = _rows_to_shape(rows[start_index:end_index + 1])
            bus_eta_min += predict_segment_minutes(
                hop, hop + 1, hour, _path_km(segment), speed
            )
        trip_distance_km = _path_km(trip_shape) if len(trip_shape) > 1 else geodesic(
            (nearest_user_station.station_latitude, nearest_user_station.station_longitude),
            (nearest_dest_station.station_latitude, nearest_dest_station.station_longitude),
        ).km
        if bus_eta_min <= 0 and trip_distance_km > 0:
            bus_eta_min = predict_segment_minutes(10, 9, hour, trip_distance_km, speed)
    else:
        trip_distance_km = geodesic(user_location, dest_location).km
        bus_eta_min = predict_segment_minutes(10, 9, hour, trip_distance_km, speed)

    walk_km = geodesic(
        user_location,
        (nearest_user_station.station_latitude, nearest_user_station.station_longitude),
    ).km + geodesic(
        dest_location,
        (nearest_dest_station.station_latitude, nearest_dest_station.station_longitude),
    ).km
    walk_eta_min = (walk_km / WALK_KMH) * 60.0
    eta_min = max(1, int(round(bus_eta_min + walk_eta_min)))
    trip_distance_km = round(trip_distance_km, 2)
    fare_npr = _fare_npr(trip_distance_km)
    board_name = _short_place(nearest_user_station.station_english_name)
    alight_name = _short_place(nearest_dest_station.station_english_name)
    trip_title = f"{board_name} → {alight_name}"
    route_pk = route.pk if corridor else None

    response_data = {
        'my_location_name': user_point[2] if len(user_point) > 2 else userlocation,
        'my_location_lat_long': [user_location[0], user_location[1]],

        'nearest_user_station_id': nearest_user_station.station_id,
        'nearest_user_station_english_name': nearest_user_station.station_english_name,
        'nearest_user_station_lat_long': [nearest_user_station.station_latitude, nearest_user_station.station_longitude],

        'nearest_dest_station_id': nearest_dest_station.station_id,
        'nearest_dest_station_english_name': nearest_dest_station.station_english_name,
        'nearest_dest_station_lat_long': [nearest_dest_station.station_latitude, nearest_dest_station.station_longitude],

        'dest_location_name': dest_point[2] if len(dest_point) > 2 else destlocation,
        'dest_location_lat_long': [dest_location[0], dest_location[1]],

        'trip_distance_km': trip_distance_km,
        'fare_npr': fare_npr,
        'eta_min': eta_min,
        'bus_eta_min': max(1, int(round(bus_eta_min))) if bus_eta_min else 0,
        'stored_route_name': stored_route_name,
        'trip_title': trip_title,
        'uses_stored_route': uses_stored_route,
        'ride_stops': ride_stops,
        'trip_shape': trip_shape,
        'trip_brief': {
            'title': trip_title,
            'origin': board_name,
            'destination': alight_name,
            'route_pk': route_pk,
            'shape': trip_shape,
            'stops': ride_stops,
        },
        'routes_variable': routes_data,
    }

    return render(request, 'home.html', response_data)

#----------------Various API classes ----------------------#

#2. Simple Class Based Views
class StationInfoListAV(APIView):
    def get(self,request):
        try:
            queryset = StationInfo.objects.all()
        except StationInfo.DoesNotExist:
            return Response(
                {'Error': 'Station List Not Found'},
                status = status.HTTP_404_NOT_FOUND
            )
        serializer = StationInfoSerializer(queryset, many=True)
        return Response(serializer.data, status = status.HTTP_200_OK)
    
 
class StationInfoDetailAV(APIView):
    def get(self, request, pk):
        try:
            queryset = StationInfo.objects.get(pk=pk)
        except StationInfo.DoesNotExist:
            return Response(
                {'Error': 'Station Not Found'},
                status = status.HTTP_404_NOT_FOUND
            )
        serializer = StationInfoSerializer(queryset)
        return Response(serializer.data, status = status.HTTP_200_OK)

 
class RouteInfoListAV(APIView):
    def get(self,request):
        try:
            queryset = RouteInfo.objects.all()
        except RouteInfo.DoesNotExist:
            return Response(
                {'Error': 'Route List Not Found'},
                status = status.HTTP_404_NOT_FOUND
            )
        serializer = RouteInfoSerializer(queryset, many=True)
        return Response(serializer.data, status = status.HTTP_200_OK)



class RouteInfoDetailAV(APIView):
    def get(self, request, pk):
        try:
            queryset = RouteInfo.objects.get(pk=pk)
        except RouteInfo.DoesNotExist:
            return Response(
                {'Error': 'Route Currently Unavailable'},
                status = status.HTTP_404_NOT_FOUND
            )
        serializer = RouteInfoSerializer(queryset)
        return Response(serializer.data, status = status.HTTP_200_OK)
    
 
class RouteStationInfoDetailAV(APIView):
    def get(self, request, pk):
        try:
            queryset = RouteStationInfo.objects.get(pk=pk)
        except RouteStationInfo.DoesNotExist:
            return Response(
                {'Error': 'Route Station Currently Unavailable'},
                status = status.HTTP_404_NOT_FOUND
            )
        serializer = RouteStationInfoSerializer(queryset)
        return Response(serializer.data, status = status.HTTP_200_OK)




#2 Class Based Views : generics
class RouteStationInfoList1(generics.ListAPIView):
    serializer_class = RouteStationInfoSerializer

    def get_queryset(self):
        pk = self.kwargs['pk']
        return RouteStationInfo.objects.filter(route_info=pk)
    

class RouteStationInfoList2(generics.ListAPIView):
    serializer_class = RouteStationInfoSerializer

    def get_queryset(self):
        pk = self.kwargs['pk']
        return RouteStationInfo.objects.filter(station_info=pk)

class RouteStationInfoList3(generics.ListAPIView):
    serializer_class = RouteStationInfoSerializer

    def get_queryset(self):
        pk1 = self.kwargs['pk1']
        pk2 = self.kwargs['pk2']
        return RouteStationInfo.objects.filter(route_info_id=pk1, station_info_id=pk2)
