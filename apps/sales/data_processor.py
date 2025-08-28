import pandas as pd
import io
from datetime import datetime
from decimal import Decimal
from django.db import transaction
from .models import Product, Sale, DailyAggregate


class CSVDataProcessor:
    def __init__(self):
        self.errors = []
        self.processed_count = 0
        self.skipped_count = 0
    
    def process_csv_file(self, csv_file):
        """
        Main method to process uploaded CSV file
        Expected CSV format: product_name,category,price,quantity,sold_at
        """
        try:
            # Read CSV file
            csv_content = csv_file.read().decode('utf-8')
            df = pd.read_csv(io.StringIO(csv_content))
            
            # Validate required columns
            required_columns = ['product_name', 'category', 'price', 'quantity', 'sold_at']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                raise ValueError(f"Missing required columns: {missing_columns}")
            
            # Process data in transaction
            with transaction.atomic():
                self._process_rows(df)
                self._recompute_daily_aggregates()
            
            return {
                'success': True,
                'processed_count': self.processed_count,
                'skipped_count': self.skipped_count,
                'errors': self.errors,
                'message': f'Processed {self.processed_count} rows, skipped {self.skipped_count} invalid rows'
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error processing CSV: {str(e)}',
                'errors': self.errors
            }
    
    def _process_rows(self, df):
        """Process each row in the dataframe"""
        for index, row in df.iterrows():
            try:
                # Validate row data
                if not self._validate_row(row, index):
                    self.skipped_count += 1
                    continue
                
                # Get or create product
                product = self._get_or_create_product(
                    name=row['product_name'].strip(),
                    category=row.get('category', '').strip(),
                    price=Decimal(str(row['price']))
                )
                
                # Parse sold_at date
                sold_at = pd.to_datetime(row['sold_at']).date()
                
                # Create sale record
                sale = Sale.objects.create(
                    product=product,
                    quantity=int(row['quantity']),
                    price=Decimal(str(row['price'])),
                    sold_at=sold_at,
                    total=Decimal(str(row['quantity'])) * Decimal(str(row['price']))
                )
                
                self.processed_count += 1
                
            except Exception as e:
                self.errors.append(f"Row {index + 2}: {str(e)}")
                self.skipped_count += 1
    
    def _validate_row(self, row, index):
        """Validate individual row data"""
        errors_for_row = []
        
        # Check for required fields
        if pd.isna(row['product_name']) or not str(row['product_name']).strip():
            errors_for_row.append("Product name is required")
        
        # Check for negative values
        try:
            price = float(row['price'])
            if price < 0:
                errors_for_row.append("Price cannot be negative")
        except (ValueError, TypeError):
            errors_for_row.append("Invalid price format")
        
        try:
            quantity = int(row['quantity'])
            if quantity <= 0:
                errors_for_row.append("Quantity must be positive")
        except (ValueError, TypeError):
            errors_for_row.append("Invalid quantity format")
        
        # Check date format
        try:
            pd.to_datetime(row['sold_at'])
        except:
            errors_for_row.append("Invalid date format")
        
        if errors_for_row:
            self.errors.append(f"Row {index + 2}: {'; '.join(errors_for_row)}")
            return False
        
        return True
    
    def _get_or_create_product(self, name, category, price):
        """Get existing product or create new one"""
        try:
            product = Product.objects.get(name=name)
            # Update product info if needed
            if product.price != price or product.category != category:
                product.price = price
                product.category = category
                product.save()
        except Product.DoesNotExist:
            product = Product.objects.create(
                name=name,
                category=category,
                price=price
            )
        return product
    
    def _recompute_daily_aggregates(self):
        """Recompute daily aggregates from all sales data"""
        # Get all unique dates from sales
        sale_dates = Sale.objects.values_list('sold_at', flat=True).distinct()
        
        for date in sale_dates:
            # Calculate aggregates for this date
            daily_sales = Sale.objects.filter(sold_at=date)
            
            total_revenue = sum(sale.total for sale in daily_sales)
            total_orders = daily_sales.count()
            total_units = sum(sale.quantity for sale in daily_sales)
            
            # Update or create daily aggregate
            DailyAggregate.objects.update_or_create(
                date=date,
                defaults={
                    'total_revenue': total_revenue,
                    'total_orders': total_orders,
                    'total_units': total_units
                }
            )