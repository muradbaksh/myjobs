from rest_framework.views import APIView
from rest_framework.response import Response


class HealthCheckAPIView(APIView):
    permission_classes = []
    def get(self, request):
        return Response({"status": "healthy"})