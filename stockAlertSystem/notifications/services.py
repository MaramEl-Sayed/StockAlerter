from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
import logging
from django.utils import timezone

logger = logging.getLogger(__name__)

def send_email_notification(user_id, subject, message, alert_history_id=None):
    """Send email notification to user"""
    try:
        user = User.objects.get(id=user_id)
        
        # Check if user has email notifications enabled
        if hasattr(user, 'profile') and not user.profile.email_notifications:
            logger.info(f"Email notifications disabled for user {user.username}")
            return f"Email notifications disabled for {user.username}"
        
        # Send email
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email],
            fail_silently=False,
        )
        
        # Update notification status if alert_history_id provided
        if alert_history_id:
            from .models import Notification
            try:
                notification = Notification.objects.get(
                    alert_history_id=alert_history_id,
                    notification_type='email'
                )
                notification.status = 'sent'
                notification.sent_at = timezone.now()
                notification.save()
            except Notification.DoesNotExist:
                # Create notification record
                from alerts.models import AlertHistory
                try:
                    alert_history = AlertHistory.objects.get(id=alert_history_id)
                    Notification.objects.create(
                        user=user,
                        alert_history=alert_history,
                        notification_type='email',
                        subject=subject,
                        message=message,
                        status='sent',
                        sent_at=timezone.now()
                    )
                except AlertHistory.DoesNotExist:
                    logger.warning(f"AlertHistory {alert_history_id} not found")
        
        logger.info(f"Email sent successfully to {user.email}")
        return f"Email sent to {user.email}"
        
    except User.DoesNotExist:
        logger.error(f"User {user_id} not found")
        return f"User {user_id} not found"
    except Exception as e:
        logger.error(f"Error sending email to user {user_id}: {str(e)}")
        
        # Update notification status to failed
        if alert_history_id:
            try:
                from .models import Notification
                notification = Notification.objects.get(
                    alert_history_id=alert_history_id,
                    notification_type='email'
                )
                notification.status = 'failed'
                notification.error_message = str(e)
                notification.save()
            except:
                pass
        
        return f"Error: {str(e)}"

def send_bulk_email_notifications(notification_ids):
    """Send multiple email notifications in bulk"""
    logger.info(f"Starting bulk email send for {len(notification_ids)} notifications")
    
    success_count = 0
    error_count = 0
    
    for notification_id in notification_ids:
        try:
            from .models import Notification
            notification = Notification.objects.get(id=notification_id)
            
            if notification.status == 'pending':
                result = send_email_notification(
                    user_id=notification.user.id,
                    subject=notification.subject,
                    message=notification.message,
                    alert_history_id=notification.alert_history.id if notification.alert_history else None
                )
                
                if 'Error' not in result:
                    success_count += 1
                else:
                    error_count += 1
                    
        except Exception as e:
            error_count += 1
            logger.error(f"Error processing notification {notification_id}: {str(e)}")
    
    logger.info(f"Bulk email completed: {success_count} sent, {error_count} errors")
    return f"Bulk email: {success_count} sent, {error_count} errors"

def create_email_template(name, subject, body):
    """Create a new email template"""
    from .models import EmailTemplate
    
    template, created = EmailTemplate.objects.get_or_create(
        name=name,
        defaults={
            'subject': subject,
            'body': body,
            'is_active': True
        }
    )
    
    if not created:
        template.subject = subject
        template.body = body
        template.save()
    
    return template

def get_email_template(name):
    """Get an email template by name"""
    from .models import EmailTemplate
    
    try:
        return EmailTemplate.objects.get(name=name, is_active=True)
    except EmailTemplate.DoesNotExist:
        return None

def format_alert_email(alert, stock_price, template_name='stock_alert'):
    """Format email content for stock alerts"""
    template = get_email_template(template_name)
    
    if template:
        # Replace placeholders in template
        message = template.body.replace(
            '{symbol}', alert.stock.symbol
        ).replace(
            '{price}', str(stock_price)
        ).replace(
            '{condition}', alert.condition
        ).replace(
            '{target_price}', str(alert.target_price)
        ).replace(
            '{username}', alert.user.username
        )
        
        subject = template.subject.replace(
            '{symbol}', alert.stock.symbol
        ).replace(
            '{price}', str(stock_price)
        )
        
        return subject, message
    
    # Default template if no custom template exists
    subject = f"Stock Alert: {alert.stock.symbol} {alert.condition} ${alert.target_price}"
    message = f"""
Hello {alert.user.username},

Your stock alert has been triggered!

Stock: {alert.stock.symbol}
Current Price: ${stock_price}
Alert Condition: {alert.condition} ${alert.target_price}
Alert Type: {alert.alert_type}

This alert was set to notify you when {alert.stock.symbol} goes {alert.condition} ${alert.target_price}.

Best regards,
Stock Alert System
    """.strip()
    
    return subject, message
