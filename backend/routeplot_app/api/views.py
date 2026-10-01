import math
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
 
#----------------------------------------------------------#

def search_stations_autocomplete(request):
    """Fast autocomplete endpoint for transit stops and landmarks."""
    query = request.GET.get('q', '').strip()
    if len(query) < 2:
        return JsonResponse({'results': []})

    stations = StationInfo.objects.filter(
        station_english_name__icontains=query
    ).exclude(station_english_name='Route Point').values(
        'station_id', 'station_english_name', 'station_latitude', 'station_longitude'
    )[:12]

    results = []
    seen_names = set()
    for s in stations:
        clean_name = s['station_english_name'].strip()
        if clean_name and clean_name.lower() not in seen_names:
            seen_names.add(clean_name.lower())
            results.append({
                'id': s['station_id'],
                'name': clean_name,
                'lat': s['station_latitude'],
                'lng': s['station_longitude'],
            })
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
        nearest_user_station = min(all_stations, key=lambda s: geodesic(user_location, (s.station_latitude, s.station_longitude)).km)
        nearest_dest_station = min(all_stations, key=lambda s: geodesic(dest_location, (s.station_latitude, s.station_longitude)).km)
    except Exception:
        return render(request, 'home.html', {
            'error': 'Station data not found. Please ensure database seeders have run.',
            'routes_variable': routes_data,
        })

    nearest_user_station_loc = [nearest_user_station.station_latitude, nearest_user_station.station_longitude]
    nearest_dest_station_loc = [nearest_dest_station.station_latitude, nearest_dest_station.station_longitude]
 
    trip_distance_km = round(geodesic(user_location, dest_location).km, 2)
    if trip_distance_km <= 5.0:
        fare_npr = 20
    else:
        extra_km = trip_distance_km - 5.0
        fare_npr = 20 + int(math.ceil(extra_km / 5.0)) * 5

    response_data = {
        'my_location_name': user_point[2] if len(user_point) > 2 else userlocation,
        'my_location_lat_long': [user_location[0], user_location[1]],

        'nearest_user_station_id': nearest_user_station.station_id,
        'nearest_user_station_english_name': nearest_user_station.station_english_name,
        'nearest_user_station_lat_long': nearest_user_station_loc,

        'nearest_dest_station_id': nearest_dest_station.station_id,
        'nearest_dest_station_english_name': nearest_dest_station.station_english_name,
        'nearest_dest_station_lat_long': nearest_dest_station_loc,

        'dest_location_name': dest_point[2] if len(dest_point) > 2 else destlocation,
        'dest_location_lat_long': [dest_location[0], dest_location[1]],

        'trip_distance_km': trip_distance_km,
        'fare_npr': fare_npr,
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
