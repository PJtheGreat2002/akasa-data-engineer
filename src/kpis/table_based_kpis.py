"""
Table-based KPI calculations using SQL queries
"""
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import pandas as pd

from src.kpis.base_kpi import BaseKPI
from src.database.db_manager import db_manager
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class RepeatCustomersKPI(BaseKPI):
    """KPI 1: Customers with more than one order"""
    
    def __init__(self):
        super().__init__(
            name="Repeat Customers",
            description="Customers who have placed more than one order"
        )
    
    def calculate(self, **kwargs) -> Dict[str, Any]:
        """Calculate repeat customers using SQL"""
        try:
            query = """
                SELECT 
                    c.customer_id,
                    c.customer_name,
                    COUNT(o.order_id) as order_count,
                    SUM(o.total_amount) as total_spent
                FROM customers c
                INNER JOIN orders o ON c.mobile_number = o.mobile_number
                GROUP BY c.customer_id, c.customer_name
                HAVING COUNT(o.order_id) > 1
                ORDER BY order_count DESC, total_spent DESC
            """
            
            results = db_manager.execute_query(query)
            
            # Convert to DataFrame for better handling
            df = pd.DataFrame(results)
            
            metadata = {
                'total_repeat_customers': len(df),
                'total_orders': int(df['order_count'].sum()) if not df.empty else 0,
                'total_revenue': float(df['total_spent'].sum()) if not df.empty else 0.0
            }
            
            logger.info(f"Repeat Customers KPI: {metadata['total_repeat_customers']} customers found")
            
            return self._format_result(results, metadata)
            
        except Exception as e:
            return self._format_error(e)


class MonthlyOrderTrendsKPI(BaseKPI):
    """KPI 2: Total orders and revenue aggregated by month"""
    
    def __init__(self):
        super().__init__(
            name="Monthly Order Trends",
            description="Orders and revenue aggregated by month"
        )
    
    def calculate(self, **kwargs) -> Dict[str, Any]:
        """Calculate monthly trends using SQL"""
        try:
            query = """
                SELECT 
                    DATE_FORMAT(order_date_time, '%Y-%m') as month_year,
                    COUNT(order_id) as total_orders,
                    SUM(total_amount) as total_revenue,
                    AVG(total_amount) as avg_order_value,
                    COUNT(DISTINCT mobile_number) as unique_customers
                FROM orders
                GROUP BY DATE_FORMAT(order_date_time, '%Y-%m')
                ORDER BY month_year ASC
            """
            
            results = db_manager.execute_query(query)
            
            df = pd.DataFrame(results)
            
            metadata = {
                'total_months': len(df),
                'total_orders': int(df['total_orders'].sum()) if not df.empty else 0,
                'total_revenue': float(df['total_revenue'].sum()) if not df.empty else 0.0,
                'avg_monthly_orders': float(df['total_orders'].mean()) if not df.empty else 0.0
            }
            
            logger.info(f"Monthly Trends KPI: {metadata['total_months']} months analyzed")
            
            return self._format_result(results, metadata)
            
        except Exception as e:
            return self._format_error(e)


class RegionalRevenueKPI(BaseKPI):
    """KPI 3: Revenue aggregated by customer region"""
    
    def __init__(self):
        super().__init__(
            name="Regional Revenue",
            description="Total revenue by customer region"
        )
    
    def calculate(self, **kwargs) -> Dict[str, Any]:
        """Calculate regional revenue using SQL"""
        try:
            query = """
                SELECT 
                    c.region,
                    COUNT(DISTINCT c.customer_id) as customer_count,
                    COUNT(o.order_id) as total_orders,
                    SUM(o.total_amount) as total_revenue,
                    AVG(o.total_amount) as avg_order_value
                FROM customers c
                LEFT JOIN orders o ON c.mobile_number = o.mobile_number
                GROUP BY c.region
                ORDER BY total_revenue DESC
            """
            
            results = db_manager.execute_query(query)
            
            df = pd.DataFrame(results)
            
            metadata = {
                'total_regions': len(df),
                'total_revenue': float(df['total_revenue'].sum()) if not df.empty else 0.0,
                'highest_revenue_region': results[0]['region'] if results else None
            }
            
            logger.info(f"Regional Revenue KPI: {metadata['total_regions']} regions analyzed")
            
            return self._format_result(results, metadata)
            
        except Exception as e:
            return self._format_error(e)


