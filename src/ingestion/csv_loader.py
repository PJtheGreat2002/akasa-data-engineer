"""
CSV file loader for customer data
"""
import pandas as pd
from pathlib import Path
from typing import Optional, List, Dict
from datetime import datetime

from config.config import Config
from src.utils.logger import setup_logger
from src.utils.validators import DataValidator
from src.database.db_manager import db_manager

logger = setup_logger(__name__)


class CSVLoader:
    """Load and validate customer data from CSV files"""
    
    def __init__(self):
        self.validator = DataValidator()
        self.required_columns = ['customer_id', 'customer_name', 'mobile_number', 'region']
    
    def load_csv(self, file_path: Path) -> Optional[pd.DataFrame]:
        """
        Load CSV file into DataFrame
        
        Args:
            file_path: Path to CSV file
            
        Returns:
            DataFrame or None if error
        """
        try:
            logger.info(f"Loading CSV file: {file_path}")
            
            if not file_path.exists():
                logger.error(f"File not found: {file_path}")
                return None
            
            # Load with customer_id as string
            df = pd.read_csv(file_path, dtype={'customer_id': str})
            logger.info(f"Loaded {len(df)} rows from CSV")
            
            return df
            
        except Exception as e:
            logger.error(f"Error loading CSV file: {e}")
            return None
    
    def validate_dataframe(self, df: pd.DataFrame) -> tuple[bool, List[str]]:
        """
        Validate DataFrame structure and content
        
        Args:
            df: DataFrame to validate
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        # Check required columns
        missing_cols = set(self.required_columns) - set(df.columns)
        if missing_cols:
            errors.append(f"Missing required columns: {missing_cols}")
            return False, errors
        
        # Check for empty DataFrame
        if df.empty:
            errors.append("CSV file is empty")
            return False, errors
        
        # Validate data types and values
        for idx, row in df.iterrows():
            row_errors = []
            
            # Validate customer_id (must be non-empty string, max 25 chars)
            customer_id = str(row['customer_id']).strip()
            if not customer_id or len(customer_id) > 25:
                row_errors.append(f"Invalid customer_id: {customer_id} (must be 1-25 characters)")
            
            # Validate customer_name
            if not self.validator.validate_string(row['customer_name'], min_length=2):
                row_errors.append(f"Invalid customer_name: {row['customer_name']}")
            
            # Validate mobile_number - accept any format, just normalize
            normalized_mobile = self.validator.normalize_mobile_number(row['mobile_number'])
            if not normalized_mobile:
                row_errors.append(f"Invalid mobile_number: {row['mobile_number']} (must be 8-15 digits)")
            
            # Validate region
            if not self.validator.validate_string(row['region'], min_length=2):
                row_errors.append(f"Invalid region: {row['region']}")
            
            if row_errors:
                errors.append(f"Row {idx + 2}: {', '.join(row_errors)}")  # idx+2 because CSV has header
        
        is_valid = len(errors) == 0
        if is_valid:
            logger.info("CSV validation successful")
        else:
            logger.warning(f"CSV validation failed with {len(errors)} errors")
        
        return is_valid, errors

    def clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and normalize DataFrame
        
        Args:
            df: DataFrame to clean
            
        Returns:
            Cleaned DataFrame
        """
        logger.info("Cleaning customer data...")
        
        df_clean = df.copy()
        
        # Remove leading/trailing whitespaces
        for col in df_clean.columns:
            if df_clean[col].dtype == 'object':
                df_clean[col] = df_clean[col].str.strip()
        
        # Ensure customer_id is string and clean
        df_clean['customer_id'] = df_clean['customer_id'].astype(str).str.strip()
        
        # Normalize mobile numbers
        df_clean['mobile_number'] = df_clean['mobile_number'].apply(
            self.validator.normalize_mobile_number
        )
        
        # Remove duplicates based on customer_id
        initial_count = len(df_clean)
        df_clean = df_clean.drop_duplicates(subset=['customer_id'], keep='first')
        duplicates_removed = initial_count - len(df_clean)
        
        if duplicates_removed > 0:
            logger.warning(f"Removed {duplicates_removed} duplicate customer records")
        
        # Remove rows with invalid data
        df_clean = df_clean.dropna(subset=self.required_columns)
        
        logger.info(f"Cleaning complete. {len(df_clean)} valid records")
        
        return df_clean
    
    def load_to_database(self, df: pd.DataFrame, mode: str = 'replace') -> bool:
        """
        Load customer data into database
        
        Args:
            df: DataFrame to load
            mode: 'replace' or 'append'
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Loading {len(df)} customer records to database (mode: {mode})")
            
            if mode == 'replace':
                # Clear existing data
                delete_query = "DELETE FROM customers"
                db_manager.execute_query(delete_query, fetch=False)
                logger.info("Existing customer data cleared")
            
            # Prepare insert query
            insert_query = """
                INSERT INTO customers (customer_id, customer_name, mobile_number, region)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    customer_name = VALUES(customer_name),
                    region = VALUES(region),
                    updated_at = CURRENT_TIMESTAMP
            """
            
            # Prepare data for insertion (customer_id as string)
            data = [
                (
                    str(row['customer_id']),
                    row['customer_name'],
                    row['mobile_number'],
                    row['region']
                )
                for _, row in df.iterrows()
            ]
            
            # Execute batch insert
            db_manager.execute_many(insert_query, data)
            
            logger.info(f"Successfully loaded {len(data)} customer records")
            return True
            
        except Exception as e:
            logger.error(f"Error loading data to database: {e}")
            return False
    
    def process_csv(self, file_path: Optional[Path] = None, mode: str = 'replace') -> Dict:
        """
        Complete CSV processing pipeline
        
        Args:
            file_path: Path to CSV file (uses default if None)
            mode: Database load mode ('replace' or 'append')
            
        Returns:
            Dictionary with processing results
        """
        start_time = datetime.now()
        result = {
            'success': False,
            'records_loaded': 0,
            'errors': [],
            'duration': 0
        }
        
        try:
            # Use default path if not provided
            if file_path is None:
                file_path = Config.CUSTOMERS_CSV
            
            # Load CSV
            df = self.load_csv(file_path)
            if df is None:
                result['errors'].append("Failed to load CSV file")
                return result
            
            # Validate
            is_valid, validation_errors = self.validate_dataframe(df)
            if not is_valid:
                result['errors'].extend(validation_errors)
                logger.error(f"Validation failed: {len(validation_errors)} errors")
                return result
            
            # Clean
            df_clean = self.clean_dataframe(df)
            
            # Load to database
            if self.load_to_database(df_clean, mode=mode):
                result['success'] = True
                result['records_loaded'] = len(df_clean)
                logger.info(f"CSV processing completed successfully: {len(df_clean)} records")
            else:
                result['errors'].append("Failed to load data to database")
            
        except Exception as e:
            logger.error(f"Error in CSV processing pipeline: {e}")
            result['errors'].append(str(e))
        
        finally:
            result['duration'] = (datetime.now() - start_time).total_seconds()
        
        return result


# Create singleton instance
csv_loader = CSVLoader()