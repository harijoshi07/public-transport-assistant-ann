from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from hardware_app.api.serializers import RealTimeUpdateSerializer, BackupGPSDataSerializer
from hardware_app.models import RealTimeUpdate, BackupGPSData, DeviceID
from routeplot_app.models import RouteInfo


def _get_or_create_device(device_ident):
    """Helper to resolve or auto-provision a DeviceID instance."""
    if device_ident is None:
        return None
    try:
        dev_num = int(device_ident)
    except (ValueError, TypeError):
        return None

    dev = DeviceID.objects.filter(device_id=dev_num).first() or DeviceID.objects.filter(id=dev_num).first()
    if not dev:
        default_route = RouteInfo.objects.first()
        dev = DeviceID.objects.create(
            device_id=dev_num,
            device_name=f"Bus-{dev_num}",
            route_id=default_route
        )
    return dev


class RealTimeUpdateAV(APIView):
    def post(self, request):
        try:
            device_raw = request.data.get('current_device_id')
            dev = _get_or_create_device(device_raw)
            if not dev:
                return Response({'error': 'Valid current_device_id is required'}, status=status.HTTP_400_BAD_REQUEST)

            payload = request.data.copy()
            payload['current_device_id'] = dev.id

            instance = RealTimeUpdate.objects.filter(current_device_id=dev).first()
            if instance is not None:
                serializer = RealTimeUpdateSerializer(instance, data=payload)
            else:
                serializer = RealTimeUpdateSerializer(data=payload)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):
        queryset = RealTimeUpdate.objects.all()
        serializer = RealTimeUpdateSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class BackupGPSDataAV(APIView):
    def post(self, request):
        try:
            device_raw = request.data.get('backup_device_id')
            dev = _get_or_create_device(device_raw)
            if not dev:
                return Response({'error': 'Valid backup_device_id is required'}, status=status.HTTP_400_BAD_REQUEST)

            payload = request.data.copy()
            payload['backup_device_id'] = dev.id

            serializer = BackupGPSDataSerializer(data=payload)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):
        queryset = BackupGPSData.objects.all().order_by('-backup_timestamp')[:100]
        serializer = BackupGPSDataSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
