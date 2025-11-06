"""
Memory-based KPI calculations using Pandas DataFrames
"""
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import pandas as pd

from src.kpis.base_kpi import BaseKPI
from src.database.db_manager import db_manager
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class MemoryBasedKPIEngine:
    """Engine for in-memory KPI calculations using Pandas"""
    
    def __init__(self):
        self.customers_df = None
        self.orders_df = None
        self.last_loaded = None
        logger.info("Memory-based KPI Engine initialized")
    
    def load_data(self) -> bool:
        """Load data from database into DataFrames"""
        try:
            logger.info("Loading data into memory...")
            
            # Load customers
            customers_query = "SELECT * FROM customers"
            customers_data = db_manager.execute_query(customers_query)
            self.customers_df = pd.DataFrame(customers_data)
            
            # Load orders
            orders_query = "SELECT * FROM orders"
            orders_data = db_manager.execute_query(orders_query)
            self.orders_df = pd.DataFrame(orders_data)
            
            # Convert datetime columns
            if not self.orders_df.empty:
                self.orders_df['order_date_time'] = pd.to_datetime(self.orders_df['order_date_time'])
            
            self.last_loaded = datetime.now()
            
            logger.info(f"Data loaded: {len(self.customers_df)} customers, {len(self.orders_df)} orders")
            return True
            
        except Exception as e:
            logger.error(f"Error loading data into memory: {e}")
            return False
    
    def calculate_repeat_customers(self) -> Dict[str, Any]:
        """KPI 1: Calculate repeat customers using Pandas"""
        try:
            if self.customers_df is None or self.orders_df is None:
                self.load_data()
            
            # Merge customers and orders
            merged = self.customers_df.merge(
                self.orders_df,
                on='mobile_number',
                how='inner'
            )
            
            # Group by customer and count orders
            customer_orders = merged.groupby(['customer_id', 'customer_name']).agg({
                'order_id': 'count',
                'total_amount': 'sum'
            }).reset_index()
            
            customer_orders.columns = ['customer_id', 'customer_name', 'order_count', 'total_spent']
            
            # Convert to proper data types
            customer_orders['order_count'] = pd.to_numeric(customer_orders['order_count'], errors='coerce')
            customer_orders['total_spent'] = pd.to_numeric(customer_orders['total_spent'], errors='coerce')
            
            # Filter repeat customers (more than 1 order)
            repeat_customers = customer_orders[customer_orders['order_count'] > 1]
            repeat_customers = repeat_customers.sort_values(
                by=['order_count', 'total_spent'],
                ascending=[False, False]
            )
            
            results = repeat_customers.to_dict('records')
            
            metadata = {
                'total_repeat_customers': len(repeat_customers),
                'total_orders': int(repeat_customers['order_count'].sum()) if not repeat_customers.empty else 0,
                'total_revenue': float(repeat_customers['total_spent'].sum()) if not repeat_customers.empty else 0.0
            }
            
            logger.info(f"Memory: Repeat Customers KPI - {metadata['total_repeat_customers']} customers")
            
            return {
                'kpi_name': 'Repeat Customers',
                'data': results,
                'metadata': metadata,
                'calculated_at': datetime.now().isoformat(),
                'success': True,
                'method': 'memory'
            }
            
        except Exception as e:
            logger.error(f"Error calculating repeat customers (memory): {e}")
            return {'success': False, 'error': str(e)}
    
    def calculate_monthly_trends(self) -> Dict[str, Any]:
        """KPI 2: Calculate monthly order trends using Pandas"""
        try:
            if self.orders_df is None or self.orders_df.empty:
                self.load_data()
            
            # Extract month-year
            orders_copy = self.orders_df.copy()
            orders_copy['month_year'] = orders_copy['order_date_time'].dt.to_period('M').astype(str)
            
            # Aggregate by month
            monthly_stats = orders_copy.groupby('month_year').agg({
                'order_id': 'count',
                'total_amount': ['sum', 'mean'],
                'mobile_number': 'nunique'
            }).reset_index()
            
            monthly_stats.columns = [
                'month_year', 'total_orders', 'total_revenue',
                'avg_order_value', 'unique_customers'
            ]
            
            # Convert to proper data types
            monthly_stats['total_orders'] = pd.to_numeric(monthly_stats['total_orders'], errors='coerce')
            monthly_stats['total_revenue'] = pd.to_numeric(monthly_stats['total_revenue'], errors='coerce')
            monthly_stats['avg_order_value'] = pd.to_numeric(monthly_stats['avg_order_value'], errors='coerce')
            monthly_stats['unique_customers'] = pd.to_numeric(monthly_stats['unique_customers'], errors='coerce')
            
            monthly_stats = monthly_stats.sort_values('month_year')
            
            results = monthly_stats.to_dict('records')
            
            metadata = {
                'total_months': len(monthly_stats),
                'total_orders': int(monthly_stats['total_orders'].sum()) if not monthly_stats.empty else 0,
                'total_revenue': float(monthly_stats['total_revenue'].sum()) if not monthly_stats.empty else 0.0,
                'avg_monthly_orders': float(monthly_stats['total_orders'].mean()) if not monthly_stats.empty else 0.0
            }
            
            logger.info(f"Memory: Monthly Trends KPI - {metadata['total_months']} months")
            
            return {
                'kpi_name': 'Monthly Order Trends',
                'data': results,
                'metadata': metadata,
                'calculated_at': datetime.now().isoformat(),
                'success': True,
                'method': 'memory'
            }
            
        except Exception as e:
            logger.error(f"Error calculating monthly trends (memory): {e}")
            return {'success': False, 'error': str(e)}
    
    def calculate_regional_revenue(self) -> Dict[str, Any]:
        """KPI 3: Calculate regional revenue using Pandas"""
        try:
            if self.customers_df is None or self.orders_df is None:
                self.load_data()
            
            # Merge customers and orders
            merged = self.customers_df.merge(
                self.orders_df,
                on='mobile_number',
                how='left'
            )
            
            # Aggregate by region
            regional_stats = merged.groupby('region').agg({
                'customer_id': 'nunique',
                'order_id': 'count',
                'total_amount': ['sum', 'mean']
            }).reset_index()
            
            regional_stats.columns = [
                'region', 'customer_count', 'total_orders',
                'total_revenue', 'avg_order_value'
            ]
            
            # Convert to proper data types
            regional_stats['customer_count'] = pd.to_numeric(regional_stats['customer_count'], errors='coerce')
            regional_stats['total_orders'] = pd.to_numeric(regional_stats['total_orders'], errors='coerce')
            regional_stats['total_revenue'] = pd.to_numeric(regional_stats['total_revenue'], errors='coerce')
            regional_stats['avg_order_value'] = pd.to_numeric(regional_stats['avg_order_value'], errors='coerce')
            
            # Fill NaN values (regions with no orders)
            regional_stats['total_revenue'] = regional_stats['total_revenue'].fillna(0)
            regional_stats['avg_order_value'] = regional_stats['avg_order_value'].fillna(0)
            
            regional_stats = regional_stats.sort_values('total_revenue', ascending=False)
            
            results = regional_stats.to_dict('records')
            
            metadata = {
                'total_regions': len(regional_stats),
                'total_revenue': float(regional_stats['total_revenue'].sum()),
                'highest_revenue_region': results[0]['region'] if results else None
            }
            
            logger.info(f"Memory: Regional Revenue KPI - {metadata['total_regions']} regions")
            
            return {
                'kpi_name': 'Regional Revenue',
                'data': results,
                'metadata': metadata,
                'calculated_at': datetime.now().isoformat(),
                'success': True,
                'method': 'memory'
            }
            
        except Exception as e:
            logger.error(f"Error calculating regional revenue (memory): {e}")
            return {'success': False, 'error': str(e)}
    
    def calculate_top_customers_last_30_days(self, days: int = 30, limit: int = 10) -> Dict[str, Any]:
        """KPI 4: Calculate top customers in last N days using Pandas"""
        try:
            if self.customers_df is None or self.orders_df is None:
                self.load_data()
            
            # Filter orders from last N days
            cutoff_date = datetime.now() - timedelta(days=days)
            recent_orders = self.orders_df[self.orders_df['order_date_time'] >= cutoff_date]
            
            if recent_orders.empty:
                logger.warning(f"No orders found in last {days} days")
                return {
                    'kpi_name': 'Top Customers (Last 30 Days)',
                    'data': [],
                    'metadata': {'time_period_days': days, 'top_customer_count': 0},
                    'calculated_at': datetime.now().isoformat(),
                    'success': True,
                    'method': 'memory'
                }
            
            # Merge with customers
            merged = self.customers_df.merge(
                recent_orders,
                on='mobile_number',
                how='inner'
            )
            
            # Aggregate by customer
            customer_stats = merged.groupby(['customer_id', 'customer_name', 'region']).agg({
                'order_id': 'count',
                'total_amount': ['sum', 'mean'],
                'order_date_time': 'max'
            }).reset_index()
            
            customer_stats.columns = [
                'customer_id', 'customer_name', 'region',
                'order_count', 'total_spend', 'avg_order_value', 'last_order_date'
            ]
            
            # Convert to proper data types
            customer_stats['total_spend'] = pd.to_numeric(customer_stats['total_spend'], errors='coerce')
            customer_stats['avg_order_value'] = pd.to_numeric(customer_stats['avg_order_value'], errors='coerce')
            customer_stats['order_count'] = pd.to_numeric(customer_stats['order_count'], errors='coerce')
            
            # Remove any rows with NaN in total_spend
            customer_stats = customer_stats.dropna(subset=['total_spend'])
            
            # Get top N customers
            top_customers = customer_stats.nlargest(limit, 'total_spend')
            
            # Convert datetime to string for JSON serialization
            top_customers['last_order_date'] = top_customers['last_order_date'].astype(str)
            
            results = top_customers.to_dict('records')
            
            metadata = {
                'time_period_days': days,
                'top_customer_count': len(top_customers),
                'total_revenue_top_customers': float(top_customers['total_spend'].sum()),
                'avg_spend_top_customers': float(top_customers['total_spend'].mean())
            }
            
            logger.info(f"Memory: Top Customers KPI - {metadata['top_customer_count']} in last {days} days")
            
            return {
                'kpi_name': 'Top Customers (Last 30 Days)',
                'data': results,
                'metadata': metadata,
                'calculated_at': datetime.now().isoformat(),
                'success': True,
                'method': 'memory'
            }
            
        except Exception as e:
            logger.error(f"Error calculating top customers (memory): {e}")
            return {'success': False, 'error': str(e)}
    
    def calculate_all_kpis(self, **kwargs) -> Dict[str, Any]:
        """Calculate all KPIs using in-memory approach"""
        logger.info("Calculating all memory-based KPIs...")
        
        # Ensure data is loaded
        if self.customers_df is None or self.orders_df is None:
            if not self.load_data():
                return {'success': False, 'error': 'Failed to load data'}
        
        results = {
            'repeat_customers': self.calculate_repeat_customers(),
            'monthly_trends': self.calculate_monthly_trends(),
            'regional_revenue': self.calculate_regional_revenue(),
            'top_customers': self.calculate_top_customers_last_30_days(**kwargs)
        }
        
        logger.info("All memory-based KPIs calculated successfully")
        return results


# Create singleton instance
memory_kpi_engine = MemoryBasedKPIEngine()