from django.core.management.base import BaseCommand
from stocks.services import update_all_stock_prices, update_single_stock_price

class Command(BaseCommand):
    help = 'Update stock prices manually'

    def add_arguments(self, parser):
        parser.add_argument(
            '--symbol',
            type=str,
            help='Update specific stock symbol only',
        )

    def handle(self, *args, **options):
        if options['symbol']:
            self.stdout.write(f'Updating price for {options["symbol"]}...')
            result = update_single_stock_price(options['symbol'])
            self.stdout.write(self.style.SUCCESS(result))
        else:
            self.stdout.write('Updating all stock prices...')
            result = update_all_stock_prices()
            self.stdout.write(self.style.SUCCESS(result))
        
        self.stdout.write(self.style.SUCCESS('Price update completed'))
