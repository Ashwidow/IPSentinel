from flask import Flask, render_template, jsonify, request
from ..ip_monitor import IPMonitor
from ..scheduler import Scheduler as IPScheduler
from ..notifications import NotificationManager
import os
from datetime import datetime

def create_app():
    app = Flask(__name__)
    monitor = IPMonitor()
    notifications = NotificationManager()
    scheduler = IPScheduler(monitor, notifications)  # Pass notifications to scheduler
    
    # Start IP monitoring
    scheduler.start()

    # Register routes
    @app.route('/')
    def index():
        status = monitor.check_ip_change()
        return render_template('index.html', ip_status=status)

    @app.route('/notifications')
    def notifications_page():
        return render_template('notifications.html', config=notifications.config)

    @app.route('/settings')
    def settings_page():
        return render_template('settings.html', 
                             schedule=scheduler.get_schedule(), 
                             monitor=monitor)

    @app.route('/api/notifications', methods=['GET'])
    def get_notifications():
        try:
            config = notifications.get_config()
            return jsonify({
                'status': 'success',
                'data': config
            })
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500

    @app.route('/api/notifications/discord', methods=['POST'])
    def update_discord():
        data = request.json
        notifications.update_discord(
            enabled=data.get('enabled', False),
            webhook_url=data.get('webhook_url', ''),
            events=data.get('events', [])
        )
        return jsonify({'status': 'success'})

    @app.route('/api/notifications/pushover', methods=['POST'])
    def update_pushover():
        data = request.json
        notifications.update_pushover(
            enabled=data.get('enabled', False),
            user_key=data.get('user_key', ''),
            api_token=data.get('api_token', ''),
            events=data.get('events', [])
        )
        return jsonify({'status': 'success'})

    @app.route('/api/notifications/test', methods=['POST'])
    def test_notification():
        data = request.json
        service = data.get('service')
        
        if service == 'discord':
            webhook_url = data.get('webhook_url')
            if webhook_url:
                success = notifications.test_discord_webhook(webhook_url)
            else:
                success = notifications.test_notification(service)
        elif service == 'pushover':
            user_key = data.get('user_key')
            api_token = data.get('api_token')
            if user_key and api_token:
                success = notifications.test_pushover_credentials(user_key, api_token)
            else:
                success = notifications.test_notification(service)
        else:
            success = False
            
        if success:
            return jsonify({
                'status': 'success',
                'message': f'Test notification sent to {service}'
            })
        return jsonify({
            'status': 'error',
            'message': f'Failed to send test notification to {service}'
        })

    @app.route('/health')
    def health_check():
        """Health check endpoint for Docker and monitoring"""
        try:
            # Basic health checks
            status = {
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'version': '1.0.0',
                'services': {
                    'web': 'ok',
                    'scheduler': 'ok' if scheduler else 'error',
                    'monitor': 'ok' if monitor else 'error'
                }
            }
            return jsonify(status), 200
        except Exception as e:
            return jsonify({
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }), 503

    @app.route('/api/notifications/debug', methods=['GET'])
    def get_debug_status():
        return jsonify({
            'debug': notifications.get_config().get('debug', False)
        })

    @app.route('/api/notifications/debug', methods=['POST'])
    def set_debug_status():
        data = request.json
        enabled = data.get('enabled', False)
        notifications.set_debug(enabled)
        return jsonify({
            'status': 'success',
            'debug': enabled
        })

    @app.route('/api/schedule', methods=['GET'])
    def get_schedule():
        try:
            schedule_info = scheduler.get_schedule()
            return jsonify({
                'status': 'success',
                'data': schedule_info
            })
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500

    @app.route('/api/schedule', methods=['POST'])
    def update_schedule():
        data = request.json
        try:
            if 'cron' in data:
                # Custom CRON expression
                scheduler.update_cron_schedule(data['cron'])
                return jsonify({'status': 'success', 'message': 'Custom schedule updated successfully'})
            else:
                # Interval in seconds
                scheduler.update_schedule(data.get('interval', 300))
                return jsonify({'status': 'success', 'message': 'Schedule updated successfully'})
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500

    @app.route('/api/status')
    def api_status():
        return jsonify(monitor.check_ip_change())

    @app.route('/api/status', methods=['POST'])
    def force_check():
        try:
            result = monitor.check_ip_change()
            
            # Send notification if IP changed
            if result.get('status') == 'changed':
                ip = result.get('ip', 'Unknown')
                notifications.send_ip_change_notification(ip)
            
            return jsonify({
                'status': 'success',
                'message': 'IP check completed',
                'data': result
            })
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': f'Error during IP check: {str(e)}'
            }), 500

    @app.route('/api/history')
    def api_history():
        try:
            with open(monitor.log_file, 'r') as f:
                logs = [line.strip() for line in f if "IP changed to" in line]
            return jsonify({
                'status': 'success',
                'logs': logs,
                'count': len(logs)
            })
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500

    @app.route('/api/logs/clear', methods=['POST'])
    def clear_logs():
        try:
            # Clear the log file completely
            with open(monitor.log_file, 'w') as f:
                f.write("")  # Ensure file is completely empty
            
            # Get the current IP and reset monitor state properly
            current_ip = monitor.get_public_ip()
            if current_ip:
                # Set this as the current IP without logging it as a change
                monitor.current_ip = current_ip
                # Update the persistent storage
                monitor._save_ip(current_ip)
            
            # Clear last IP data file if it exists and recreate with current IP
            last_ip_file = os.path.join('data', 'last_ip.json')
            if os.path.exists(last_ip_file):
                os.remove(last_ip_file)
            
            # Save the current IP so future checks have a baseline
            if current_ip:
                monitor._save_ip(current_ip)
            
            return jsonify({
                'status': 'success',
                'message': 'All logs and statistics have been cleared'
            })
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': f'Error clearing logs: {str(e)}'
            }), 500

    return app
