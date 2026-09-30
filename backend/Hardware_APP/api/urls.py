from django.urls import path
from Hardware_APP.api.views import RealTimeUpdateAV, BackupGPSDataAV

urlpatterns = [
    path("post_realtime_gps_data/", RealTimeUpdateAV.as_view(), name='post_realtime_gps_data'),
    path("post_to_backup_gps_data/", BackupGPSDataAV.as_view(), name='post_to_backup_gps_data')
]

  