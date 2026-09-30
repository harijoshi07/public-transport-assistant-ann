from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from Hardware_APP.api.serializers import RealTimeUpdateSerializer, BackupGPSDataSerializer
from Hardware_APP.models import RealTimeUpdate, BackupGPSData, DeviceID

'''
def post(self, request):
        try:
            current_device_id = request.data.get('current_device_id')  # Use get to avoid KeyError
            if current_device_id is not None:
                instance = RealTimeUpdate.objects.get(current_device_id=current_device_id)
                serializer = RealTimeUpdateSerializer(instance, data=request.data)
            else:
                serializer = RealTimeUpdateSerializer(data=request.data)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except RealTimeUpdate.DoesNotExist:
            return Response({"error": "Instance not found"}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
''' 



def get_number_of_active_buses_in_particularRoute(requests):
    
    pass




class RealTimeUpdateAV(APIView):
    def post(self, request):
        try:
            current_device_id = request.data.get('current_device_id')  # Use get to avoid KeyError
            if current_device_id is not None:
                instance = RealTimeUpdate.objects.get(current_device_id=current_device_id)
                serializer = RealTimeUpdateSerializer(instance, data=request.data)
            else:
                serializer = RealTimeUpdateSerializer(data=request.data)
 
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({'Error':'Could Not Post GPS Data'}, status=status.HTTP_400_BAD_REQUEST)
            
        except RealTimeUpdate.DoesNotExist:
            return Response({"error": "Instance not found"}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):
        queryset = RealTimeUpdate.objects.all()
        serializer = RealTimeUpdateSerializer(queryset, many=True)
        return Response(serializer.data, status = status.HTTP_200_OK)
    


class BackupGPSDataAV(APIView):
    def post(self,request):
        serializer = BackupGPSDataSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'Error':'Could Not Post GPS Data'}, status=status.HTTP_400_BAD_REQUEST)
        
    def get(self, request):
        queryset = BackupGPSData.objects.all()
        serializer = BackupGPSDataSerializer(queryset, many=True)
        return Response(serializer.data, status = status.HTTP_200_OK)

