class TopCustomersLast30DaysKPI(BaseKPI):
    """KPI 4: Top 10 customers by spend in last 30 days"""
    
    def __init__(self):
        super().__init__(
            name="Top Customers (Last 30 Days)",
            description="Top 10 customers by spending in the last 30 days"
        )
    
    def calculate(self, days: int = 30, limit: int = 10, **kwargs) -> Dict[str, Any]:
        """
        Calculate top customers using SQL
        
        Args:
            days: Number of days to look back (default: 30)
            limit: Number of top customers to return (default: 10)
        """
        try:
            query = """
                SELECT 
                    c.customer_id,
                    c.customer_name,
                    c.region,
                    COUNT(o.order_id) as order_count,
                    SUM(o.total_amount) as total_spend,
                    AVG(o.total_amount) as avg_order_value,
                    MAX(o.order_date_time) as last_order_date
                FROM customers c
                INNER JOIN orders o ON c.mobile_number = o.mobile_number
                WHERE o.order_date_time >= DATE_SUB(NOW(), INTERVAL %s DAY)
                GROUP BY c.customer_id, c.customer_name, c.region
                ORDER BY total_spend DESC
                LIMIT %s
            """
            
            results = db_manager.execute_query(query, (days, limit))
            
            df = pd.DataFrame(results)
            
            metadata = {
                'time_period_days': days,
                'top_customer_count': len(df),
                'total_revenue_top_customers': float(df['total_spend'].sum()) if not df.empty else 0.0,
                'avg_spend_top_customers': float(df['total_spend'].mean()) if not df.empty else 0.0
            }
            
            logger.info(f"Top Customers KPI: {metadata['top_customer_count']} customers in last {days} days")
            
            return self._format_result(results, metadata)
            
        except Exception as e:
            return self._format_error(e)


class TableBasedKPIEngine:
    """Engine to manage all table-based KPI calculations"""
    
    def __init__(self):
        self.kpis = {
            'repeat_customers': RepeatCustomersKPI(),
            'monthly_trends': MonthlyOrderTrendsKPI(),
            'regional_revenue': RegionalRevenueKPI(),
            'top_customers': TopCustomersLast30DaysKPI()
        }
        logger.info("Table-based KPI Engine initialized")
    
    def calculate_kpi(self, kpi_name: str, **kwargs) -> Dict[str, Any]:
        """
        Calculate a specific KPI
        
        Args:
            kpi_name: Name of the KPI to calculate
            **kwargs: Additional parameters for KPI calculation
            
        Returns:
            KPI result dictionary
        """
        if kpi_name not in self.kpis:
            return {
                'success': False,
                'error': f"Unknown KPI: {kpi_name}. Available: {list(self.kpis.keys())}"
            }
        
        return self.kpis[kpi_name].calculate(**kwargs)
    
    def calculate_all_kpis(self, **kwargs) -> Dict[str, Any]:
        """
        Calculate all KPIs
        
        Returns:
            Dictionary with all KPI results
        """
        logger.info("Calculating all table-based KPIs...")
        
        results = {}
        for kpi_name, kpi in self.kpis.items():
            results[kpi_name] = kpi.calculate(**kwargs)
        
        logger.info("All table-based KPIs calculated successfully")
        return results
    
    def get_kpi_list(self) -> list:
        """Get list of available KPIs"""
        return [
            {
                'name': kpi.name,
                'key': key,
                'description': kpi.description
            }
            for key, kpi in self.kpis.items()
        ]


# Create singleton instance
table_kpi_engine = TableBasedKPIEngine()