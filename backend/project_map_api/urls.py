"""project_map_api URL Configuration"""
from django.contrib import admin
from django.urls import path, include

 
urlpatterns = [
    path("admin/", admin.site.urls),
    path('', include('api_consumer.urls')),
    path("api/", include('routeplot_app.api.urls')),
    path("api/", include('hardware_app.api.urls'))
]










