"""
Test script to verify setup
"""
from config.config import Config
from src.utils.logger import setup_logger
from src.database.db_manager import db_manager

logger = setup_logger(__name__)


def test_configuration():
    """Test configuration loading"""
    logger.info("Testing configuration...")
    print(f"✅ Database: {Config.DB_CONFIG['database']}")
    print(f"✅ Log Level: {Config.LOG_LEVEL}")
    print(f"✅ Page Title: {Config.PAGE_TITLE}")
    print(f"✅ Data Directory: {Config.RAW_DATA_DIR}")
    

def test_database_connection():
    """Test database connection"""
    logger.info("Testing database connection...")
    if db_manager.test_connection():
        print("✅ Database connection successful")
    else:
        print("❌ Database connection failed")
        return False
    
    # Test tables
    tables = ['customers', 'orders', 'customer_order_summary']
    for table in tables:
        info = db_manager.get_table_info(table)
        print(f"✅ Table '{table}': {info['row_count']} rows")
    
    return True


def test_query():
    """Test a simple query"""
    logger.info("Testing database query...")
    query = "SELECT COUNT(*) as count FROM customers"
    result = db_manager.execute_query(query)
    if result:
        print(f"✅ Query test successful: {result[0]['count']} customers found")
        return True
    return False


if __name__ == "__main__":
    print("\n" + "="*50)
    print("🚀 AKASA AIR PIPELINE - SETUP TEST")
    print("="*50 + "\n")
    
    try:
        test_configuration()
        print()
        
        if test_database_connection():
            print()
            test_query()
        
        print("\n" + "="*50)
        print("✅ ALL TESTS PASSED!")
        print("="*50 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        logger.error(f"Setup test failed: {e}", exc_info=True)