from rest_framework import serializers


class KPISerializer(serializers.Serializer):
    total_revenue = serializers.FloatField()
    total_orders = serializers.IntegerField()
    total_units = serializers.IntegerField()


class DailyRevenueSerializer(serializers.Serializer):
    date = serializers.DateField()
    revenue = serializers.FloatField()
    orders = serializers.IntegerField()
    units = serializers.IntegerField()


class TopProductSerializer(serializers.Serializer):
    name = serializers.CharField()
    category = serializers.CharField()
    total_sales = serializers.FloatField()
    units_sold = serializers.IntegerField()
    orders_count = serializers.IntegerField()


class DateRangeSerializer(serializers.Serializer):
    from_date = serializers.DateField(source='from', allow_null=True, required=False)
    to_date = serializers.DateField(source='to', allow_null=True, required=False)


class MetricsSummarySerializer(serializers.Serializer):
    kpis = KPISerializer()
    daily_revenue = DailyRevenueSerializer(many=True)
    top_products = TopProductSerializer(many=True)
    date_range = DateRangeSerializer()