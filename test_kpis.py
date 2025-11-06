"""
Test KPI calculation engines
"""
import json
from src.kpis.table_based_kpis import table_kpi_engine
from src.kpis.memory_based_kpis import memory_kpi_engine
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


def print_kpi_result(result, method=""):
    """Pretty print KPI result"""
    if result.get('success'):
        print(f"✅ {result.get('kpi_name', 'KPI')} ({method})")
        
        # Print metadata
        metadata = result.get('metadata', result)
        for key, value in metadata.items():
            if key not in ['data', 'kpi_name', 'description', 'calculated_at', 'success', 'method']:
                print(f"   {key}: {value}")
        
        # Print sample data
        data = result.get('data', [])
        if data:
            print(f"   Sample records: {min(3, len(data))} of {len(data)}")
            for record in data[:3]:
                print(f"      {record}")
    else:
        print(f"❌ Failed: {result.get('error')}")
    print()


def test_table_based_kpis():
    """Test table-based KPIs"""
    print("\n" + "="*60)
    print("TABLE-BASED KPIs (SQL)")
    print("="*60 + "\n")
    
    # Test individual KPIs
    print("1. Repeat Customers:")
    result = table_kpi_engine.calculate_kpi('repeat_customers')
    print_kpi_result(result, "SQL")
    
    print("2. Monthly Trends:")
    result = table_kpi_engine.calculate_kpi('monthly_trends')
    print_kpi_result(result, "SQL")
    
    print("3. Regional Revenue:")
    result = table_kpi_engine.calculate_kpi('regional_revenue')
    print_kpi_result(result, "SQL")
    
    print("4. Top Customers (Last 30 Days):")
    result = table_kpi_engine.calculate_kpi('top_customers', days=30, limit=10)
    print_kpi_result(result, "SQL")


def test_memory_based_kpis():
    """Test memory-based KPIs"""
    print("\n" + "="*60)
    print("MEMORY-BASED KPIs (Pandas)")
    print("="*60 + "\n")
    
    # Load data first
    print("Loading data into memory...")
    memory_kpi_engine.load_data()
    print()
    
    print("1. Repeat Customers:")
    result = memory_kpi_engine.calculate_repeat_customers()
    print_kpi_result(result, "Pandas")
    
    print("2. Monthly Trends:")
    result = memory_kpi_engine.calculate_monthly_trends()
    print_kpi_result(result, "Pandas")
    
    print("3. Regional Revenue:")
    result = memory_kpi_engine.calculate_regional_revenue()
    print_kpi_result(result, "Pandas")
    
    print("4. Top Customers (Last 30 Days):")
    result = memory_kpi_engine.calculate_top_customers_last_30_days(days=30, limit=10)
    print_kpi_result(result, "Pandas")


def test_all_kpis():
    """Test calculating all KPIs at once"""
    print("\n" + "="*60)
    print("CALCULATE ALL KPIs AT ONCE")
    print("="*60 + "\n")
    
    print("Table-based (SQL):")
    table_results = table_kpi_engine.calculate_all_kpis()
    print(f"✅ Calculated {len(table_results)} KPIs\n")
    
    print("Memory-based (Pandas):")
    memory_results = memory_kpi_engine.calculate_all_kpis()
    print(f"✅ Calculated {len(memory_results)} KPIs\n")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 TESTING KPI ENGINES")
    print("="*60)
    
    try:
        test_table_based_kpis()
        test_memory_based_kpis()
        test_all_kpis()
        
        print("="*60)
        print("✅ ALL KPI TESTS COMPLETED!")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        logger.error(f"KPI test failed: {e}", exc_info=True)