# http://localhost:8000/api/post_realtime_gps_data/

import requests

api_url = "http://localhost:8000/api/post_realtime_gps_data/"

data = {
        "current_latitude": 27.693,
        "current_longitude": 85.3178,
        "current_device_id": 1
}
response = requests.post(api_url, json=data)
print(response.text)






















