from django.contrib import admin
from RoutePlot_APP.models import StationInfo, RouteInfo, RouteStationInfo

# Register your models here.

admin.site.register(StationInfo)
admin.site.register(RouteInfo)
admin.site.register(RouteStationInfo)
