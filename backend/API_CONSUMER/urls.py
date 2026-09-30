from django.urls import path
from .views import  Post_GPS_Location, Get_Routes, Get_Stations_on_Route

urlpatterns = [
    path('', Get_Routes, name="map"),
    path('post/<int:deviceid>/<str:latitude>/<str:longitude>/', Post_GPS_Location, name="gpsdata"),
    path('post_to_get_stationsname_for_particular_route/<int:routenumber>/', Get_Stations_on_Route, name="stations-data" )
    # path('home/', home, name="home")
    
]


 

 
