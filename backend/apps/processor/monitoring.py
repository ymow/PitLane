"""Performance monitoring for processor components."""
import psutil
import time
import logging
from functools import wraps
from typing import Dict, Any, Callable
from django.core.cache import cache
from django.conf import settings

logger = logging.getLogger(__name__)


class ProcessorMetrics:
    """Centralized metrics collection for processor performance."""
    
    @staticmethod
    def get_memory_usage() -> Dict[str, float]:
        """Get current memory usage in MB."""
        process = psutil.Process()
        memory_info = process.memory_info()
        
        return {
            'rss_mb': memory_info.rss / (1024 * 1024),  # Resident Set Size
            'vms_mb': memory_info.vms / (1024 * 1024),  # Virtual Memory Size
            'percent': process.memory_percent()
        }
    
    @staticmethod
    def get_system_memory() -> Dict[str, float]:
        """Get system memory statistics."""
        memory = psutil.virtual_memory()
        
        return {
            'total_gb': memory.total / (1024**3),
            'available_gb': memory.available / (1024**3),
            'used_percent': memory.percent,
            'free_gb': memory.free / (1024**3)
        }
    
    @staticmethod
    def cache_metrics(key: str, value: Any, timeout: int = 300) -> None:
        """Cache metrics for monitoring dashboard."""
        try:
            cache.set(f"processor_metrics:{key}", value, timeout)
        except Exception as e:
            logger.warning(f"Failed to cache metrics {key}: {e}")
    
    @classmethod
    def log_memory_usage(cls, component: str, operation: str = "process") -> None:
        """Log current memory usage for a component."""
        memory_usage = cls.get_memory_usage()
        system_memory = cls.get_system_memory()
        
        logger.info(
            f"Memory usage for {component}.{operation}: "
            f"RSS: {memory_usage['rss_mb']:.1f}MB, "
            f"VMS: {memory_usage['vms_mb']:.1f}MB, "
            f"Process: {memory_usage['percent']:.1f}%, "
            f"System: {system_memory['used_percent']:.1f}%"
        )
        
        # Cache for monitoring
        cls.cache_metrics(f"{component}_{operation}_memory", memory_usage)
        cls.cache_metrics("system_memory", system_memory)


def monitor_memory(component: str):
    """Decorator to monitor memory usage before and after function execution."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Skip monitoring in test environment unless explicitly enabled
            if hasattr(settings, 'TESTING') and not getattr(settings, 'ENABLE_MEMORY_MONITORING', False):
                return func(*args, **kwargs)
            
            # Get memory before
            memory_before = ProcessorMetrics.get_memory_usage()
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                
                # Get memory after
                memory_after = ProcessorMetrics.get_memory_usage()
                execution_time = time.time() - start_time
                
                # Calculate memory delta
                memory_delta = {
                    'rss_mb': memory_after['rss_mb'] - memory_before['rss_mb'],
                    'vms_mb': memory_after['vms_mb'] - memory_before['vms_mb'],
                }
                
                # Log performance metrics
                logger.info(
                    f"Performance metrics for {component}.{func.__name__}: "
                    f"Time: {execution_time:.2f}s, "
                    f"Memory delta RSS: {memory_delta['rss_mb']:+.1f}MB, "
                    f"VMS: {memory_delta['vms_mb']:+.1f}MB, "
                    f"Final RSS: {memory_after['rss_mb']:.1f}MB"
                )
                
                # Cache performance data
                perf_data = {
                    'execution_time': execution_time,
                    'memory_delta': memory_delta,
                    'memory_after': memory_after,
                    'timestamp': time.time()
                }
                ProcessorMetrics.cache_metrics(f"{component}_{func.__name__}_perf", perf_data)
                
                # Alert if memory usage is high
                if memory_after['rss_mb'] > 500:  # Alert if over 500MB
                    logger.warning(
                        f"High memory usage detected in {component}.{func.__name__}: "
                        f"{memory_after['rss_mb']:.1f}MB RSS"
                    )
                
                return result
                
            except Exception as e:
                # Log error with memory state
                memory_error = ProcessorMetrics.get_memory_usage()
                logger.error(
                    f"Error in {component}.{func.__name__} after {time.time() - start_time:.2f}s: {e}. "
                    f"Memory at error: {memory_error['rss_mb']:.1f}MB RSS"
                )
                raise
                
        return wrapper
    return decorator


def monitor_spacy_model_load():
    """Special monitoring for Spacy model loading."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger.info("Loading Spacy model - monitoring memory usage...")
            
            # Memory before loading
            memory_before = ProcessorMetrics.get_memory_usage()
            system_before = ProcessorMetrics.get_system_memory()
            
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                
                # Memory after loading
                memory_after = ProcessorMetrics.get_memory_usage()
                system_after = ProcessorMetrics.get_system_memory()
                load_time = time.time() - start_time
                
                memory_increase = memory_after['rss_mb'] - memory_before['rss_mb']
                
                logger.info(
                    f"Spacy model loaded successfully in {load_time:.2f}s. "
                    f"Memory increase: {memory_increase:.1f}MB. "
                    f"Total process memory: {memory_after['rss_mb']:.1f}MB. "
                    f"System memory usage: {system_after['used_percent']:.1f}%"
                )
                
                # Cache model loading metrics
                model_metrics = {
                    'load_time': load_time,
                    'memory_increase_mb': memory_increase,
                    'total_memory_mb': memory_after['rss_mb'],
                    'system_memory_percent': system_after['used_percent'],
                    'timestamp': time.time()
                }
                ProcessorMetrics.cache_metrics("spacy_model_load", model_metrics)
                
                # Alert if model loading used excessive memory
                if memory_increase > 200:  # Alert if model uses over 200MB
                    logger.warning(
                        f"Spacy model loading used {memory_increase:.1f}MB memory. "
                        f"Consider monitoring memory usage during peak traffic."
                    )
                
                return result
                
            except Exception as e:
                logger.error(f"Failed to load Spacy model after {time.time() - start_time:.2f}s: {e}")
                raise
                
        return wrapper
    return decorator


# Django management command for memory diagnostics
def log_processor_memory_status():
    """Log current memory status for all processor components."""
    logger.info("=== Processor Memory Status ===")
    
    # Current process memory
    ProcessorMetrics.log_memory_usage("processor", "status_check")
    
    # System memory
    system_memory = ProcessorMetrics.get_system_memory()
    logger.info(
        f"System Memory: {system_memory['used_percent']:.1f}% used, "
        f"{system_memory['available_gb']:.1f}GB available"
    )
    
    # Check cached metrics
    try:
        cached_metrics = [
            "spacy_model_load",
            "entity_extractor_process_article_perf",
            "deduplicator_is_duplicate_perf",
            "categorizer_categorize_perf"
        ]
        
        for metric in cached_metrics:
            data = cache.get(f"processor_metrics:{metric}")
            if data:
                if isinstance(data, dict) and 'timestamp' in data:
                    age = time.time() - data['timestamp']
                    logger.info(f"Recent {metric}: {data} (age: {age:.0f}s)")
    
    except Exception as e:
        logger.warning(f"Could not retrieve cached metrics: {e}")
    
    logger.info("=== End Memory Status ===")