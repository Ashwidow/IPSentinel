import click
import json
import os
from crontab import CronSlices
from .ip_monitor import IPMonitor

@click.group()
def cli():
    """IP Tracker CLI - Monitor and track your public IP address"""
    pass

@cli.command()
def check():
    """Check current public IP address"""
    monitor = IPMonitor()
    status = monitor.check_ip_change()
    
    if status['status'] == 'error':
        click.secho(status['message'], fg='red')
        exit(1)
    
    color = 'green' if status['status'] == 'unchanged' else 'yellow'
    click.secho(status['message'], fg=color)
    click.echo(f"Current IP: {status['ip']}")

@cli.command()
def history():
    """Show IP address change history"""
    monitor = IPMonitor()
    try:
        with open(monitor.log_file, 'r') as f:
            logs = f.readlines()
        
        if not logs:
            click.echo("No history found")
            return
        
        for log in logs:
            click.echo(log.strip())
    except FileNotFoundError:
        click.secho("No history file found", fg='yellow')
    except Exception as e:
        click.secho(f"Error reading history: {e}", fg='red')

@cli.command()
def current():
    """Get last known IP address"""
    monitor = IPMonitor()
    try:
        with open(monitor.data_dir / 'last_ip.json', 'r') as f:
            data = json.load(f)
            click.echo(f"IP: {data['ip']}")
            click.echo(f"Last updated: {data['last_updated']}")
    except FileNotFoundError:
        click.secho("No saved IP found", fg='yellow')
    except Exception as e:
        click.secho(f"Error: {e}", fg='red')

@cli.group()
def schedule():
    """Manage IP check schedule"""
    pass

@schedule.command()
def show():
    """Show current schedule"""
    config_file = os.path.join('data', 'config.json')
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
            click.echo(f"Current schedule: {config.get('schedule', '0 0 * * *')}")
    except FileNotFoundError:
        click.echo("Current schedule: 0 0 * * * (default)")

@schedule.command()
def daily():
    """Set schedule to daily at midnight"""
    _update_schedule("0 0 * * *")

@schedule.command()
def hourly():
    """Set schedule to every hour"""
    _update_schedule("0 * * * *")

@schedule.command()
@click.argument('cron')
def custom(cron):
    """Set custom schedule using CRON expression"""
    if not CronSlices.is_valid(cron):
        click.secho("Invalid CRON expression", fg='red')
        return
    _update_schedule(cron)

def _update_schedule(schedule):
    """Update schedule in config file"""
    config_file = os.path.join('data', 'config.json')
    config = {}
    
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            config = json.load(f)
    
    config['schedule'] = schedule
    
    with open(config_file, 'w') as f:
        json.dump(config, f)
    
    click.secho(f"Schedule updated to: {schedule}", fg='green')

if __name__ == '__main__':
    cli()