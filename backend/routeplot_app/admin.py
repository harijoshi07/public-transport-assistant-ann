from django.contrib import admin
from routeplot_app.models import StationInfo, RouteInfo, RouteStationInfo

# Register your models here.

admin.site.register(StationInfo)
admin.site.register(RouteInfo)
admin.site.register(RouteStationInfo)
