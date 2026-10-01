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


def nearest_station_info(request, userlocation, destlocation):
    """Geocodes origin and destination, identifies nearest transit stops, and computes fares."""
    geolocator = Nominatim(user_agent="PublicTransportAssistant/1.0")
    
    user_clean = userlocation.strip().replace(",", " ")
    dest_clean = destlocation.strip().replace(",", " ")

    userloc = None
    destloc = None

    try:
        userloc = geolocator.geocode(f"{user_clean}, Kathmandu, Nepal", timeout=6)
        if not userloc:
            userloc = geolocator.geocode(f"{user_clean}, Nepal", timeout=6)
        if not userloc:
            userloc = geolocator.geocode(user_clean, timeout=6)
    except Exception:
        userloc = None

    try:
        destloc = geolocator.geocode(f"{dest_clean}, Kathmandu, Nepal", timeout=6)
        if not destloc:
            destloc = geolocator.geocode(f"{dest_clean}, Nepal", timeout=6)
        if not destloc:
            destloc = geolocator.geocode(dest_clean, timeout=6)
    except Exception:
        destloc = None

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

    if not userloc:
        return render(request, 'home.html', {
            'error': f'Could not find coordinates for origin "{userlocation}". Please enter a recognized landmark (e.g. Kalanki, Thapathali, Ratnapark).',
            'routes_variable': routes_data,
        })

    if not destloc:
        return render(request, 'home.html', {
            'error': f'Could not find coordinates for destination "{destlocation}". Please enter a recognized landmark (e.g. Koteshwor, Airport, Lagankhel).',
            'routes_variable': routes_data,
        })

    user_location = (userloc.latitude, userloc.longitude)
    dest_location = (destloc.latitude, destloc.longitude)
        
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
        'my_location_name': userlocation,
        'my_location_lat_long': [user_location[0], user_location[1]],

        'nearest_user_station_id': nearest_user_station.station_id,
        'nearest_user_station_english_name': nearest_user_station.station_english_name,
        'nearest_user_station_lat_long': nearest_user_station_loc,

        'nearest_dest_station_id': nearest_dest_station.station_id,
        'nearest_dest_station_english_name': nearest_dest_station.station_english_name,
        'nearest_dest_station_lat_long': nearest_dest_station_loc,

        'dest_location_name': destlocation,
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
