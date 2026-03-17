"""Scheduler for automated discovery pipeline"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from motor.motor_asyncio import AsyncIOMotorDatabase
import logging
from .pipeline import DiscoveryPipeline

logger = logging.getLogger(__name__)

class DiscoveryScheduler:
    """Scheduler for automated facility discovery"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.scheduler = AsyncIOScheduler()
        self.is_running = False
    
    async def run_scheduled_discovery(self):
        """Run discovery pipeline on schedule"""
        try:
            logger.info("Running scheduled discovery pipeline")
            pipeline = DiscoveryPipeline(self.db, mode='demo')
            result = await pipeline.run_discovery()
            logger.info(f"Scheduled discovery completed: {result}")
        except Exception as e:
            logger.error(f"Scheduled discovery error: {str(e)}")
    
    def start(self, schedule: str = 'weekly'):
        """Start the scheduler
        
        Args:
            schedule: 'daily', 'weekly', or cron expression
        """
        if self.is_running:
            logger.warning("Scheduler already running")
            return
        
        # Add job based on schedule
        if schedule == 'daily':
            # Run daily at 2 AM
            self.scheduler.add_job(
                self.run_scheduled_discovery,
                CronTrigger(hour=2, minute=0),
                id='daily_discovery',
                replace_existing=True
            )
            logger.info("Scheduled daily discovery at 2:00 AM")
        
        elif schedule == 'weekly':
            # Run weekly on Monday at 2 AM
            self.scheduler.add_job(
                self.run_scheduled_discovery,
                CronTrigger(day_of_week='mon', hour=2, minute=0),
                id='weekly_discovery',
                replace_existing=True
            )
            logger.info("Scheduled weekly discovery on Monday at 2:00 AM")
        
        else:
            # Custom cron expression
            self.scheduler.add_job(
                self.run_scheduled_discovery,
                CronTrigger.from_crontab(schedule),
                id='custom_discovery',
                replace_existing=True
            )
            logger.info(f"Scheduled discovery with custom cron: {schedule}")
        
        self.scheduler.start()
        self.is_running = True
        logger.info("Discovery scheduler started")
    
    def stop(self):
        """Stop the scheduler"""
        if self.is_running:
            self.scheduler.shutdown()
            self.is_running = False
            logger.info("Discovery scheduler stopped")
    
    def get_status(self) -> dict:
        """Get scheduler status"""
        jobs = []
        if self.is_running:
            for job in self.scheduler.get_jobs():
                jobs.append({
                    'id': job.id,
                    'next_run': job.next_run_time.isoformat() if job.next_run_time else None
                })
        
        return {
            'is_running': self.is_running,
            'jobs': jobs
        }
