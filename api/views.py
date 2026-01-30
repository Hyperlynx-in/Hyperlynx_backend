from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny


class HealthCheckView(APIView):
    """
    Health check endpoint to verify API is running.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        return Response(
            {
                'status': 'success',
                'message': 'Hyperlynx API is running',
                'code': 200
            },
            status=status.HTTP_200_OK
        )

