import csv
from django.conf import settings
from django.core.management.base import BaseCommand
from RoutePlot_APP.models import RouteInfo

class Command(BaseCommand):
    help = 'Load data from Station file'

    def handle(self, *args, **kwargs):
        data_file = settings.BASE_DIR / 'Data' / 'routeinfo.csv'
        keys = ('route_id', 'route_english_name', 'route_nepali_name', 'start', 'end')

        records = []
        with open(data_file, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                records.append({k: row[k] for k in keys})

        for record in records:
            # add the data to the database
            print("Inserting Data of Route:")
            RouteInfo.objects.get_or_create(
                route_id=record['route_id'],
                route_english_name=record['route_english_name'],
                route_nepali_name=record['route_nepali_name'],
                start=record['start'],
                end=record['end']
            )
