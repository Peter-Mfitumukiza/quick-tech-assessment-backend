from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import CSVUploadSerializer
from .data_processor import CSVDataProcessor


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_csv(request):
    """
    CSV Upload and Processing endpoint
    POST /api/sales/upload/
    """
    serializer = CSVUploadSerializer(data=request.data)
    
    if serializer.is_valid():
        csv_file = serializer.validated_data['file']
        
        # Process the CSV file
        processor = CSVDataProcessor()
        result = processor.process_csv_file(csv_file)
        
        if result['success']:
            return Response({
                'success': True,
                'message': result['message'],
                'data': {
                    'processed_count': result['processed_count'],
                    'skipped_count': result['skipped_count'],
                    'errors': result['errors']
                }
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'message': result['message'],
                'errors': result.get('errors', [])
            }, status=status.HTTP_400_BAD_REQUEST)
    
    return Response({
        'success': False,
        'message': 'Invalid file upload',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)