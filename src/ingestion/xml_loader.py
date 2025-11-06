"""
XML file loader for order data
"""
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional, List, Dict
from datetime import datetime
import pandas as pd

from config.config import Config
from src.utils.logger import setup_logger
from src.utils.validators import DataValidator
from src.database.db_manager import db_manager

logger = setup_logger(__name__)


class XMLLoader:
    """Load and validate order data from XML files"""
    
    def __init__(self):
        self.validator = DataValidator()
        self.required_fields = [
            'order_id', 'mobile_number', 'order_date_time',
            'sku_id', 'sku_count', 'total_amount'
        ]
    
    def load_xml(self, file_path: Path) -> Optional[List[Dict]]:
        """
        Load XML file and parse into list of dictionaries
        
        Args:
            file_path: Path to XML file
            
        Returns:
            List of order dictionaries or None if error
        """
        try:
            logger.info(f"Loading XML file: {file_path}")
            
            if not file_path.exists():
                logger.error(f"File not found: {file_path}")
                return None
            
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            orders = []
            for order_elem in root.findall('order'):
                order = {}
                for field in self.required_fields:
                    elem = order_elem.find(field)
                    order[field] = elem.text if elem is not None else None
                
                orders.append(order)
            
            logger.info(f"Loaded {len(orders)} orders from XML")
            return orders
            
        except ET.ParseError as e:
            logger.error(f"XML parsing error: {e}")
            return None
        except Exception as e:
            logger.error(f"Error loading XML file: {e}")
            return None
    
    def validate_orders(self, orders: List[Dict]) -> tuple[bool, List[str]]:
        """
        Validate order data
        
        Args:
            orders: List of order dictionaries
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        if not orders:
            errors.append("No orders found in XML file")
            return False, errors
        
        for idx, order in enumerate(orders):
            row_errors = []
            
            # Check required fields
            missing_fields = [f for f in self.required_fields if f not in order or not order[f]]
            if missing_fields:
                row_errors.append(f"Missing fields: {missing_fields}")
                errors.append(f"Order {idx + 1}: {', '.join(row_errors)}")
                continue
            
            # Validate order_id (must be non-empty string, max 25 chars)
            order_id = str(order['order_id']).strip()
            if not order_id or len(order_id) > 25:
                row_errors.append(f"Invalid order_id: {order_id} (must be 1-25 characters)")
            
            # Validate mobile_number - accept any format, just normalize
            normalized_mobile = self.validator.normalize_mobile_number(order['mobile_number'])
            if not normalized_mobile:
                row_errors.append(f"Invalid mobile_number: {order['mobile_number']} (must be 8-15 digits)")
            
            # Validate order_date_time
            parsed_date = self.validator.validate_datetime(order['order_date_time'])
            if not parsed_date:
                row_errors.append(f"Invalid order_date_time: {order['order_date_time']}")
            
            # Validate sku_id
            if not self.validator.validate_string(order['sku_id'], min_length=1):
                row_errors.append(f"Invalid sku_id: {order['sku_id']}")
            
            # Validate sku_count
            if not self.validator.validate_positive_number(order['sku_count']):
                row_errors.append(f"Invalid sku_count: {order['sku_count']}")
            
            # Validate total_amount
            if not self.validator.validate_non_negative_number(order['total_amount']):
                row_errors.append(f"Invalid total_amount: {order['total_amount']}")
            
            if row_errors:
                errors.append(f"Order {idx + 1}: {', '.join(row_errors)}")
        
        is_valid = len(errors) == 0
        if is_valid:
            logger.info("XML validation successful")
        else:
            logger.warning(f"XML validation failed with {len(errors)} errors")
        
        return is_valid, errors
    
    def clean_orders(self, orders: List[Dict]) -> List[Dict]:
        """
        Clean and normalize order data
        
        Args:
            orders: List of order dictionaries
            
        Returns:
            Cleaned list of orders
        """
        logger.info("Cleaning order data...")
        
        cleaned_orders = []
        
        for order in orders:
            try:
                cleaned_order = {
                    'order_id': str(order['order_id']).strip(),  # Keep as string
                    'mobile_number': self.validator.normalize_mobile_number(order['mobile_number']),
                    'order_date_time': self.validator.validate_datetime(order['order_date_time']),
                    'sku_id': order['sku_id'].strip(),
                    'sku_count': int(order['sku_count']),
                    'total_amount': float(order['total_amount'])
                }
                
                # Only add if all fields are valid
                if all(v is not None for v in cleaned_order.values()):
                    cleaned_orders.append(cleaned_order)
                else:
                    logger.warning(f"Skipping order {order['order_id']} due to invalid data")
                    
            except Exception as e:
                logger.warning(f"Error cleaning order {order.get('order_id', 'unknown')}: {e}")
                continue
        
        # Remove duplicates based on order_id
        initial_count = len(cleaned_orders)
        seen_ids = set()
        unique_orders = []
        
        for order in cleaned_orders:
            if order['order_id'] not in seen_ids:
                seen_ids.add(order['order_id'])
                unique_orders.append(order)
        
        duplicates_removed = initial_count - len(unique_orders)
        if duplicates_removed > 0:
            logger.warning(f"Removed {duplicates_removed} duplicate order records")
        
        logger.info(f"Cleaning complete. {len(unique_orders)} valid records")
        return unique_orders
    
    def load_to_database(self, orders: List[Dict], mode: str = 'replace') -> bool:
        """
        Load order data into database
        
        Args:
            orders: List of order dictionaries
            mode: 'replace' or 'append'
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Loading {len(orders)} order records to database (mode: {mode})")
            
            if mode == 'replace':
                # Clear existing data
                delete_query = "DELETE FROM orders"
                db_manager.execute_query(delete_query, fetch=False)
                logger.info("Existing order data cleared")
            
            # Prepare insert query
            insert_query = """
                INSERT INTO orders 
                (order_id, mobile_number, order_date_time, sku_id, sku_count, total_amount)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    sku_count = VALUES(sku_count),
                    total_amount = VALUES(total_amount)
            """
            
            # Prepare data for insertion (order_id as string)
            data = [
                (
                    str(order['order_id']),  # Keep as string
                    order['mobile_number'],
                    order['order_date_time'],
                    order['sku_id'],
                    order['sku_count'],
                    order['total_amount']
                )
                for order in orders
            ]
            
            # Execute batch insert
            db_manager.execute_many(insert_query, data)
            
            logger.info(f"Successfully loaded {len(data)} order records")
            return True
            
        except Exception as e:
            logger.error(f"Error loading data to database: {e}")
            return False
    
    def process_xml(self, file_path: Optional[Path] = None, mode: str = 'replace') -> Dict:
        """
        Complete XML processing pipeline
        
        Args:
            file_path: Path to XML file (uses default if None)
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
                file_path = Config.ORDERS_XML
            
            # Load XML
            orders = self.load_xml(file_path)
            if orders is None:
                result['errors'].append("Failed to load XML file")
                return result
            
            # Validate
            is_valid, validation_errors = self.validate_orders(orders)
            if not is_valid:
                result['errors'].extend(validation_errors)
                logger.error(f"Validation failed: {len(validation_errors)} errors")
                return result
            
            # Clean
            cleaned_orders = self.clean_orders(orders)
            
            # Load to database
            if self.load_to_database(cleaned_orders, mode=mode):
                result['success'] = True
                result['records_loaded'] = len(cleaned_orders)
                logger.info(f"XML processing completed successfully: {len(cleaned_orders)} records")
            else:
                result['errors'].append("Failed to load data to database")
            
        except Exception as e:
            logger.error(f"Error in XML processing pipeline: {e}")
            result['errors'].append(str(e))
        
        finally:
            result['duration'] = (datetime.now() - start_time).total_seconds()
        
        return result


# Create singleton instance
xml_loader = XMLLoader()