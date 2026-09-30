from rest_framework import serializers
from Hardware_APP.models import DeviceID, RealTimeUpdate, BackupGPSData
from RoutePlot_APP.api.seriaizers import RouteInfoSerializer


class DeviceIDSerializer(serializers.ModelSerializer):
    device_id = RouteInfoSerializer(many=True, read_only=True)
    class Meta:
        model = DeviceID
        fields = '__all__'


class RealTimeUpdateSerializer(serializers.ModelSerializer):
    current_location = DeviceIDSerializer(many=True, read_only=True)
    class Meta:
        model = RealTimeUpdate
        fields = '__all__'


class BackupGPSDataSerializer(serializers.ModelSerializer):
    backup_location = DeviceIDSerializer(many=True, read_only=True)   # Returns only BackupGPSData models __str__
    class Meta:
        model = BackupGPSData
        fields = '__all__'




 

 










