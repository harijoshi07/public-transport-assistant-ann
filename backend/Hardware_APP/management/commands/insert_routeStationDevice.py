import csv
from django.conf import settings
from django.core.management.base import BaseCommand
from Hardware_APP.models import DeviceRouteStationInfo

class Command(BaseCommand):
    help = 'Load data from device1RouteStation file'

    def handle(self, *args, **kwargs):
        data_file = settings.BASE_DIR / 'Data' / 'device1RouteStation.csv'
        keys = ('route_id', 'station_id', 'device_id')

        records = []
        with open(data_file, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                records.append({k: row[k] for k in keys})

        for record in records:
            # add the data to the database
            DeviceRouteStationInfo.objects.get_or_create(
                route_information=record['route_id'],
                station_information=record['station_id'],
                device_information=record['device_id']
            )
