from django.utils import timezone
from django.core.cache import cache
from django.conf import settings
from .models import Alert, AlertHistory
from stocks.models import Stock
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

def check_all_alerts():
    """
    Check all active alerts against current stock prices
    Used by the APScheduler
    """
    try:
        # Get all active alerts
        active_alerts = Alert.objects.filter(is_active=True)
        triggered_count = 0
        checked_count = 0
        
        for alert in active_alerts:
            try:
                checked_count += 1
                
                # Get current stock price
                stock = alert.stock
                if not stock or not stock.price:
                    logger.warning(f"Alert {alert.id}: No price data for {stock.symbol if stock else 'Unknown'}")
                    continue
                
                current_price = stock.price
                is_triggered = False
                trigger_reason = ""
                
                # Check threshold alerts
                if alert.alert_type == 'threshold':
                    if alert.condition == 'above' and current_price > alert.target_price:
                        is_triggered = True
                        trigger_reason = f"Price ${current_price} above threshold ${alert.target_price}"
                    elif alert.condition == 'below' and current_price < alert.target_price:
                        is_triggered = True
                        trigger_reason = f"Price ${current_price} below threshold ${alert.target_price}"
                
                # Check duration alerts
                elif alert.alert_type == 'duration':
                    # For duration alerts, we need to check if the condition has been met for the specified duration
                    if alert.condition == 'below' and current_price < alert.target_price:
                        # Check if price has been below threshold for the required duration
                        duration_met = check_duration_condition(alert, current_price)
                        if duration_met:
                            is_triggered = True
                            trigger_reason = f"Price ${current_price} below ${alert.target_price} for {alert.duration_minutes} minutes"
                
                # If alert is triggered, create alert history record
                if is_triggered:
                    alert_history = AlertHistory.objects.create(
                        alert=alert,
                        stock_price=current_price,
                        message=trigger_reason
                    )
                    
                    # Send notification
                    send_alert_notification(alert, alert_history)
                    
                    # Update alert status to triggered
                    alert.status = 'triggered'
                    alert.save()
                    
                    triggered_count += 1
                    logger.info(f"Alert {alert.id} triggered: {trigger_reason}")
                
            except Exception as e:
                logger.error(f"Error checking alert {alert.id}: {e}")
                continue
        
        result = {
            'checked_count': checked_count,
            'triggered_count': triggered_count,
            'total_alerts': len(active_alerts),
            'timestamp': timezone.now().isoformat()
        }
        
        logger.info(f"Alert checking completed: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Error in check_all_alerts: {e}")
        return None

def check_duration_condition(alert, current_price, target_price=None):
    """
    Check if a duration condition has been met
    """
    try:
        from django.utils import timezone
        from datetime import timedelta
        
        # Use target_price parameter if provided, otherwise use alert.target_price
        threshold = target_price if target_price is not None else alert.target_price
        
        if alert.condition == 'below' and current_price < threshold:
            # Check if condition has been met for the required duration
            if hasattr(alert, 'condition_start_time') and alert.condition_start_time:
                # Check if enough time has passed
                time_elapsed = timezone.now() - alert.condition_start_time
                required_duration = timedelta(minutes=alert.duration_minutes)
                
                return time_elapsed >= required_duration
            else:
                # First time condition is met, start timing
                alert.condition_start_time = timezone.now()
                alert.save()
                return False
        else:
            # Condition not met, reset timing
            if hasattr(alert, 'condition_start_time') and alert.condition_start_time:
                alert.condition_start_time = None
                alert.save()
            return False
            
    except Exception as e:
        logger.error(f"Error checking duration condition: {e}")
        return False

def check_threshold_condition(alert, current_price, target_price):
    """
    Check if a threshold condition has been met
    """
    try:
        if alert.condition == 'above':
            return current_price > target_price
        elif alert.condition == 'below':
            return current_price < target_price
        elif alert.condition == 'equals':
            # Use tolerance for equals condition (0.01 or 1 cent)
            tolerance = Decimal('0.01')
            return abs(current_price - target_price) <= tolerance
        return False
    except Exception as e:
        logger.error(f"Error checking threshold condition: {e}")
        return False

