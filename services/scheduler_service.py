from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
from models.receipt import Receipt
from services.email_service import EmailService
from app import db
from environment import CURRENCY
import os
import logging

logger = logging.getLogger(__name__)

class SchedulerService:
    """Service for managing scheduled tasks"""
    
    def __init__(self, app=None):
        self.scheduler = BackgroundScheduler()
        self.email_service = EmailService()
        self.app = app
        
        # Get email recipients from environment
        recipients_str = os.getenv('ALERT_EMAIL_RECIPIENTS', '')
        self.alert_recipients = [email.strip() for email in recipients_str.split(',') if email.strip()]
        
        # Get days to check (comma-separated, e.g., "0,1,2,3,4" for Mon-Fri)
        check_days_str = os.getenv('CHECK_DAYS', '0,1,2,3,4,5,6')  # All days by default
        self.check_days = [int(day.strip()) for day in check_days_str.split(',') if day.strip()]
        
        # Get time to run check (default: 23:30)
        self.check_hour = int(os.getenv('CHECK_HOUR', 23))
        self.check_minute = int(os.getenv('CHECK_MINUTE', 30))
        
        # Whether to send summary even if receipts exist
        self.always_send_summary = os.getenv('ALWAYS_SEND_SUMMARY', 'false').lower() == 'true'
    
    def check_daily_receipts(self):
        """Check if receipts were generated today and send alert if none found"""
        try:
            if not self.app:
                logger.error("App context not available")
                return
            
            with self.app.app_context():
                today = datetime.now()            
                # Check if today is a day we should check
                if today.weekday() not in self.check_days:
                    logger.info(f"Skipping check for {today.strftime('%A')} (not in check days)")
                    return
                if today.weekday()==0:
                    today = today - timedelta(days=3)
                else:
                    today = today - timedelta(days=1) 
                print("Report generated for", today)
                # Query for today's receipts
                start_of_day = today.replace(hour=0, minute=0, second=0, microsecond=0)
                end_of_day = today.replace(hour=23, minute=59, second=59, microsecond=999999)
                
                receipts = Receipt.query.filter(
                    Receipt.deleted_at.is_(None),
                    Receipt.created_at >= start_of_day,
                    Receipt.created_at <= end_of_day
                ).all()
                
                if not receipts:
                    # No receipts found - send alert
                    if self.alert_recipients:
                        logger.info(f"No receipts found for {today.strftime('%Y-%m-%d')}. Sending alert...")
                        success, error = self.email_service.send_no_receipts_alert(
                            self.alert_recipients,
                            today
                        )
                        
                        if success:
                            logger.info(f"Alert sent successfully to {len(self.alert_recipients)} recipients")
                        else:
                            logger.error(f"Failed to send alert: {error}")
                    else:
                        logger.warning("No alert recipients configured")
                else:
                    # Receipts found
                    logger.info(f"Found {len(receipts)} receipts for {today.strftime('%Y-%m-%d')}")
                    
                    # Optionally send summary email
                    if self.always_send_summary and self.alert_recipients:
                        currency = CURRENCY
                        summary_data = self._calculate_summary(receipts)
                        success, error = self.email_service.send_daily_summary(
                            self.alert_recipients,
                            today,
                            summary_data,
                            currency
                        )
                        
                        if success:
                            logger.info("Daily summary sent successfully")
                        else:
                            logger.error(f"Failed to send summary: {error}")
        
        except Exception as e:
            logger.error(f"Error in check_daily_receipts: {str(e)}")
    
    def _calculate_summary(self, receipts):
        """Calculate summary statistics from receipts"""
        total_receipts = len(receipts)
        total_revenue = sum(float(receipt.gross_amount) for receipt in receipts)
        # total_items = sum(len(receipt.receipt_items) for receipt in receipts)
        
        return {
            'total_receipts': total_receipts,
            'total_revenue': total_revenue,
            # 'total_items': total_items
        }
    
    def start(self):
        """Start the scheduler"""
        if not self.alert_recipients:
            logger.warning("No email recipients configured. Scheduler will not send alerts.")
            return
        
        # Schedule daily check
        # Runs at the specified time every day
        self.scheduler.add_job(
            func=self.check_daily_receipts,
            trigger=CronTrigger(
                hour=self.check_hour,
                minute=self.check_minute,
                day_of_week=','.join(map(str, self.check_days))
            ),
            id='daily_receipt_check',
            name='Check daily receipts and send alerts',
            replace_existing=True
        )
        
        self.scheduler.start()
        logger.info(f"Scheduler started. Daily check scheduled for {self.check_hour:02d}:{self.check_minute:02d} on days: {self.check_days}")
    
    def stop(self):
        """Stop the scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Scheduler stopped")
    
    def trigger_check_now(self):
        """Manually trigger the daily check (for testing)"""
        logger.info("Manually triggering daily receipt check...")
        self.check_daily_receipts()