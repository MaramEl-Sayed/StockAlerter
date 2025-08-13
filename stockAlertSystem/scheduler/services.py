from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from apscheduler.jobstores.memory import MemoryJobStore
from django.conf import settings
import logging
from datetime import datetime, timezone
import pytz

logger = logging.getLogger(__name__)

class StockScheduler:
    """
    APScheduler-based scheduler for stock price updates and alert checking
    """
    
    def __init__(self):
        # Configure job stores and executors
        jobstores = {
            'default': MemoryJobStore()
        }
        
        # Create scheduler with configuration
        self.scheduler = BackgroundScheduler(
            jobstores=jobstores,
            timezone=pytz.timezone('UTC')
        )
        
        # Setup all scheduled jobs
        self.setup_jobs()
        
        # Track if scheduler is running
        self.is_running = False
    
    def setup_jobs(self):
        """Setup all scheduled jobs for the stock system"""
        
        # Update stock prices every 5 minutes
        self.scheduler.add_job(
            self.update_stock_prices,
            IntervalTrigger(minutes=5),
            id='update_stock_prices',
            name='Update Stock Prices',
            max_instances=1,
            replace_existing=True,
            misfire_grace_time=300  # 5 minutes grace period
        )
        
        # Check alerts every 2 minutes
        self.scheduler.add_job(
            self.check_alerts,
            IntervalTrigger(minutes=2),
            id='check_alerts',
            name='Check Alerts',
            max_instances=1,
            replace_existing=True,
            misfire_grace_time=120  # 2 minutes grace period
        )
        
        # Market hours update (9:30 AM - 4:00 PM EST, weekdays only)
        # More frequent updates during trading hours
        self.scheduler.add_job(
            self.market_hours_update,
            CronTrigger(
                hour='9-16', 
                minute='*/3',  # Every 3 minutes during market hours
                day_of_week='mon-fri',
                timezone='US/Eastern'
            ),
            id='market_hours_update',
            name='Market Hours Update',
            max_instances=1,
            replace_existing=True
        )
        
        # Daily cleanup job (midnight UTC)
        self.scheduler.add_job(
            self.daily_cleanup,
            CronTrigger(hour=0, minute=0),
            id='daily_cleanup',
            name='Daily Cleanup',
            max_instances=1,
            replace_existing=True
        )
        
        logger.info("Stock scheduler jobs configured successfully")
    
    def update_stock_prices(self):
        """Update stock prices for all active stocks"""
        try:
            from stocks.services import update_all_stock_prices
            result = update_all_stock_prices()
            logger.info(f"Stock prices updated successfully: {result}")
            return result
        except Exception as e:
            logger.error(f"Error updating stock prices: {e}")
            return None
    
    def check_alerts(self):
        """Check all active alerts against current stock prices"""
        try:
            from alerts.services import check_all_alerts
            result = check_all_alerts()
            logger.info(f"Alerts checked successfully: {result}")
            return result
        except Exception as e:
            logger.error(f"Error checking alerts: {e}")
            return None
    
    def market_hours_update(self):
        """Update during market hours with higher frequency"""
        try:
            from stocks.services import update_all_stock_prices
            result = update_all_stock_prices()
            logger.info(f"Market hours update completed: {result}")
            return result
        except Exception as e:
            logger.error(f"Error in market hours update: {e}")
            return None
    
    def daily_cleanup(self):
        """Daily cleanup of old data and maintenance tasks"""
        try:
            from stocks.services import cleanup_old_prices
            from alerts.services import cleanup_old_alerts
            
            # Clean up old stock prices (keep last 30 days)
            prices_cleaned = cleanup_old_prices(days=30)
            
            # Clean up old alert history (keep last 90 days)
            alerts_cleaned = cleanup_old_alerts(days=90)
            
            logger.info(f"Daily cleanup completed - Prices: {prices_cleaned}, Alerts: {alerts_cleaned}")
            return {"prices_cleaned": prices_cleaned, "alerts_cleaned": alerts_cleaned}
        except Exception as e:
            logger.error(f"Error in daily cleanup: {e}")
            return None
    
    def start(self):
        """Start the scheduler"""
        try:
            if not self.is_running:
                self.scheduler.start()
                self.is_running = True
                logger.info("Stock scheduler started successfully")
                return True
            else:
                logger.info("Scheduler is already running")
                return True
        except Exception as e:
            logger.error(f"Error starting scheduler: {e}")
            return False
    
    def stop(self):
        """Stop the scheduler"""
        try:
            if self.is_running:
                self.scheduler.shutdown()
                self.is_running = False
                logger.info("Stock scheduler stopped successfully")
                return True
            else:
                logger.info("Scheduler is not running")
                return True
        except Exception as e:
            logger.error(f"Error stopping scheduler: {e}")
            return False
    
    def restart(self):
        """Restart the scheduler"""
        try:
            self.stop()
            self.start()
            logger.info("Stock scheduler restarted successfully")
            return True
        except Exception as e:
            logger.error(f"Error restarting scheduler: {e}")
            return False
    
    def get_jobs(self):
        """Get all scheduled jobs with detailed information"""
        jobs = []
        for job in self.scheduler.get_jobs():
            job_info = {
                'id': job.id,
                'name': job.name,
                'next_run_time': job.next_run_time,
                'trigger': str(job.trigger),
                'active': not job.pending
            }
            jobs.append(job_info)
        return jobs
    
    def pause_job(self, job_id):
        """Pause a specific job"""
        try:
            self.scheduler.pause_job(job_id)
            logger.info(f"Job {job_id} paused successfully")
            return True
        except Exception as e:
            logger.error(f"Error pausing job {job_id}: {e}")
            return False
    
    def resume_job(self, job_id):
        """Resume a specific job"""
        try:
            self.scheduler.resume_job(job_id)
            logger.info(f"Job {job_id} resumed successfully")
            return True
        except Exception as e:
            logger.error(f"Error resuming job {job_id}: {e}")
            return False
    
    def remove_job(self, job_id):
        """Remove a specific job"""
        try:
            self.scheduler.remove_job(job_id)
            logger.info(f"Job {job_id} removed successfully")
            return True
        except Exception as e:
            logger.error(f"Error removing job {job_id}: {e}")
            return False
    
    def get_scheduler_status(self):
        """Get comprehensive scheduler status"""
        return {
            'is_running': self.is_running,
            'job_count': len(self.scheduler.get_jobs()),
            'jobs': self.get_jobs(),
            'next_run_times': {
                job.id: job.next_run_time.isoformat() if job.next_run_time else None
                for job in self.scheduler.get_jobs()
            }
        }
    
    def add_custom_job(self, func, trigger, **kwargs):
        """Add a custom job to the scheduler"""
        try:
            job = self.scheduler.add_job(func, trigger, **kwargs)
            logger.info(f"Custom job added successfully: {job.id}")
            return job.id
        except Exception as e:
            logger.error(f"Error adding custom job: {e}")
            return None

# Global scheduler instance
scheduler_instance = None

def get_scheduler():
    """Get or create the global scheduler instance"""
    global scheduler_instance
    if scheduler_instance is None:
        scheduler_instance = StockScheduler()
    return scheduler_instance

def start_scheduler():
    """Start the global scheduler"""
    scheduler = get_scheduler()
    return scheduler.start()

def stop_scheduler():
    """Stop the global scheduler"""
    scheduler = get_scheduler()
    return scheduler.stop()
