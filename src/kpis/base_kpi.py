"""
Base KPI class for common functionality
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime
import pandas as pd

from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class BaseKPI(ABC):
    """Base class for all KPI calculations"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.last_calculated = None
        self.last_result = None
    
    @abstractmethod
    def calculate(self, **kwargs) -> Dict[str, Any]:
        """
        Calculate the KPI
        
        Returns:
            Dictionary containing KPI results and metadata
        """
        pass
    
    def get_result(self) -> Optional[Dict[str, Any]]:
        """Get the last calculated result"""
        return self.last_result
    
    def _format_result(self, data: Any, metadata: Dict = None) -> Dict[str, Any]:
        """
        Format KPI result with metadata
        
        Args:
            data: KPI calculation result
            metadata: Additional metadata
            
        Returns:
            Formatted result dictionary
        """
        result = {
            'kpi_name': self.name,
            'description': self.description,
            'data': data,
            'calculated_at': datetime.now().isoformat(),
            'success': True
        }
        
        if metadata:
            result.update(metadata)
        
        self.last_calculated = datetime.now()
        self.last_result = result
        
        return result
    
    def _format_error(self, error: Exception) -> Dict[str, Any]:
        """
        Format error result
        
        Args:
            error: Exception object
            
        Returns:
            Error result dictionary
        """
        logger.error(f"Error calculating {self.name}: {error}")
        
        return {
            'kpi_name': self.name,
            'description': self.description,
            'data': None,
            'calculated_at': datetime.now().isoformat(),
            'success': False,
            'error': str(error)
        }