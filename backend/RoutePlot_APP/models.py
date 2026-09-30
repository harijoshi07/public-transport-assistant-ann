from django.db import models 

# Create your models here.

class StationInfo(models.Model):
    station_id = models.BigIntegerField()
    station_english_name = models.CharField(max_length=100)
    station_nepali_name = models.CharField(max_length=100)
    station_latitude = models.FloatField()
    station_longitude = models.FloatField()
 
    def __str__(self):
        return f"Station ID : {self.station_id}  :  {self.station_english_name}"
  
class RouteInfo(models.Model):
    route_id = models.BigIntegerField()
    route_english_name = models.CharField(max_length=250)
    route_nepali_name = models.CharField(max_length=250)
    start = models.CharField(max_length=50)
    end = models.CharField(max_length=50)

    def __str__(self):
        return f"Route ID : {self.route_id}:  {self.route_english_name}"
 

class RouteStationInfo(models.Model):
    route_info = models.ForeignKey(RouteInfo, on_delete=models.CASCADE, related_name="route_information")
    station_info = models.ForeignKey(StationInfo, on_delete=models.CASCADE, related_name="station_information")
    station_order = models.BigIntegerField()

    def __str__(self):
        return str(self.route_info) + " --> " + str(self.station_info) + " --> " + "Order : "+ str(self.station_order) 












