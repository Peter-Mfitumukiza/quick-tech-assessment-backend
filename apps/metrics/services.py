from django.db.models import Sum, Count
from django.utils.dateparse import parse_date
from apps.sales.models import Sale, DailyAggregate, Product
from datetime import datetime, timedelta


class MetricsService:
    
    @staticmethod
    def get_dashboard_metrics(date_from=None, date_to=None):
        """
        Get comprehensive metrics for the dashboard
        """
        # Build queryset with date filters if provided
        sale_queryset = Sale.objects.all()
        aggregate_queryset = DailyAggregate.objects.all()
        
        if date_from:
            if isinstance(date_from, str):
                date_from = parse_date(date_from)
            sale_queryset = sale_queryset.filter(sold_at__gte=date_from)
            aggregate_queryset = aggregate_queryset.filter(date__gte=date_from)
        
        if date_to:
            if isinstance(date_to, str):
                date_to = parse_date(date_to)
            # Add one day to include the entire end date
            date_to_inclusive = date_to + timedelta(days=1)
            sale_queryset = sale_queryset.filter(sold_at__lt=date_to_inclusive)
            aggregate_queryset = aggregate_queryset.filter(date__lte=date_to)
        
        # Get KPIs
        kpis = MetricsService._get_kpis(sale_queryset)
        
        # Get daily revenue data
        daily_revenue = MetricsService._get_daily_revenue(aggregate_queryset)
        
        # Get top products
        top_products = MetricsService._get_top_products(sale_queryset)
        
        return {
            'kpis': kpis,
            'daily_revenue': daily_revenue,
            'top_products': top_products,
            'date_range': {
                'from': date_from.isoformat() if date_from else None,
                'to': date_to.isoformat() if date_to else None
            }
        }
    
    @staticmethod
    def _get_kpis(sale_queryset):
        """Calculate key performance indicators"""
        aggregations = sale_queryset.aggregate(
            total_revenue=Sum('total'),
            total_orders=Count('id'),
            total_units=Sum('quantity')
        )
        
        return {
            'total_revenue': float(aggregations['total_revenue'] or 0),
            'total_orders': aggregations['total_orders'] or 0,
            'total_units': aggregations['total_units'] or 0
        }
    
    @staticmethod
    def _get_daily_revenue(aggregate_queryset):
        """Get daily revenue breakdown"""
        daily_data = aggregate_queryset.order_by('date').values(
            'date', 'total_revenue', 'total_orders', 'total_units'
        )
        
        return [
            {
                'date': item['date'].isoformat(),
                'revenue': float(item['total_revenue']),
                'orders': item['total_orders'],
                'units': item['total_units']
            }
            for item in daily_data
        ]
    
    @staticmethod
    def _get_top_products(sale_queryset, limit=5):
        """Get top performing products by revenue"""
        top_products = (sale_queryset
                       .values('product__name', 'product__category')
                       .annotate(
                           total_sales=Sum('total'),
                           units_sold=Sum('quantity'),
                           orders_count=Count('id')
                       )
                       .order_by('-total_sales')[:limit])
        
        return [
            {
                'name': item['product__name'],
                'category': item['product__category'],
                'total_sales': float(item['total_sales']),
                'units_sold': item['units_sold'],
                'orders_count': item['orders_count']
            }
            for item in top_products
        ]