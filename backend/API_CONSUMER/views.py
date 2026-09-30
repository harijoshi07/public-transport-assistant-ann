import requests
from django.shortcuts import render
from django.http import JsonResponse
from RoutePlot_APP.models import StationInfo


# def Get_Stations(request):
#     api_url = "http://localhost:8000/api/get-complete-stationinfo/"
#     response = requests.get(api_url) # Make an HTTP request to the API

#     if response.status_code == 200:
#         json_data = response.json()
#         stations_data = []

#         for i in range(min(20, len(json_data))): # Extract latitude and longitude from the API response
#             latitude = json_data[i]['station_latitude']
#             longitude = json_data[i]['station_longitude']
#             stations_data.append({'latitude': latitude, 'longitude': longitude})

#         context = {
#             "stations": stations_data
#         }

#     else:
#         context = {
#             "error_message": f"Failed to fetch data from the API. Status code: {response.status_code}"
#         }
#     return render(request, 'home.html', context)


def Get_Routes(request):
    api_url = "http://localhost:8000/api/get-complete-routeinfo/"
    response = requests.get(api_url)

    if response.status_code == 200:
        json_data = response.json()
        routes_data = []

        for item in json_data:  # Iterate over the list directly
            route_id = item['id']
            route_actual_id = item['route_id']
            route_name = item['route_english_name']
            route_start = item['start']
            route_end = item['end']
            
            routes_data.append({'route_id': route_id,
                                'route_actual_id': route_actual_id,
                                'route_name': route_name,
                                'route_start': route_start,
                                'route_end': route_end})
    
        context = {
            "routes_variable": routes_data
        }

    return render(request, 'home.html', context)



# def Get_Stations_on_Route(request, routenumber):
#     api_url = f"http://localhost:8000/api/get-all-stations-on-routeid/{routenumber}/"
#     response = requests.get(api_url)

#     if response.status_code == 200:
#         json_data = response.json()
#         stations_data = []

#         for i in json_data:
#             station_id = json_data[i]['station_info']
#             stations_data.append({
#                 'station_id': station_id,
#             })

#     query_set = StationInfo.objects.filter(station_data=station_id)
#     #     context = {
#     #         "stations_variable": stations_data
#     #     }
#     # else:
#     #     context = {
#     #         "stations_variable": []
#     #     }

#     return render(request, 'Elements/stations_on_route.html')


def Get_Stations_on_Route(request, routenumber):
    api_url = f"http://localhost:8000/api/get-all-stations-on-routeid/{routenumber}/"
    response = requests.get(api_url)

    if response.status_code == 200:
        json_data = response.json()
        # Extract station IDs from the JSON data
        station_ids = [item['station_info'] for item in json_data]

        # Fetch additional fields from StationInfo model
        query_set = StationInfo.objects.filter(id__in=station_ids).values(
            'station_id', 'station_english_name', 'station_latitude', 'station_longitude'
        )
        
        context = {
            "stations_variable": query_set
        }
    else:
        context = {
            "stations_variable": []
        }

    return render(request, 'home2.html', context)


def Post_GPS_Location(request, deviceid, latitude, longitude):
    latitude = float(latitude)
    longitude = float(longitude)
    api_url1 = "http://localhost:8000/api/post_realtime_gps_data/"
    api_url2 = "http://localhost:8000/api/post_to_backup_gps_data/"

    data1 = {
        'current_latitude': latitude,
        'current_longitude': longitude,
        'current_device_id': deviceid,
    }

    data2 = {
        'backup_latitude': latitude,
        'backup_longitude': longitude,
        'backup_device_id': deviceid,
    }

    try:
        response1 = requests.post(api_url1, json=data1)
        response1.raise_for_status()
        print(response1)

        response2 = requests.post(api_url2, json=data2)
        response2.raise_for_status()
        print(response2)

    except requests.exceptions.HTTPError as err:
        return JsonResponse({'error': f"HTTP error occurred: {err}"}, status=500)

    except requests.exceptions.ConnectionError as e:
        # Handle connection errors
        return JsonResponse({'error': f"Error connecting to the server: {e}"}, status=500)

    except requests.exceptions.Timeout as e:
        # Handle timeouts
        return JsonResponse({'error': f"Request timed out: {e}"}, status=500)

    except requests.exceptions.RequestException as e:
        # Handle other types of request exceptions
        return JsonResponse({'error': f"Error: {e}"}, status=500)

    # If everything is successful, return a JsonResponse
    data = {
        'backup_device_id': deviceid,
        'backup_latitude': latitude,
        'backup_longitude': longitude,
        'current_device_id': deviceid,
        'current_latitude': latitude,
        'current_longitude': longitude
    }

    return JsonResponse(data)


# def home(request):
#     return render(request, 'base1.html')





'''
{"my_location_name": "hanumanthan", 
"my_location_lat-long": [27.6885029, 85.3160104], 

"nearest_user_station_id": 3529, 
"nearest_user_station_english_name": "Kupandol", 
"nearest_user_station_lat-long": [27.687809242186514, 85.31633835285902], 
"nearest_dest_station_id": 1096, 

"nearest_dest_station_english_name": "Sinamangal Bus Route Point",
"nearest_dest_station_lat-long": [27.6952988, 85.3550202], 

"dest_location_name": "Tribhuvan International Airport", 
"dest_location_lat_long": [27.6939119, 85.3582197389141]
}


'''