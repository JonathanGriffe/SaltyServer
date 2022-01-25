from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Status


class StatusDetail(APIView):
    def get(self, request, format=None):
        status = str(Status.objects.first())
        return Response(status)
