"""
Test data loaders
"""
from src.ingestion.csv_loader import csv_loader
from src.ingestion.xml_loader import xml_loader
from src.database.db_manager import db_manager
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


def test_csv_loader():
    """Test CSV loader"""
    print("\n" + "="*50)
    print("Testing CSV Loader")
    print("="*50)
    
    result = csv_loader.process_csv()
    
    if result['success']:
        print(f"✅ CSV loaded successfully")
        print(f"   Records loaded: {result['records_loaded']}")
        print(f"   Duration: {result['duration']:.2f}s")
    else:
        print(f"❌ CSV loading failed")
        for error in result['errors']:
            print(f"   Error: {error}")
    
    return result['success']


def test_xml_loader():
    """Test XML loader"""
    print("\n" + "="*50)
    print("Testing XML Loader")
    print("="*50)
    
    result = xml_loader.process_xml()
    
    if result['success']:
        print(f"✅ XML loaded successfully")
        print(f"   Records loaded: {result['records_loaded']}")
        print(f"   Duration: {result['duration']:.2f}s")
    else:
        print(f"❌ XML loading failed")
        for error in result['errors']:
            print(f"   Error: {error}")
    
    return result['success']


def verify_data():
    """Verify data in database"""
    print("\n" + "="*50)
    print("Verifying Data in Database")
    print("="*50)
    
    # Check customers
    customer_query = "SELECT COUNT(*) as count FROM customers"
    customer_result = db_manager.execute_query(customer_query)
    print(f"✅ Customers table: {customer_result[0]['count']} records")
    
    # Check orders
    order_query = "SELECT COUNT(*) as count FROM orders"
    order_result = db_manager.execute_query(order_query)
    print(f"✅ Orders table: {order_result[0]['count']} records")
    
    # Sample customer data
    sample_customer = db_manager.execute_query("SELECT * FROM customers LIMIT 1")
    print(f"\nSample customer: {sample_customer[0]}")
    
    # Sample order data
    sample_order = db_manager.execute_query("SELECT * FROM orders LIMIT 1")
    print(f"Sample order: {sample_order[0]}")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 TESTING DATA LOADERS")
    print("="*60)
    
    try:
        csv_success = test_csv_loader()
        xml_success = test_xml_loader()
        
        if csv_success and xml_success:
            verify_data()
            
            print("\n" + "="*60)
            print("✅ ALL LOADER TESTS PASSED!")
            print("="*60 + "\n")
        else:
            print("\n" + "="*60)
            print("❌ SOME TESTS FAILED")
            print("="*60 + "\n")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        logger.error(f"Loader test failed: {e}", exc_info=True)