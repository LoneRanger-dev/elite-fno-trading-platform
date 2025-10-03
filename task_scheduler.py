"""
🕒 Task Scheduler
Automates periodic tasks like market analysis reports.
"""
import schedule
import time
import threading
import logging
from market_analysis_engine import MarketAnalysisEngine
from telegram_bot import telegram_bot  # Assuming telegram_bot is the global instance

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TaskScheduler:
    def __init__(self):
        self.analysis_engine = MarketAnalysisEngine(telegram_bot=telegram_bot)
        self.is_running = False
        self.scheduler_thread = None
        logger.info("Task Scheduler initialized")

    def _run_pre_market_report(self):
        """Job function for the pre-market report."""
        logger.info("Scheduler is running pre-market report job.")
        self.analysis_engine.generate_pre_market_report()

    def _run_post_market_report(self):
        """Job function for the post-market report."""
        logger.info("Scheduler is running post-market report job.")
        self.analysis_engine.generate_post_market_report()

    def setup_schedule(self):
        """Sets up the scheduled jobs."""
        # Schedule jobs at specific times (using 24-hour format)
        # Note: This uses the server's local time.
        schedule.every().day.at("08:30").do(self._run_pre_market_report)
        schedule.every().day.at("15:45").do(self._run_post_market_report) # Run 15 mins after market close
        
        logger.info("Scheduled tasks:")
        for job in schedule.get_jobs():
            logger.info(f"- {job}")

    def _scheduler_loop(self):
        """The main loop that runs pending jobs."""
        logger.info("Scheduler loop started.")
        while self.is_running:
            schedule.run_pending()
            time.sleep(1) # Check for pending jobs every second
        logger.info("Scheduler loop stopped.")

    def start(self):
        """Starts the scheduler in a background thread."""
        if not self.is_running:
            self.is_running = True
            self.setup_schedule()
            self.scheduler_thread = threading.Thread(target=self._scheduler_loop)
            self.scheduler_thread.daemon = True
            self.scheduler_thread.start()
            logger.info("🚀 Task Scheduler started in background.")
        else:
            logger.info("Task Scheduler is already running.")

    def stop(self):
        """Stops the scheduler."""
        if self.is_running:
            self.is_running = False
            if self.scheduler_thread:
                self.scheduler_thread.join(timeout=5)
            logger.info("⏹️ Task Scheduler stopped.")

# Global scheduler instance
task_scheduler = TaskScheduler()

# For testing purposes
if __name__ == '__main__':
    logger.info("Running Task Scheduler in test mode...")
    task_scheduler.start()
    try:
        # Keep the main thread alive to see the scheduler run
        while True:
            time.sleep(10)
            logger.info(f"Scheduler alive. Next run: {schedule.next_run}")
    except KeyboardInterrupt:
        logger.info("Stopping test mode.")
        task_scheduler.stop()
