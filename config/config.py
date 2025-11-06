"""
Application configuration management
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration"""
    
    # Base paths
    BASE_DIR = Path(__file__).resolve().parent.parent
    DATA_DIR = BASE_DIR / 'data'
    RAW_DATA_DIR = DATA_DIR / 'raw'
    PROCESSED_DATA_DIR = DATA_DIR / 'processed'
    LOG_DIR = BASE_DIR / 'logs'
    
    # Database configuration
    DB_CONFIG = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': int(os.getenv('DB_PORT', 3306)),
        'database': os.getenv('DB_NAME', 'akasa_db'),
        'user': os.getenv('DB_USER', 'akasa_user'),
        'password': os.getenv('DB_PASSWORD', 'akasa_pass'),
        'pool_size': int(os.getenv('DB_POOL_SIZE', 5)),
        'max_overflow': int(os.getenv('DB_MAX_OVERFLOW', 10)),
        'pool_recycle': 3600,
        'pool_pre_ping': True
    }
    
    # Application settings
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    TIMEZONE = os.getenv('TIMEZONE', 'UTC')
    
    # Streamlit settings
    PAGE_TITLE = os.getenv('PAGE_TITLE', 'Akasa Air Analytics')
    PAGE_ICON = os.getenv('PAGE_ICON', '✈️')
    AUTO_REFRESH_INTERVAL = int(os.getenv('AUTO_REFRESH_INTERVAL', 300))
    CACHE_TTL = int(os.getenv('CACHE_TTL', 600))
    
    # Feature flags
    ENABLE_AUTO_REFRESH = os.getenv('ENABLE_AUTO_REFRESH', 'true').lower() == 'true'
    ENABLE_FILE_UPLOAD = os.getenv('ENABLE_FILE_UPLOAD', 'true').lower() == 'true'
    ENABLE_MANUAL_REFRESH = os.getenv('ENABLE_MANUAL_REFRESH', 'true').lower() == 'true'
    ENABLE_EXPORT = os.getenv('ENABLE_EXPORT', 'true').lower() == 'true'
    
    # File paths
    CUSTOMERS_CSV = RAW_DATA_DIR / 'customers.csv'
    ORDERS_XML = RAW_DATA_DIR / 'orders.xml'
    
    @classmethod
    def ensure_directories(cls):
        """Create necessary directories if they don't exist"""
        cls.DATA_DIR.mkdir(exist_ok=True)
        cls.RAW_DATA_DIR.mkdir(exist_ok=True)
        cls.PROCESSED_DATA_DIR.mkdir(exist_ok=True)
        cls.LOG_DIR.mkdir(exist_ok=True)
    
    @classmethod
    def get_database_url(cls):
        """Get SQLAlchemy database URL"""
        return (
            f"mysql+pymysql://{cls.DB_CONFIG['user']}:{cls.DB_CONFIG['password']}"
            f"@{cls.DB_CONFIG['host']}:{cls.DB_CONFIG['port']}/{cls.DB_CONFIG['database']}"
        )

# Initialize directories on import
Config.ensure_directories()