def check_alert_condition(alert):
    """
    Check if an alert condition is met
    """
    try:
        if not alert.stock or not alert.stock.price:
            return False
        
        current_price = alert.stock.price
        
        if alert.alert_type == 'threshold':
            return check_threshold_condition(alert, current_price, alert.target_price)
        elif alert.alert_type == 'duration':
            return check_duration_condition(alert, current_price)
        
        return False
    except Exception as e:
        logger.error(f"Error checking alert condition: {e}")
        return False

def send_alert_notification(alert, alert_history):
    """
    Send notification for triggered alert
    """
    try:
        from notifications.services import send_email_notification
        
        # Prepare notification data
        subject = f"Stock Alert: {alert.stock.symbol} {alert.condition} {alert.target_price}"
        message = f"""
        Your stock alert has been triggered

        Stock: {alert.stock.symbol}
        Condition: {alert.condition} ${alert.target_price}
        Current Price: ${alert_history.stock_price}
        Triggered At: {alert_history.triggered_at}
        Reason: {alert_history.message}
        """
        
        # Send email notification directly (no Celery)
        if alert.user.email:
            result = send_email_notification(
                user_id=alert.user.id,
                subject=subject,
                message=message,
                alert_history_id=alert_history.id
            )
            logger.info(f"Email notification sent for alert {alert.id}: {result}")
        
        # Log to console for development
        logger.info(f"ALERT TRIGGERED: {subject}")
        logger.info(f"Message: {message}")
        
    except Exception as e:
        logger.error(f"Error sending alert notification: {e}")

def cleanup_old_alerts(days=90):
    """
    Clean up old triggered alerts
    Used by the APScheduler for daily cleanup
    """
    try:
        from django.utils import timezone
        from datetime import timedelta
        
        cutoff_date = timezone.now() - timedelta(days=days)
        deleted_count, _ = AlertHistory.objects.filter(
            triggered_at__lt=cutoff_date
        ).delete()
        
        logger.info(f"Cleaned up {deleted_count} old triggered alerts (older than {days} days)")
        return deleted_count
        
    except Exception as e:
        logger.error(f"Error cleaning up old alerts: {e}")
        return 0

def create_alert(user, stock_symbol, alert_type, condition, target_price, duration_minutes=None):
    """
    Create a new alert
    """
    try:
        # Validate stock exists
        try:
            stock = Stock.objects.get(symbol=stock_symbol, is_active=True)
        except Stock.DoesNotExist:
            return False, "Stock not found or inactive"
        
        # Create the alert with proper duration handling
        alert_data = {
            'user': user,
            'stock': stock,
            'alert_type': alert_type,
            'condition': condition,
            'target_price': target_price,
            'is_active': True
        }
        
        # Only add duration_minutes for duration alerts
        if alert_type == 'duration':
            if duration_minutes is None:
                alert_data['duration_minutes'] = 0
            else:
                alert_data['duration_minutes'] = duration_minutes
        else:
            alert_data['duration_minutes'] = None
        
        alert = Alert.objects.create(**alert_data)
        
        logger.info(f"Alert created successfully: {alert.id} for {stock_symbol}")
        return True, alert
        
    except Exception as e:
        logger.error(f"Error creating alert: {e}")
        return False, str(e)

def deactivate_alert(alert_id, user):
    """
    Deactivate an alert
    """
    try:
        alert = Alert.objects.get(id=alert_id, user=user)
        alert.is_active = False
        alert.save()
        
        logger.info(f"Alert {alert_id} deactivated successfully")
        return True, "Alert deactivated successfully"
        
    except Alert.DoesNotExist:
        return False, "Alert not found"
    except Exception as e:
        logger.error(f"Error deactivating alert: {e}")
        return False, str(e)
