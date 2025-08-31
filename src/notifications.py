import requests
import json
from pathlib import Path
import os

class NotificationManager:
    def __init__(self, config_dir="data"):
        self.config_dir = Path(config_dir)
        self.config_file = self.config_dir / 'notifications.json'
        self.config = self._load_config()

    def _load_config(self):
        """Load notification settings from config file"""
        if not self.config_file.exists():
            return {
                'debug': False,
                'discord': {'enabled': False, 'webhook_url': '', 'events': []},
                'pushover': {'enabled': False, 'user_key': '', 'api_token': '', 'events': []}
            }
        
        config = {}
        with open(self.config_file, 'r') as f:
            config = json.load(f)
        
        # Add debug setting if it doesn't exist
        if 'debug' not in config:
            config['debug'] = False
            
        return config

    def _save_config(self):
        """Save notification settings to config file"""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=4)

    def get_config(self):
        """Get current notification configuration"""
        return self.config

    def _debug_log(self, message):
        """Print debug message if debug mode is enabled"""
        if self.config.get('debug', False):
            print(f"NOTIFICATION DEBUG: {message}")

    def set_debug(self, enabled):
        """Enable or disable debug logging"""
        self.config['debug'] = enabled
        self._save_config()
        self._debug_log(f"Debug logging {'enabled' if enabled else 'disabled'}")

    def configure_discord(self, enabled, webhook_url, events):
        """Configure Discord notifications"""
        self.config['discord'] = {
            'enabled': enabled,
            'webhook_url': webhook_url,
            'events': events
        }
        self._save_config()

    def configure_pushover(self, enabled, user_key, api_token, events):
        """Configure Pushover notifications"""
        self.config['pushover'] = {
            'enabled': enabled,
            'user_key': user_key,
            'api_token': api_token,
            'events': events
        }
        self._save_config()

    def send_ip_change_notification(self, new_ip):
        """Send notification when IP address changes"""
        title = "🌐 IP Address Changed"
        message = f"Your public IP address has changed to: **{new_ip}**"
        self._debug_log(f"Sending IP change notification for IP: {new_ip}")
        self.send_notification('ip_change', title, message)

    def send_notification(self, event, title, message):
        """Send notification to all enabled services for the given event"""
        self._debug_log(f"send_notification called with event={event}")
        self._debug_log(f"Discord enabled: {self.config['discord']['enabled']}")
        self._debug_log(f"Discord events: {self.config['discord']['events']}")
        
        sent_count = 0
        
        if self.config['discord']['enabled'] and event in self.config['discord']['events']:
            self._debug_log("Sending Discord notification...")
            if self._send_discord(title, message):
                sent_count += 1
        else:
            self._debug_log(f"Discord notification skipped - enabled: {self.config['discord']['enabled']}, event in events: {event in self.config['discord']['events']}")
        
        if self.config['pushover']['enabled'] and event in self.config['pushover']['events']:
            self._debug_log("Sending Pushover notification...")
            if self._send_pushover(title, message):
                sent_count += 1
        else:
            self._debug_log(f"Pushover notification skipped - enabled: {self.config['pushover']['enabled']}, event in events: {event in self.config['pushover']['events']}")
        
        self._debug_log(f"Notification sent to {sent_count} service(s)")
        return sent_count > 0

    def _send_discord(self, title, message):
        """Send notification to Discord"""
        webhook_url = self.config['discord']['webhook_url']
        if not webhook_url:
            self._debug_log("No Discord webhook URL configured")
            return False

        payload = {
            "embeds": [{
                "title": title,
                "description": message,
                "color": 3447003  # Discord Blue
            }]
        }

        try:
            self._debug_log(f"Sending to Discord webhook: {webhook_url[:50]}...")
            response = requests.post(webhook_url, json=payload)
            if response.status_code == 204:
                self._debug_log("Discord notification sent successfully")
                return True
            else:
                self._debug_log(f"Discord notification failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            self._debug_log(f"Discord notification error: {e}")
            print(f"Failed to send Discord notification: {e}")
            return False

    def _send_pushover(self, title, message):
        """Send notification to Pushover"""
        if not all([self.config['pushover']['user_key'], self.config['pushover']['api_token']]):
            self._debug_log("No Pushover credentials configured")
            return False

        payload = {
            "token": self.config['pushover']['api_token'],
            "user": self.config['pushover']['user_key'],
            "title": title,
            "message": message,
            "priority": 0
        }

        try:
            self._debug_log(f"Sending to Pushover with user key: {self.config['pushover']['user_key'][:10]}...")
            response = requests.post(
                "https://api.pushover.net/1/messages.json",
                data=payload
            )
            if response.status_code == 200:
                self._debug_log("Pushover notification sent successfully")
                return True
            else:
                self._debug_log(f"Pushover notification failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            self._debug_log(f"Pushover notification error: {e}")
            print(f"Failed to send Pushover notification: {e}")
            return False

    def test_notification(self, service):
        """Test notification for a specific service"""
        self._debug_log(f"Testing {service} notification")
        title = "🧪 Test Notification"
        message = f"This is a test notification from IP Sentinel for {service.title()}."
        
        if service == 'discord':
            return self._send_discord(title, message)
        elif service == 'pushover':
            return self._send_pushover(title, message)
        
        return False

    def test_discord_webhook(self, webhook_url):
        """Test a Discord webhook without saving configuration"""
        self._debug_log(f"Testing Discord webhook: {webhook_url[:50]}...")
        
        payload = {
            "embeds": [{
                "title": "🧪 Test Notification",
                "description": "This is a test notification from IP Sentinel for Discord.",
                "color": 3447003  # Discord Blue
            }]
        }

        try:
            response = requests.post(webhook_url, json=payload)
            success = response.status_code == 204
            self._debug_log(f"Discord webhook test {'successful' if success else 'failed'}: {response.status_code}")
            return success
        except Exception as e:
            self._debug_log(f"Discord webhook test error: {e}")
            return False

    def test_pushover_credentials(self, user_key, api_token):
        """Test Pushover credentials without saving configuration"""
        self._debug_log(f"Testing Pushover credentials for user: {user_key[:10]}...")
        
        payload = {
            "token": api_token,
            "user": user_key,
            "title": "🧪 Test Notification",
            "message": "This is a test notification from IP Sentinel for Pushover.",
            "priority": 0
        }

        try:
            response = requests.post(
                "https://api.pushover.net/1/messages.json",
                data=payload
            )
            success = response.status_code == 200
            self._debug_log(f"Pushover test {'successful' if success else 'failed'}: {response.status_code}")
            return success
        except Exception as e:
            self._debug_log(f"Pushover test error: {e}")
            return False
