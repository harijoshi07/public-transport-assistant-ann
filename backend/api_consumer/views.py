from django.shortcuts import render
from django.http import JsonResponse
from routeplot_app.models import StationInfo, RouteInfo, RouteStationInfo
from hardware_app.models import DeviceID, RealTimeUpdate, BackupGPSData


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


def Get_Stations_on_Route(request, routenumber):
    """Renders stations along a selected transit route."""
    station_ids = RouteStationInfo.objects.filter(route_info=routenumber).values_list('station_info', flat=True)
    query_set = StationInfo.objects.filter(id__in=station_ids).values(
        'station_id', 'station_english_name', 'station_latitude', 'station_longitude'
    )
    context = {"stations_variable": list(query_set)}
    return render(request, 'home2.html', context)


def Post_GPS_Location(request, deviceid, latitude, longitude):
    """Direct ingestion endpoint for vehicle GPS coordinates."""
    try:
        lat = float(latitude)
        lng = float(longitude)
        dev, _ = DeviceID.objects.get_or_create(device_id=deviceid, defaults={'device_name': f"Bus-{deviceid}"})

        RealTimeUpdate.objects.create(
            current_device_id=dev,
            current_latitude=lat,
            current_longitude=lng
        )
        BackupGPSData.objects.create(
            backup_device_id=dev,
            backup_latitude=lat,
            backup_longitude=lng
        )
        return JsonResponse({
            'status': 'success',
            'device_id': deviceid,
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