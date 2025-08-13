from django.core.management.base import BaseCommand
from django.db import transaction
from stocks.models import Stock
from stocks.services import update_all_stock_prices
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Initialize default stocks in the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fetch-prices',
            action='store_true',
            help='Fetch current prices for all stocks after initialization',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force re-initialization even if stocks exist',
        )

    def handle(self, *args, **options):
        self.stdout.write('Starting stock initialization...')
        
        default_stocks = [
            {'symbol': 'AAPL', 'name': 'Apple Inc.', 'exchange': 'NASDAQ'},
            {'symbol': 'GOOGL', 'name': 'Alphabet Inc.', 'exchange': 'NASDAQ'},
            {'symbol': 'MSFT', 'name': 'Microsoft Corporation', 'exchange': 'NASDAQ'},
            {'symbol': 'TSLA', 'name': 'Tesla Inc.', 'exchange': 'NASDAQ'},
            {'symbol': 'AMZN', 'name': 'Amazon.com Inc.', 'exchange': 'NASDAQ'},
            {'symbol': 'META', 'name': 'Meta Platforms Inc.', 'exchange': 'NASDAQ'},
            {'symbol': 'NVDA', 'name': 'NVIDIA Corporation', 'exchange': 'NASDAQ'},
            {'symbol': 'BRK.A', 'name': 'Berkshire Hathaway Inc.', 'exchange': 'NYSE'},
            {'symbol': 'JPM', 'name': 'JPMorgan Chase & Co.', 'exchange': 'NYSE'},
            {'symbol': 'JNJ', 'name': 'Johnson & Johnson', 'exchange': 'NYSE'},
        ]
        
        created_count = 0
        updated_count = 0
        
        with transaction.atomic():
            for stock_data in default_stocks:
                stock, created = Stock.objects.get_or_create(
                    symbol=stock_data['symbol'],
                    defaults={
                        'name': stock_data['name'],
                        'exchange': stock_data['exchange'],
                        'is_active': True,
                        'currency': 'USD'
                    }
                )
                
                if created:
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'Created: {stock.symbol} - {stock.name}')
                    )
                else:
                    if options['force']:
                        # Update existing stock
                        stock.name = stock_data['name']
                        stock.exchange = stock_data['exchange']
                        stock.is_active = True
                        stock.save()
                        updated_count += 1
                        self.stdout.write(
                            self.style.WARNING(f'Updated: {stock.symbol} - {stock.name}')
                        )
                    else:
                        updated_count += 1
                        self.stdout.write(
                            self.style.SUCCESS(f'Exists: {stock.symbol} - {stock.name}')
                        )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nStock initialization completed: {created_count} created, {updated_count} existing'
            )
        )
        
        # Fetch prices if requested
        if options['fetch_prices']:
            self.stdout.write('\nFetching current stock prices...')
            try:
                task = update_all_stock_prices.delay()
                self.stdout.write(
                    self.style.SUCCESS(f'Price update task queued (ID: {task.id})')
                )
                self.stdout.write(
                    
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Failed to queue price update: {str(e)}')
                )
                self.stdout.write(
                    'You can manually update prices later with: python manage.py update_prices'
                )
        
        self.stdout.write(
            self.style.SUCCESS('\n Stock initialization completed successfully')
        )
