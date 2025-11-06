"""
Common validation utilities
"""
import re
from typing import Any, Optional
from datetime import datetime
import pytz

from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class DataValidator:
    """Data validation utilities"""
    
    @staticmethod
    def validate_mobile_number(mobile: str) -> bool:
        """
        Validate mobile number format (accepts any numeric format)
        
        Args:
            mobile: Mobile number string
            
        Returns:
            True if valid, False otherwise
        """
        if not mobile:
            return False
        
        # Remove all non-digit characters
        cleaned = re.sub(r'[^\d]', '', str(mobile).strip())
        
        # Check if it's a valid length (8-15 digits to support international numbers)
        return 8 <= len(cleaned) <= 15
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        if not email:
            return False
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, str(email).strip()))
    
    @staticmethod
    def validate_positive_number(value: Any) -> bool:
        """Validate if value is a positive number"""
        try:
            return float(value) > 0
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_non_negative_number(value: Any) -> bool:
        """Validate if value is a non-negative number"""
        try:
            return float(value) >= 0
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_datetime(dt_string: str, format: str = None) -> Optional[datetime]:
        """
        Validate and parse datetime string
        
        Args:
            dt_string: Datetime string
            format: Expected datetime format (optional)
            
        Returns:
            Parsed datetime object or None if invalid
        """
        if not dt_string:
            return None
        
        formats = [format] if format else [
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d',
            '%d-%m-%Y',
            '%d/%m/%Y'
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(str(dt_string).strip(), fmt)
            except ValueError:
                continue
        
        logger.warning(f"Could not parse datetime: {dt_string}")
        return None
    
    @staticmethod
    def normalize_mobile_number(mobile: str) -> Optional[str]:
        """
        Normalize mobile number to clean format
        
        Args:
            mobile: Mobile number string
            
        Returns:
            Normalized mobile number or None if invalid
        """
        if not mobile:
            return None
        
        # Remove all non-digit characters except +
        cleaned = re.sub(r'[^\d+]', '', str(mobile).strip())
        
        # If it's just digits, keep as is
        # If it has +, keep the +
        if not cleaned:
            return None
        
        # Basic validation: should have at least 8 digits
        digit_count = len(re.sub(r'[^\d]', '', cleaned))
        if digit_count < 8:
            logger.debug(f"Mobile number too short: {mobile}")
            return None
        
        return cleaned
    
    @staticmethod
    def validate_string(value: Any, min_length: int = 1, max_length: int = 255) -> bool:
        """
        Validate string value
        
        Args:
            value: String value to validate
            min_length: Minimum string length
            max_length: Maximum string length
            
        Returns:
            True if valid, False otherwise
        """
        if not value:
            return False
        
        str_value = str(value).strip()
        return min_length <= len(str_value) <= max_length