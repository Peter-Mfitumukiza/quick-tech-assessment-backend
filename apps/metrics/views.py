from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from .services import MetricsService
from .serializers import MetricsSummarySerializer


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def metrics_summary(request):
    """
    Dashboard Metrics Summary endpoint
    GET /api/metrics/summary/
    
    Query Parameters:
    - date_from (optional): Start date filter (YYYY-MM-DD)
    - date_to (optional): End date filter (YYYY-MM-DD)
    """
    try:
        # Get query parameters
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        
        # Get metrics data
        metrics_data = MetricsService.get_dashboard_metrics(
            date_from=date_from,
            date_to=date_to
        )
        
        # Serialize and return response
        serializer = MetricsSummarySerializer(data=metrics_data)
        if serializer.is_valid():
            return Response({
                'success': True,
                'data': serializer.validated_data
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'message': 'Error serializing metrics data',
                'errors': serializer.errors
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error retrieving metrics: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)