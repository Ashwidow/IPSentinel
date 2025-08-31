import requests
import logging
import os
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict

class IPMonitor:
    def __init__(self, log_file: str = "logs/ip_changes.log", data_dir: str = "data"):
        self.log_file = log_file
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup logging with custom datetime format
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format='%(asctime)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'  # Remove milliseconds from timestamp
        )
        
        self.current_ip = self._load_last_ip()
        self.agent_mode = os.getenv('ENABLE_AGENT', 'false').lower() == 'true'
        self.check_interval = int(os.getenv('AGENT_INTERVAL', '300'))
    
    def _load_last_ip(self) -> Optional[str]:
        """Load the last known IP from storage"""
        ip_file = self.data_dir / 'last_ip.json'
        if ip_file.exists():
            try:
                with open(ip_file, 'r') as f:
                    data = json.load(f)
                return data.get('ip')
            except Exception as e:
                logging.error(f"Error loading last IP: {e}")
        return None
    
    def _save_ip(self, ip: str) -> None:
        """Save current IP to persistent storage"""
        ip_file = self.data_dir / 'last_ip.json'
        data = {
            'ip': ip,
            'last_updated': datetime.now().isoformat()
        }
        try:
            with open(ip_file, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            logging.error(f"Error saving IP: {e}")
    
    def get_public_ip(self) -> Optional[str]:
        """Get public IP with fallback providers"""
        providers = [
            ('https://api.ipify.org?format=json', lambda r: r.json()['ip']),
            ('https://ifconfig.me/ip', lambda r: r.text.strip()),
            ('https://api.ipapi.com/api/check?access_key=free', lambda r: r.json()['ip'])
        ]
        
        for url, parser in providers:
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    return parser(response)
            except Exception as e:
                logging.debug(f"Provider {url} failed: {e}")
                continue
        
        logging.error("All IP providers failed")
        return None
    
    def _get_last_change_time(self) -> Optional[datetime]:
        """Get the timestamp of the last IP change from logs"""
        try:
            if not os.path.exists(self.log_file):
                return None
                
            with open(self.log_file, 'r') as f:
                lines = f.readlines()
                
            # Look for the most recent "IP changed to" entry
            for line in reversed(lines):
                if "IP changed to" in line:
                    # Extract timestamp from log line (format: "YYYY-MM-DD HH:MM:SS - IP changed to: ...")
                    timestamp_str = line.split(' - ')[0]
                    return datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
            
            return None
        except Exception as e:
            logging.error(f"Error getting last change time: {e}")
            return None

    def check_ip_change(self) -> Dict[str, str]:
        """Check for IP changes and return status"""
        new_ip = self.get_public_ip()
        status = {'status': 'error', 'message': 'Failed to get IP'}
        
        if new_ip:
            if self.current_ip != new_ip:
                self.current_ip = new_ip
                self._save_ip(new_ip)
                msg = f"IP changed to: {new_ip}"
                logging.info(msg)
                status = {'status': 'changed', 'message': msg, 'ip': new_ip}
            else:
                # Generate a more informative status message based on last change
                last_change = self._get_last_change_time()
                if last_change:
                    now = datetime.now()
                    time_diff = now - last_change
                    
                    if time_diff.days > 1:
                        status_msg = f"IP unchanged for {time_diff.days} days"
                        status_type = 'unchanged'
                    elif time_diff.days == 1:
                        status_msg = "IP unchanged for 1 day"
                        status_type = 'unchanged'
                    elif time_diff.seconds > 3600:
                        hours = time_diff.seconds // 3600
                        status_msg = f"IP unchanged for {hours} hour{'s' if hours > 1 else ''}"
                        status_type = 'unchanged'
                    elif time_diff.seconds > 60:
                        minutes = time_diff.seconds // 60
                        status_msg = f"IP unchanged for {minutes} minute{'s' if minutes > 1 else ''}"
                        status_type = 'unchanged'
                    else:
                        status_msg = "IP changed recently"
                        status_type = 'recent_change'  # Different status for recent changes
                else:
                    status_msg = "No previous IP changes recorded"
                    status_type = 'unchanged'
                
                status = {'status': status_type, 'message': status_msg, 'ip': new_ip}
        
        return status