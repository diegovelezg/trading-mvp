"""Base connector class for data sources."""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class BaseDataConnector(ABC):
    """Base class for all data source connectors."""

    def __init__(self, name: str):
        """Initialize connector.

        Args:
            name: Name of the data source
        """
        self.name = name
        self.last_fetch = None
        self.fetch_count = 0
        self.error_count = 0

    @abstractmethod
    def fetch_data(self, **kwargs) -> List[Dict]:
        """Fetch data from the source.

        Returns:
            List of data items
        """
        pass

    @abstractmethod
    def normalize_data(self, raw_data: List[Dict]) -> List[Dict]:
        """Normalize data to standard format.

        Args:
            raw_data: Raw data from source

        Returns:
            Normalized data items
        """
        pass

    def is_rate_limited(self) -> bool:
        """Check if source is rate limited.

        Returns:
            True if rate limited, False otherwise
        """
        return False

    def get_status(self) -> Dict:
        """Get connector status.

        Returns:
            Status dictionary
        """
        return {
            "name": self.name,
            "last_fetch": self.last_fetch.isoformat() if self.last_fetch else None,
            "fetch_count": self.fetch_count,
            "error_count": self.error_count,
            "rate_limited": self.is_rate_limited()
        }
