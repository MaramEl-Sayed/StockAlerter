import requests
import time
import logging
from django.conf import settings
from django.core.cache import cache
from decimal import Decimal
import random
from django.utils import timezone
from datetime import timedelta

logger = logging.getLogger(__name__)

# Rate limiting: max 100 requests per minute for free tier
RATE_LIMIT_KEY = 'twelve_data_api_calls'
RATE_LIMIT_MAX = 100
RATE_LIMIT_WINDOW = 60  # seconds

def check_rate_limit():
    """Check if we're within API rate limits"""
    current_calls = cache.get(RATE_LIMIT_KEY, 0)
    if current_calls >= RATE_LIMIT_MAX:
        return False
    
    # Increment call counter
    cache.set(RATE_LIMIT_KEY, current_calls + 1, RATE_LIMIT_WINDOW)
    return True

def fetch_stock_price(symbol):
    """
    Fetch stock price from Twelve Data API with rate limiting and error handling
    """
    if not check_rate_limit():
        raise Exception("API rate limit exceeded. Please wait before making more requests.")
    
    api_key = settings.TWELVE_DATA_API_KEY
    
    url = f"https://api.twelvedata.com/price?symbol={symbol}&apikey={api_key}"
    
    try:
        # Add random delay to avoid overwhelming the API
        time.sleep(random.uniform(0.1, 0.5))
        
        response = requests.get(url, timeout=8)
        response.raise_for_status()
        
        data = response.json()
        
        if "price" in data and data["price"]:
            price = float(data["price"])
            
            # Validate price is reasonable
            if price <= 0 or price > 1000000:
                raise Exception(f"Invalid price received: ${price}")
            
            logger.info(f"Successfully fetched price for {symbol}: ${price}")
            return Decimal(str(price))
            
        elif "status" in data and data["status"] == "error":
            error_msg = data.get("message", "Unknown API error")
            logger.error(f"API error for {symbol}: {error_msg}")
            raise Exception(f"API error: {error_msg}")
            
        else:
            logger.error(f"Unexpected API response for {symbol}: {data}")
            raise Exception("Unexpected API response format")
            
    except requests.exceptions.Timeout:
        logger.error(f"Timeout fetching price for {symbol}")
        raise Exception("API request timeout")
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error for {symbol}: {str(e)}")
        raise Exception(f"Request failed: {str(e)}")
        
    except ValueError as e:
        logger.error(f"Invalid price data for {symbol}: {str(e)}")
        raise Exception("Invalid price data received")
        
    except Exception as e:
        logger.error(f"Unexpected error fetching price for {symbol}: {str(e)}")
        raise Exception(f"Failed to fetch price: {str(e)}")

def get_cached_stock_price(symbol, cache_timeout=300):
    """
    Get stock price from cache or fetch from API
    """
    cache_key = f"stock_price_{symbol}"
    cached_price = cache.get(cache_key)
    
    if cached_price is not None:
        logger.debug(f"Using cached price for {symbol}: ${cached_price}")
        return cached_price
    
    try:
        price = fetch_stock_price(symbol)
        # Cache the price for 5 minutes
        cache.set(cache_key, price, cache_timeout)
        return price
        
    except Exception as e:
        logger.error(f"Failed to fetch price for {symbol}: {str(e)}")
        raise

def batch_fetch_stock_prices(symbols, max_concurrent=5):
    """
    Fetch multiple stock prices with concurrency control
    """
    results = {}
    
    for i in range(0, len(symbols), max_concurrent):
        batch = symbols[i:i + max_concurrent]
        
        for symbol in batch:
            try:
                price = fetch_stock_price(symbol)
                results[symbol] = {'success': True, 'price': price}
            except Exception as e:
                results[symbol] = {'success': False, 'error': str(e)}
        
        # Add delay between batches to respect rate limits
        if i + max_concurrent < len(symbols):
            time.sleep(1)
    
    return results

def validate_stock_symbol(symbol):
    """
    Validate stock symbol format
    """
    if not symbol:
        return False, "Symbol cannot be empty"
    
    if not isinstance(symbol, str):
        return False, "Symbol must be a string"
    
    if len(symbol) > 10:
        return False, "Symbol too long (max 10 characters)"
    
    # Check if symbol contains only numbers (invalid)
    if symbol.isdigit():
        return False, "Symbol cannot contain only numbers"
    
    # Check for invalid characters (only alphanumeric, dots, and hyphens allowed)
    if not symbol.replace('.', '').replace('-', '').isalnum():
        return False, "Symbol contains invalid characters"
    
    return True, "Valid symbol"

