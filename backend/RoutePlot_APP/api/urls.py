from django.urls import path, include
from RoutePlot_APP.api.views import (StationInfoListAV, StationInfoDetailAV,
                                     RouteInfoListAV, RouteInfoDetailAV,
                                     RouteStationInfoDetailAV,
                                     RouteStationInfoList1, RouteStationInfoList2, RouteStationInfoList3,
                                     nearest_station_info)

 
urlpatterns = [

    path('get-complete-stationinfo/', StationInfoListAV.as_view(), name='station-list'),
    path('get-particular-stationinfo/<int:pk>/', StationInfoDetailAV.as_view(), name='station-detail'),

    path('get-complete-routeinfo/', RouteInfoListAV.as_view(), name='route-list'),
    path('get-particular-routeinfo/<int:pk>/', RouteInfoDetailAV.as_view(), name='route-detail'),

    path('get-all-stations-on-routeid/<int:pk>/', RouteStationInfoList1.as_view(), name='stations-for-routeid'),
    path('get-all-routes-passing-stationid/<int:pk>/', RouteStationInfoList2.as_view(), name='routes-for-stationid'),
    path('get-routeid-stationid/<int:pk1>/<int:pk2>/', RouteStationInfoList3.as_view(), name='routeid-stationid'),
    path('get-routestationby-id/<int:pk>/', RouteStationInfoDetailAV.as_view(), name='routestation-detail'),

    path('post-to-get-nearest-station/<str:userlocation>/<str:destlocation>/', nearest_station_info, name='nearest-station')

 
]









'''

def Get_Stations(request):
    api_url = "http://localhost:8000/api/get-complete-stationinfo/"

    # Make an HTTP request to the API
    response = requests.get(api_url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the JSON response
        api_data = response.json()

        # Extract latitude and longitude from the API response
        latitude = api_data.get('station_latitude')
        longitude = api_data.get('station_longitude')

        # Create a list containing latitude and longitude
        stations_data = [{'latitude': latitude, 'longitude': longitude}]

        # Pass the data to the template
        context = {
            "stations": stations_data
        }
    else:
        context = {
            "error_message": f"Failed to fetch data from the API. Status code: {response.status_code}"
        }

    return render(request, 'home.html', context)
'''



















