"""
Database connection and session management
"""
import mysql.connector
from mysql.connector import pooling, Error
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager
from typing import Optional

from config.config import Config
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class DatabaseManager:
    """Manages database connections and operations"""
    
    _instance = None
    _connection_pool = None
    _engine = None
    _session_factory = None
    
    def __new__(cls):
        """Singleton pattern to ensure single instance"""
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize database manager"""
        if not self._connection_pool:
            self._initialize_connection_pool()
        if not self._engine:
            self._initialize_sqlalchemy_engine()
    
    def _initialize_connection_pool(self):
        """Initialize MySQL connection pool"""
        try:
            self._connection_pool = pooling.MySQLConnectionPool(
                pool_name="akasa_pool",
                pool_size=Config.DB_CONFIG['pool_size'],
                pool_reset_session=True,
                host=Config.DB_CONFIG['host'],
                port=Config.DB_CONFIG['port'],
                database=Config.DB_CONFIG['database'],
                user=Config.DB_CONFIG['user'],
                password=Config.DB_CONFIG['password'],
                autocommit=False,
                charset='utf8mb4',
                collation='utf8mb4_unicode_ci'
            )
            logger.info("MySQL connection pool created successfully")
        except Error as e:
            logger.error(f"Error creating connection pool: {e}")
            raise
    
    def _initialize_sqlalchemy_engine(self):
        """Initialize SQLAlchemy engine for ORM operations"""
        try:
            self._engine = create_engine(
                Config.get_database_url(),
                poolclass=QueuePool,
                pool_size=Config.DB_CONFIG['pool_size'],
                max_overflow=Config.DB_CONFIG['max_overflow'],
                pool_recycle=Config.DB_CONFIG['pool_recycle'],
                pool_pre_ping=Config.DB_CONFIG['pool_pre_ping'],
                echo=False  # Set to True for SQL query logging
            )
            self._session_factory = scoped_session(
                sessionmaker(bind=self._engine, autoflush=False, autocommit=False)
            )
            logger.info("SQLAlchemy engine created successfully")
        except Exception as e:
            logger.error(f"Error creating SQLAlchemy engine: {e}")
            raise
    
    def get_connection(self):
        """
        Get a connection from the pool
        
        Returns:
            MySQL connection object
        """
        try:
            connection = self._connection_pool.get_connection()
            logger.debug("Database connection acquired from pool")
            return connection
        except Error as e:
            logger.error(f"Error getting connection from pool: {e}")
            raise
    
    @contextmanager
    def get_cursor(self, dictionary=True):
        """
        Context manager for database cursor
        
        Args:
            dictionary: Return results as dictionaries if True
            
        Yields:
            Database cursor
        """
        connection = None
        cursor = None
        try:
            connection = self.get_connection()
            cursor = connection.cursor(dictionary=dictionary)
            yield cursor
            connection.commit()
            logger.debug("Database transaction committed")
        except Error as e:
            if connection:
                connection.rollback()
                logger.warning("Database transaction rolled back")
            logger.error(f"Database error: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
                logger.debug("Database connection returned to pool")
    
    @contextmanager
    def get_session(self):
        """
        Context manager for SQLAlchemy session
        
        Yields:
            SQLAlchemy session
        """
        session = self._session_factory()
        try:
            yield session
            session.commit()
            logger.debug("SQLAlchemy session committed")
        except Exception as e:
            session.rollback()
            logger.error(f"SQLAlchemy session error: {e}")
            raise
        finally:
            session.close()
            logger.debug("SQLAlchemy session closed")
    
    def execute_query(self, query: str, params: tuple = None, fetch: bool = True):
        """
        Execute a SQL query
        
        Args:
            query: SQL query string
            params: Query parameters
            fetch: Whether to fetch results
            
        Returns:
            Query results if fetch=True, else None
        """
        with self.get_cursor() as cursor:
            cursor.execute(query, params or ())
            if fetch:
                return cursor.fetchall()
            return None
    
    def execute_many(self, query: str, data: list):
        """
        Execute a query multiple times with different data
        
        Args:
            query: SQL query string
            data: List of tuples containing query parameters
        """
        with self.get_cursor() as cursor:
            cursor.executemany(query, data)
            logger.info(f"Executed batch query with {len(data)} records")
    
    def test_connection(self) -> bool:
        """
        Test database connection
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            with self.get_cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                logger.info("Database connection test successful")
                return result is not None
        except Error as e:
            logger.error(f"Database connection test failed: {e}")
            return False
    
    def get_table_info(self, table_name: str) -> dict:
        """
        Get information about a table
        
        Args:
            table_name: Name of the table
            
        Returns:
            Dictionary with table information
        """
        try:
            # Get column information
            query = f"DESCRIBE {table_name}"
            columns = self.execute_query(query)
            
            # Get row count
            count_query = f"SELECT COUNT(*) as count FROM {table_name}"
            count_result = self.execute_query(count_query)
            row_count = count_result[0]['count'] if count_result else 0
            
            return {
                'table_name': table_name,
                'columns': columns,
                'row_count': row_count
            }
        except Error as e:
            logger.error(f"Error getting table info for {table_name}: {e}")
            return {}
    
    def close(self):
        """Close all database connections"""
        try:
            if self._session_factory:
                self._session_factory.remove()
            if self._engine:
                self._engine.dispose()
            logger.info("Database connections closed")
        except Exception as e:
            logger.error(f"Error closing database connections: {e}")


# Create singleton instance
db_manager = DatabaseManager()