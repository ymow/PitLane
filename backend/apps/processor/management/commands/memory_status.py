from django.core.management.base import BaseCommand
from apps.processor.monitoring import log_processor_memory_status, ProcessorMetrics
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Display current memory status of processor components'

    def add_arguments(self, parser):
        parser.add_argument(
            '--detailed',
            action='store_true',
            help='Show detailed memory breakdown and cached metrics'
        )

    def handle(self, *args, **options):
        detailed = options['detailed']
        
        if detailed:
            self.stdout.write('=== Detailed Processor Memory Status ===')
            log_processor_memory_status()
        else:
            self.stdout.write('=== Quick Memory Status ===')
            
            # Current process memory
            memory_usage = ProcessorMetrics.get_memory_usage()
            system_memory = ProcessorMetrics.get_system_memory()
            
            self.stdout.write(f"Process Memory: {memory_usage['rss_mb']:.1f}MB RSS, {memory_usage['percent']:.1f}%")
            self.stdout.write(f"System Memory: {system_memory['used_percent']:.1f}% used, {system_memory['available_gb']:.1f}GB available")
            
            # Memory usage assessment
            if memory_usage['rss_mb'] > 500:
                self.stdout.write(self.style.WARNING(f"HIGH MEMORY USAGE: {memory_usage['rss_mb']:.1f}MB"))
            elif memory_usage['rss_mb'] > 200:
                self.stdout.write(self.style.WARNING(f"Moderate memory usage: {memory_usage['rss_mb']:.1f}MB"))
            else:
                self.stdout.write(self.style.SUCCESS(f"Normal memory usage: {memory_usage['rss_mb']:.1f}MB"))
            
            if system_memory['used_percent'] > 80:
                self.stdout.write(self.style.ERROR(f"CRITICAL SYSTEM MEMORY: {system_memory['used_percent']:.1f}%"))
            elif system_memory['used_percent'] > 60:
                self.stdout.write(self.style.WARNING(f"High system memory usage: {system_memory['used_percent']:.1f}%"))
        
        self.stdout.write('Use --detailed for more information')