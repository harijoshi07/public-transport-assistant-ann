from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from hardware_app.api.serializers import BackupGPSDataSerializer
from hardware_app.models import BackupGPSData
from hardware_app.telemetry import (
    build_trip_corridor,
    clear_trip_replay,
    ensure_device,
    live_payload,
    record_fix,
    set_trip_replay,
)


class RealTimeUpdateAV(APIView):
    def post(self, request):
        try:
            dev = ensure_device(request.data.get("current_device_id"), request.data.get("route_pk"))
            if not dev:
                return Response({"error": "Valid current_device_id is required"}, status=status.HTTP_400_BAD_REQUEST)
            lat = float(request.data.get("current_latitude"))
            lng = float(request.data.get("current_longitude"))
            record_fix(dev, lat, lng)
            return Response({"status": "ok", "device_id": dev.device_id, "route_pk": dev.route_id_id}, status=status.HTTP_200_OK)
        except (TypeError, ValueError):
            return Response({"error": "Latitude and longitude are required"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):
        return Response(live_payload(request.GET.get("replay")), status=status.HTTP_200_OK)


class LiveReplayAV(APIView):
    """Remember the planned trip so the bus follows that line instead of the default."""

    def post(self, request):
        replay_id = str(request.data.get("replay_id") or "").strip()[:40]
        if not replay_id:
            return Response({"error": "replay_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        if request.data.get("reset"):
            clear_trip_replay(replay_id)
            return Response(live_payload(), status=status.HTTP_200_OK)
        corridor = build_trip_corridor(
            request.data.get("origin"),
            request.data.get("destination"),
            request.data.get("route_pk"),
            request.data.get("shape"),
            request.data.get("stops"),
        )
        if corridor is None:
            return Response({"error": "A route shape is required"}, status=status.HTTP_400_BAD_REQUEST)
        set_trip_replay(replay_id, corridor)
        return Response(live_payload(replay_id), status=status.HTTP_200_OK)


class BackupGPSDataAV(APIView):
    def post(self, request):
        try:
            device_raw = request.data.get('backup_device_id')
            dev = ensure_device(device_raw)
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
