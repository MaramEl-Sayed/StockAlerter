from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)

class StockAlertSystemConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'stockAlertSystem'
    
    def ready(self):
        """Start scheduler when Django starts"""
        # Only run this once when Django starts
        if not self.apps.is_installed('django.contrib.admin'):
            return
        
        try:
            # Import and start the scheduler
            from scheduler.services import start_scheduler
            success = start_scheduler()
            if success:
                logger.info("Stock scheduler started successfully via Django app config")
            else:
                logger.warning("Failed to start stock scheduler via Django app config")
        except Exception as e:
            logger.error(f"Error starting scheduler in Django app config: {e}")
            # Don't let scheduler errors prevent Django from starting
