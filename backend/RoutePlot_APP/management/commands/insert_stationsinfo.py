import csv
from django.conf import settings
from django.core.management.base import BaseCommand
from RoutePlot_APP.models import StationInfo

class Command(BaseCommand):
    help = 'Load data from Station file'

    def handle(self, *args, **kwargs):
        data_file = settings.BASE_DIR / 'Data' / 'stationinfo.csv'
        keys = ('station_id', 'station_english_name', 'station_nepali_name', 'station_latitude', 'station_longitude')

        records = []
        with open(data_file, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                records.append({k: row[k] for k in keys})

        for record in records:
            # add the data to the database
            StationInfo.objects.get_or_create(
                station_id=record['station_id'],
                station_english_name=record['station_english_name'],
                station_nepali_name=record['station_nepali_name'],
                station_latitude=record['station_latitude'],
                station_longitude=record['station_longitude']
            )
