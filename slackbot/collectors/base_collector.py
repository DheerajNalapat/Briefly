"""
Base collector interface for the Briefly Bot.
Defines the common interface that all news collectors must implement.
"""

import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class BaseCollector(ABC):
    """Abstract base class for all news collectors."""

    def __init__(self, name: str, enabled: bool = True):
        """
        Initialize the base collector.

        Args:
            name: Name of the collector
            enabled: Whether the collector is enabled
        """
        self.name = name
        self.enabled = enabled
        self.last_run = None
        self.run_count = 0
        self.error_count = 0
        self.success_count = 0

        logger.info(f"Initialized collector: {name}")

    @abstractmethod
    def collect(self, **kwargs) -> List[Dict[str, Any]]:
        """
        Collect news items from the source.

        Args:
            **kwargs: Additional arguments for collection

        Returns:
            List of news items as dictionaries
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if the collector is available and ready to use.

        Returns:
            True if available, False otherwise
        """
        pass

    def should_run(self, force: bool = False) -> bool:
        """
        Check if the collector should run based on its configuration.

        Args:
            force: Force run regardless of timing

        Returns:
            True if should run, False otherwise
        """
        if not self.enabled:
            return False

        if force:
            return True

        # Default implementation - can be overridden by subclasses
        return True

    def run(self, **kwargs) -> Dict[str, Any]:
        """
        Run the collector and return results with metadata.

        Args:
            **kwargs: Arguments to pass to collect method

        Returns:
            Dictionary with results and metadata
        """
        if not self.should_run():
            return {
                "success": False,
                "error": "Collector should not run at this time",
                "collector": self.name,
                "timestamp": datetime.now().isoformat(),
            }

        if not self.is_available():
            return {
                "success": False,
                "error": "Collector not available",
                "collector": self.name,
                "timestamp": datetime.now().isoformat(),
            }

        start_time = datetime.now()

        try:
            # Run the collection
            items = self.collect(**kwargs)

            # Update statistics
            self.last_run = start_time
            self.run_count += 1
            self.success_count += 1

            # Return results
            return {
                "success": True,
                "collector": self.name,
                "timestamp": start_time.isoformat(),
                "duration": (datetime.now() - start_time).total_seconds(),
                "items_count": len(items),
                "items": items,
                "metadata": {
                    "run_count": self.run_count,
                    "success_count": self.success_count,
                    "error_count": self.error_count,
                },
            }

        except Exception as e:
            # Update error statistics
            self.last_run = start_time
            self.run_count += 1
            self.error_count += 1

            logger.error(f"Error running collector {self.name}: {e}")

            return {
                "success": False,
                "error": str(e),
                "collector": self.name,
                "timestamp": start_time.isoformat(),
                "duration": (datetime.now() - start_time).total_seconds(),
                "metadata": {
                    "run_count": self.run_count,
                    "success_count": self.success_count,
                    "error_count": self.error_count,
                },
            }

    def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of the collector.

        Returns:
            Dictionary with collector status information
        """
        return {
            "name": self.name,
            "enabled": self.enabled,
            "available": self.is_available(),
            "last_run": self.last_run.isoformat() if self.last_run else None,
            "run_count": self.run_count,
            "success_count": self.success_count,
            "error_count": self.error_count,
            "success_rate": (
                (self.success_count / self.run_count * 100) if self.run_count > 0 else 0
            ),
        }

    def reset_stats(self):
        """Reset collector statistics."""
        self.run_count = 0
        self.success_count = 0
        self.error_count = 0
        self.last_run = None
        logger.info(f"Reset statistics for collector: {self.name}")

    def enable(self):
        """Enable the collector."""
        self.enabled = True
        logger.info(f"Enabled collector: {self.name}")

    def disable(self):
        """Disable the collector."""
        self.enabled = False
        logger.info(f"Disabled collector: {self.name}")


class CollectorManager:
    """Manages multiple collectors and coordinates their execution."""

    def __init__(self):
        """Initialize the collector manager."""
        self.collectors: Dict[str, BaseCollector] = {}
        logger.info("Initialized CollectorManager")

    def add_collector(self, collector: BaseCollector):
        """
        Add a collector to the manager.

        Args:
            collector: Collector instance to add
        """
        self.collectors[collector.name] = collector
        logger.info(f"Added collector: {collector.name}")

    def remove_collector(self, name: str):
        """
        Remove a collector from the manager.

        Args:
            name: Name of the collector to remove
        """
        if name in self.collectors:
            del self.collectors[name]
            logger.info(f"Removed collector: {name}")

    def get_collector(self, name: str) -> Optional[BaseCollector]:
        """
        Get a collector by name.

        Args:
            name: Name of the collector

        Returns:
            Collector instance or None if not found
        """
        return self.collectors.get(name)

    def run_collector(self, name: str, **kwargs) -> Dict[str, Any]:
        """
        Run a specific collector.

        Args:
            name: Name of the collector to run
            **kwargs: Arguments to pass to the collector

        Returns:
            Collection results
        """
        collector = self.get_collector(name)
        if not collector:
            return {
                "success": False,
                "error": f"Collector not found: {name}",
                "timestamp": datetime.now().isoformat(),
            }

        return collector.run(**kwargs)

    def run_all_collectors(self, **kwargs) -> Dict[str, Any]:
        """
        Run all enabled collectors.

        Args:
            **kwargs: Arguments to pass to all collectors

        Returns:
            Dictionary with results from all collectors
        """
        results = {}
        total_items = 0

        for name, collector in self.collectors.items():
            if collector.enabled:
                result = collector.run(**kwargs)
                results[name] = result

                if result["success"]:
                    total_items += result.get("items_count", 0)

        return {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "collectors_run": len(results),
            "total_items": total_items,
            "results": results,
        }

    def get_all_status(self) -> Dict[str, Any]:
        """
        Get status of all collectors.

        Returns:
            Dictionary with status of all collectors
        """
        return {
            name: collector.get_status() for name, collector in self.collectors.items()
        }

    def get_enabled_collectors(self) -> List[str]:
        """
        Get list of enabled collector names.

        Returns:
            List of enabled collector names
        """
        return [
            name for name, collector in self.collectors.items() if collector.enabled
        ]

    def get_available_collectors(self) -> List[str]:
        """
        Get list of available collector names.

        Returns:
            List of available collector names
        """
        return [
            name
            for name, collector in self.collectors.items()
            if collector.is_available()
        ]
