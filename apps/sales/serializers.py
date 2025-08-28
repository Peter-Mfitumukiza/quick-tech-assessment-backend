from rest_framework import serializers
from .models import Product, Sale, DailyAggregate


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'category', 'price', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class SaleSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    
    class Meta:
        model = Sale
        fields = ['id', 'product', 'product_name', 'quantity', 'price', 'total', 'sold_at', 'created_at']
        read_only_fields = ['id', 'total', 'created_at']


class DailyAggregateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyAggregate
        fields = ['date', 'total_revenue', 'total_orders', 'total_units', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class CSVUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
    
    def validate_file(self, value):
        if not value.name.endswith('.csv'):
            raise serializers.ValidationError("Only CSV files are allowed.")
        
        # Check file size (limit to 10MB)
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError("File size cannot exceed 10MB.")
        
        return value