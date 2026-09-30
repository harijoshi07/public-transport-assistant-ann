from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework import generics 

from RoutePlot_APP.models import StationInfo, RouteInfo, RouteStationInfo
from RoutePlot_APP.api.seriaizers import StationInfoSerializer, RouteInfoSerializer, RouteStationInfoSerializer

from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
 
#----------------------------------------------------------#

def nearest_station_info(request, userlocation, destlocation):
    geolocator = Nominatim(user_agent="MyStationApp")
    
    userloc = geolocator.geocode(userlocation)
    destloc = geolocator.geocode(destlocation)

    if not userloc and not destloc:
        return JsonResponse({'error': 'Invalid location'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user_location = (userloc.latitude, userloc.longitude)
        dest_location = (destloc.latitude, destloc.longitude)
    except:
        return JsonResponse({'error': 'Please Remove Comma !'}, status=status.HTTP_400_BAD_REQUEST)
        
    #calculating nearest station
    all_stations = StationInfo.objects.exclude(station_english_name='Route Point')
    try:
        nearest_user_station = min(all_stations, key=lambda station: geodesic(user_location, (station.station_latitude, station.station_longitude)).km)
        nearest_dest_station = min(all_stations, key=lambda station: geodesic(dest_location, (station.station_latitude, station.station_longitude)).km)
    except:
        return JsonResponse({'error': 'No Such Table Found For Calculating Nearest Stations'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    #Change nearest station location into lat long
    nearest_user_station_loc = (nearest_user_station.station_latitude, nearest_user_station.station_longitude)
    nearest_dest_station_loc = (nearest_dest_station.station_latitude, nearest_dest_station.station_longitude)
 
    #Return the response 
    response_data = {
        'my_location_name': userlocation,
        'my_location_lat_long': user_location,

        'nearest_user_station_id': nearest_user_station.station_id,
        'nearest_user_station_english_name': nearest_user_station.station_english_name,
        'nearest_user_station_lat_long': nearest_user_station_loc,

        'nearest_dest_station_id': nearest_dest_station.station_id,
        'nearest_dest_station_english_name': nearest_dest_station.station_english_name,
        'nearest_dest_station_lat_long': nearest_dest_station_loc,

        'dest_location_name':destlocation,
        'dest_location_lat_long': dest_location,
    
    } 

    # return JsonResponse(response_data)
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