def get_api_status():
    """
    Check API status and rate limit info
    """
    current_calls = cache.get(RATE_LIMIT_KEY, 0)
    remaining_calls = max(0, RATE_LIMIT_MAX - current_calls)
    
    # LocMemCache doesn't support ttl, so we'll use a different approach
    # For testing purposes, we'll return 0 for reset seconds
    try:
        reset_seconds = cache.ttl(RATE_LIMIT_KEY) if hasattr(cache, 'ttl') else 0
    except AttributeError:
        reset_seconds = 0
    
    return {
        'api_key_configured': bool(settings.TWELVE_DATA_API_KEY and 
                                 settings.TWELVE_DATA_API_KEY != 'your_actual_api_key_here'),
        'rate_limit_remaining': remaining_calls,
        'rate_limit_max': RATE_LIMIT_MAX,
        'rate_limit_reset_seconds': reset_seconds
    }

def update_all_stock_prices():
    """
    Update prices for all active stocks over 80 seconds to respect API rate limits
    Used by the APScheduler
    """
    try:
        from .models import Stock
        import time
        
        # Get all active stocks
        active_stocks = Stock.objects.filter(is_active=True)
        total_stocks = len(active_stocks)
        
        if total_stocks == 0:
            return {
                'updated_count': 0,
                'failed_count': 0,
                'total_stocks': 0,
                'timestamp': timezone.now().isoformat(),
                'message': 'No active stocks to update'
            }
        
        # Calculate delay between requests to spread over (80 seconds)
        # For 10 stocks, we'll use ~8 seconds between requests
        delay_between_requests = 8  # seconds
        
        updated_count = 0
        failed_count = 0
        
        logger.info(f"Starting staggered price update for {total_stocks} stocks over 80 seconds")
        
        for i, stock in enumerate(active_stocks):
            try:
                # Log progress
                logger.info(f"Updating stock {i+1}/{total_stocks}: {stock.symbol}")
                
                # Fetch and update price
                new_price = fetch_stock_price(stock.symbol)
                if new_price:
                    old_price = stock.price
                    stock.price = new_price
                    stock.last_updated = timezone.now()
                    stock.save()
                    
                    # Create price history record
                    from .models import StockPrice
                    StockPrice.objects.create(
                        stock=stock,
                        price=new_price
                    )
                    
                    updated_count += 1
                    logger.info(f"Updated {stock.symbol}: ${old_price} -> ${new_price}")
                else:
                    failed_count += 1
                    logger.warning(f"Failed to get price data for {stock.symbol}")
                
                # Add delay between requests, except for the last one
                if i < total_stocks - 1:
                    time.sleep(delay_between_requests)
                    
            except Exception as e:
                failed_count += 1
                logger.error(f"Error updating {stock.symbol}: {e}")
                # Continue with next stock even if this one fails
                if i < total_stocks - 1:
                    time.sleep(delay_between_requests)
                continue
        
        result = {
            'updated_count': updated_count,
            'failed_count': failed_count,
            'total_stocks': total_stocks,
            'timestamp': timezone.now().isoformat(),
            'message': f'Completed staggered update over 80 seconds'
        }
        
        logger.info(f"Stock price update completed: {updated_count} updated, {failed_count} failed")
        return result
        
    except Exception as e:
        logger.error(f"Error in update_all_stock_prices: {e}")
        return None

def cleanup_old_prices(days=30):
    """
    Clean up old stock price history records
    Used by the APScheduler for daily cleanup
    """
    try:
        from .models import StockPrice
        
        cutoff_date = timezone.now() - timedelta(days=days)
        deleted_count, _ = StockPrice.objects.filter(
            timestamp__lt=cutoff_date
        ).delete()
        
        logger.info(f"Cleaned up {deleted_count} old stock prices (older than {days} days)")
        return deleted_count
        
    except Exception as e:
        logger.error(f"Error cleaning up old prices: {e}")
        return 0

def update_single_stock_price(symbol):
    """
    Update price for a single stock
    Used by the scheduler and API endpoints
    """
    try:
        from .models import Stock
        
        # Get the stock
        try:
            stock = Stock.objects.get(symbol=symbol.upper(), is_active=True)
        except Stock.DoesNotExist:
            return f"Error: Stock {symbol} not found or inactive"
        
        # Fetch new price
        new_price = fetch_stock_price(symbol)
        
        if new_price:
            old_price = stock.price
            stock.price = new_price
            stock.last_updated = timezone.now()
            stock.save()
            
            # Create price history record
            from .models import StockPrice
            StockPrice.objects.create(
                stock=stock,
                price=new_price
            )
            
            logger.info(f"Updated {symbol}: ${old_price} -> ${new_price}")
            return f"Updated {symbol}: ${old_price} -> ${new_price}"
        
        return f"Error: Failed to fetch price for {symbol}"
        
    except Exception as e:
        error_msg = f"Error: Failed to update {symbol}: {str(e)}"
        logger.error(error_msg)
        return error_msg
