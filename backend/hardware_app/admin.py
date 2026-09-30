from django.contrib import admin
from .models import DeviceID, RealTimeUpdate, BackupGPSData

# Register your models here.

admin.site.register(DeviceID)
admin.site.register(RealTimeUpdate)
admin.site.register(BackupGPSData)

