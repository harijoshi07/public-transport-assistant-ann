import requests

api_url = "http://localhost:8000/api/post_to_backup_gps_data/"

data ={
        "backup_latitude": 27.695,
        "backup_longitude": 87.698,
        "backup_device_id": 1
    }
response = requests.post(api_url, json=data)
print(response.text)




