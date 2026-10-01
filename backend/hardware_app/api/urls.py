from django.urls import path
from hardware_app.api.views import RealTimeUpdateAV, BackupGPSDataAV, LiveReplayAV

urlpatterns = [
    path("post_realtime_gps_data/", RealTimeUpdateAV.as_view(), name='post_realtime_gps_data'),
    path("live-replay/", LiveReplayAV.as_view(), name='live-replay'),
    path("post_to_backup_gps_data/", BackupGPSDataAV.as_view(), name='post_to_backup_gps_data')
]

  