from django.core.management.base import BaseCommand
from apps.news.models import Article
from apps.processor.deduplicator import Deduplicator
from django.db import transaction
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Backfill SimHash for existing articles without simhash values'

    def add_arguments(self, parser):
        parser.add_argument(
            '--batch-size',
            type=int,
            default=100,
            help='Number of articles to process in each batch (default: 100)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be processed without making changes'
        )

    def handle(self, *args, **options):
        batch_size = options['batch_size']
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write('DRY RUN MODE - No changes will be made')
        
        # Get articles without simhash
        articles_without_hash = Article.objects.filter(simhash__isnull=True)
        total_count = articles_without_hash.count()
        
        if total_count == 0:
            self.stdout.write(self.style.SUCCESS('All articles already have simhash values'))
            return
        
        self.stdout.write(f'Found {total_count} articles without simhash')
        
        deduplicator = Deduplicator()
        processed = 0
        
        while processed < total_count:
            # Get next batch
            batch = list(articles_without_hash[processed:processed + batch_size])
            
            if not batch:
                break
                
            self.stdout.write(f'Processing batch {processed//batch_size + 1}: articles {processed+1}-{min(processed+len(batch), total_count)}')
            
            if not dry_run:
                with transaction.atomic():
                    for article in batch:
                        try:
                            # Compute simhash for title + body
                            content_text = f"{article.original_title} {article.original_body}"
                            simhash = deduplicator.compute_hash(content_text)
                            
                            # Update the article
                            article.simhash = simhash
                            article.save(update_fields=['simhash'])
                            
                        except Exception as e:
                            logger.error(f"Error processing article {article.id}: {e}")
                            self.stdout.write(
                                self.style.ERROR(f"Failed to process article {article.id}: {e}")
                            )
            else:
                # Dry run - just log what would be processed
                for article in batch:
                    self.stdout.write(f"Would process: {article.id} - {article.original_title[:50]}...")
            
            processed += len(batch)
            self.stdout.write(f'Processed {processed}/{total_count} articles')
        
        if dry_run:
            self.stdout.write(self.style.WARNING(f'DRY RUN: Would process {total_count} articles'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Successfully backfilled simhash for {total_count} articles'))