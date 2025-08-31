from croniter import croniter
import os
import time
import json
import logging
from datetime import datetime
from threading import Thread

class Scheduler:
    def __init__(self, monitor, notifications=None):
        self.monitor = monitor
        self.notifications = notifications
        self.config_file = os.path.join('data', 'schedule_config.json')
        self.schedule = self._load_schedule()
        self.running = False
        self._thread = None
        self._next_run_time = None
    
    def _load_schedule(self):
        """Load schedule from config file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    return config.get('schedule', '*/5 * * * *')  # Default: every 5 minutes
        except Exception as e:
            print(f"Error loading schedule config: {e}")
        
        # Default schedule if no config exists
        return '*/5 * * * *'
    
    def _save_schedule(self):
        """Save schedule to config file"""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            config = {
                'schedule': self.schedule,
                'last_updated': datetime.now().isoformat()
            }
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            print(f"Schedule saved: {self.schedule}")
        except Exception as e:
            print(f"Error saving schedule config: {e}")
    
    def start(self):
        """Start the scheduler in a background thread"""
        if self._thread is not None:
            return
        
        # Initialize next run time
        try:
            cron = croniter(self.schedule, datetime.now())
            self._next_run_time = cron.get_next(datetime)
        except Exception:
            self._next_run_time = None
        
        self.running = True
        self._thread = Thread(target=self._run, daemon=True)
        self._thread.start()
    
    def stop(self):
        """Stop the scheduler"""
        self.running = False
        if self._thread:
            self._thread.join()
            self._thread = None
    
    def _run(self):
        """Main scheduler loop"""
        while self.running:
            try:
                cron = croniter(self.schedule)
                next_run = cron.get_next()
                self._next_run_time = datetime.fromtimestamp(next_run)
                
                while self.running:
                    now = time.time()
                    if now >= next_run:
                        # Check for IP changes
                        result = self.monitor.check_ip_change()
                        logging.info(f"SCHEDULER DEBUG: IP check result: {result}")
                        
                        # Send notification if IP changed
                        if result.get('status') == 'changed' and self.notifications:
                            ip = result.get('ip', 'Unknown')
                            logging.info(f"SCHEDULER DEBUG: Sending notification for IP change to {ip}")
                            self.notifications.send_ip_change_notification(ip)
                            logging.info(f"SCHEDULER DEBUG: Notification sent")
                        elif result.get('status') == 'changed' and not self.notifications:
                            logging.error(f"SCHEDULER DEBUG: IP changed but no notifications object available")
                        else:
                            logging.debug(f"SCHEDULER DEBUG: No IP change detected, status: {result.get('status')}")
                        
                        # Get the next run time after executing
                        cron = croniter(self.schedule)
                        next_run = cron.get_next()
                        self._next_run_time = datetime.fromtimestamp(next_run)
                    time.sleep(10)  # Check every 10 seconds for better responsiveness
            except Exception as e:
                print(f"Scheduler error: {e}")
                time.sleep(60)  # Wait a minute before retrying
    
    @property
    def next_run(self):
        """Get the next scheduled run time"""
        if self._next_run_time:
            return self._next_run_time
        
        # Fallback calculation if not set
        try:
            cron = croniter(self.schedule, datetime.now())
            return cron.get_next(datetime)
        except Exception:
            return None
    
    def get_schedule(self):
        """Get current schedule information"""
        return {
            'schedule': self.schedule,
            'next_run': self.next_run.isoformat() if self.next_run else None,
            'running': self.running
        }
    
    def update_cron_schedule(self, cron_expression):
        """Update schedule with custom CRON expression"""
        # Validate CRON expression
        try:
            croniter(cron_expression)
        except ValueError as e:
            raise ValueError(f"Invalid CRON expression: {str(e)}")
        
        self.schedule = cron_expression
        
        # Update next run time
        try:
            cron = croniter(self.schedule, datetime.now())
            self._next_run_time = cron.get_next(datetime)
        except Exception:
            self._next_run_time = None
        
        self._save_schedule()  # Save to file
        print(f"Updated schedule to custom CRON: {self.schedule}")
        
        # Restart scheduler with new schedule
        if self.running:
            self.stop()
            time.sleep(1)  # Give it a moment to stop
            self.start()
    
    def update_schedule(self, interval_seconds):
        """Update schedule with interval in seconds"""
        # Convert seconds to cron expression
        if interval_seconds >= 3600:  # 1 hour or more
            hours = interval_seconds // 3600
            if hours == 1:
                self.schedule = "0 * * * *"  # Every hour
            else:
                self.schedule = f"0 */{hours} * * *"  # Every N hours
        elif interval_seconds >= 60:  # 1 minute or more
            minutes = interval_seconds // 60
            if minutes == 1:
                self.schedule = "* * * * *"  # Every minute
            else:
                self.schedule = f"*/{minutes} * * * *"  # Every N minutes
        else:
            # For very short intervals, use every minute
            self.schedule = "* * * * *"
        
        # Update next run time
        try:
            cron = croniter(self.schedule, datetime.now())
            self._next_run_time = cron.get_next(datetime)
        except Exception:
            self._next_run_time = None
        
        self._save_schedule()  # Save to file
        print(f"Updated schedule to: {self.schedule} (interval: {interval_seconds}s)")
        
        # Restart scheduler if it's running to pick up new schedule
        if self.running:
            self.stop()
            time.sleep(1)  # Give it a moment to stop
            self.start()
    
    def set_schedule(self, cron_expression):
        """Update the schedule with a new cron expression"""
        try:
            croniter(cron_expression)
            self.schedule = cron_expression
            return True
        except Exception:
            return False