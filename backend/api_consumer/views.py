from django.shortcuts import render
from django.http import JsonResponse
from routeplot_app.models import StationInfo, RouteInfo, RouteStationInfo
from hardware_app.telemetry import ensure_device, record_fix


def Get_Routes(request):
    """Renders the main map interface populated with all transit corridors."""
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
    return render(request, 'home.html', {"routes_variable": routes_data})


SHAPE_POINT_NAMES = {"route point", "o"}


def _is_passenger_stop(station):
    english = (getattr(station, "station_english_name", None) or "").strip()
    nepali = (getattr(station, "station_nepali_name", None) or "").strip()
    if not english or english.lower() in SHAPE_POINT_NAMES:
        return False
    if "रुट पोइन्ट" in nepali or "रुटपोइन्ट" in nepali.replace(" ", ""):
        return False
    return True


def Get_Stations_on_Route(request, routenumber):
    """Renders passenger stops for a corridor, and the full shape for the map line."""
    route_obj = (
        RouteInfo.objects.filter(id=routenumber).first()
        or RouteInfo.objects.filter(route_id=routenumber).first()
    )
    if not route_obj:
        return render(request, 'home2.html', {'stations_variable': [], 'shape_variable': []})

    route_stations = RouteStationInfo.objects.filter(route_info=route_obj).order_by('station_order')
    station_fks = [rs.station_info_id for rs in route_stations]
    stations = StationInfo.objects.filter(id__in=station_fks)
    station_map = {s.id: s for s in stations}

    shape_points = []
    display_stops = []
    last_coord = None
    last_stop_key = None
    for rs in route_stations:
        station = station_map.get(rs.station_info_id)
        if not station or station.station_latitude is None or station.station_longitude is None:
            continue
        coord = (round(float(station.station_latitude), 6), round(float(station.station_longitude), 6))
        if coord != last_coord:
            shape_points.append({"lat": coord[0], "lng": coord[1]})
            last_coord = coord
        if not _is_passenger_stop(station):
            continue
        stop_key = (station.station_id, station.station_english_name)
        if stop_key == last_stop_key:
            continue
        last_stop_key = stop_key
        display_stops.append({
            'station_id': station.station_id,
            'station_english_name': station.station_english_name,
            'station_latitude': coord[0],
            'station_longitude': coord[1],
            'station_order': len(display_stops) + 1,
        })

    return render(request, 'home2.html', {
        'stations_variable': display_stops,
        'shape_variable': shape_points,
        'current_route': route_obj
    })


def Post_GPS_Location(request, deviceid, latitude, longitude):
    """Direct ingestion endpoint for vehicle GPS coordinates."""
    try:
        lat = float(latitude)
        lng = float(longitude)
        dev = ensure_device(deviceid)
        if dev is None:
            return JsonResponse({'error': 'Valid device id is required'}, status=400)
        record_fix(dev, lat, lng)
        return JsonResponse({
            'status': 'success',
            'device_id': dev.device_id,
            'current_latitude': lat,
            'current_longitude': lng
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


# def home(request):
#     return render(request, 'base1.html')





'''
{"my_location_name": "hanumanthan", 
"my_location_lat-long": [27.6885029, 85.3160104], 

"nearest_user_station_id": 3529, 
"nearest_user_station_english_name": "Kupandol", 
"nearest_user_station_lat-long": [27.687809242186514, 85.31633835285902], 
"nearest_dest_station_id": 1096, 

"nearest_dest_station_english_name": "Sinamangal Bus Route Point",
"nearest_dest_station_lat-long": [27.6952988, 85.3550202], 

"dest_location_name": "Tribhuvan International Airport", 
"dest_location_lat_long": [27.6939119, 85.3582197389141]
}


'''