from django.db import models
from RoutePlot_APP.models import RouteInfo

# Create your models here.
 
class DeviceID(models.Model):
    route_id = models.ForeignKey(RouteInfo, on_delete=models.CASCADE, related_name='device_id')
    device_id = models.IntegerField()
    device_name = models.CharField(max_length=255)

    def __str__(self):
        return f"Device Name: {self.device_name} --> DeviceID {self.device_id} "
    

class RealTimeUpdate(models.Model):
    current_device_id = models.ForeignKey(DeviceID, on_delete =models.CASCADE, related_name="current_location")
    current_latitude = models.FloatField()
    current_longitude = models.FloatField()
    current_timestamp = models.DateTimeField(auto_now = True)
    

    def __str__(self):
        return f"DeviceID: {self.current_device_id} --> Latitude: {self.current_latitude} --> Longitude: {self.current_longitude} --> Timestamp: {self.current_timestamp}"
    


class BackupGPSData(models.Model):
    backup_device_id = models.ForeignKey(DeviceID, on_delete =models.CASCADE, related_name="backup_location")
    backup_latitude = models.FloatField()
    backup_longitude = models.FloatField()
    backup_timestamp = models.DateTimeField(auto_now_add = True)

    def __str__(self):
        return f"DeviceID: {self.backup_device_id} --> Latitude: {self.backup_latitude} --> Longitude: {self.backup_longitude} --> Timestamp: {self.backup_timestamp}"
    




















