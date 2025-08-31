# 🌐 IP Sentinel

<div align="center">

**A modern, elegant IP address monitoring solution with real-time tracking and notifications**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

## ✨ Features

- **🎯 Real-time Monitoring** - Track your public IP address changes with precision
- **🌟 Modern Web Interface** - Beautiful, responsive dashboard with live updates
- **⏰ Flexible Scheduling** - CRON-based scheduling with presets and custom expressions
- **🔔 Smart Notifications** - Discord and Pushover integration for instant alerts
- **📊 Historical Tracking** - Complete history of IP changes with timestamps
- **🐳 Docker Ready** - One-command deployment with Docker Compose
- **⚡ Lightweight** - Minimal resource usage, perfect for always-on monitoring
- **🛠️ CLI Tools** - Command-line interface for automation and scripting

## 🎯 Use Cases

IP Sentinel is particularly valuable in several networking scenarios:

### 🏠 **CGNAT (Carrier-Grade NAT) Networks**
Many ISPs use CGNAT, which can cause your public IP to change frequently. IP Sentinel helps you:
- **Monitor Dynamic IP Changes** - Know exactly when your ISP assigns a new public IP
- **Remote Access Management** - Update dynamic DNS services or firewall rules automatically
- **Service Continuity** - Detect when IP changes might affect hosted services or remote connections
- **Troubleshooting** - Correlate connectivity issues with IP changes

### 🔒 **VPN Connection Monitoring**
When using VPN services, your public IP should reflect the VPN exit point. IP Sentinel helps you:
- **VPN Leak Detection** - Verify your VPN is working and hasn't leaked your real IP
- **Connection Reliability** - Monitor VPN disconnections and reconnections
- **Exit Point Tracking** - Know which VPN server location you're currently using
- **Privacy Assurance** - Ensure your real IP remains hidden

### 🌐 **Dynamic DNS & Remote Services**
Perfect for users running services from dynamic IP connections:
- **Home Server Management** - Update DNS records when your home IP changes
- **Remote Work Setup** - Maintain access to home resources with changing IPs
- **Gaming Servers** - Keep friends updated with your current server IP
- **IoT Device Management** - Track IP changes for remote device access

## 🚀 Quick Start

### Using Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/ashwidow/IPSentinel.git
cd IPSentinel

# Start with Docker Compose
docker compose up -d

# Access the web interface
open http://localhost:7450
```

### Manual Installation

```bash
# Clone and install
git clone https://github.com/ashwidow/IPSentinel.git
cd IPSentinel
pip install -r requirements.txt

# Run the application
python run.py

# Access at http://localhost:7450
```

## 🎛️ Configuration

### Web Interface
The dashboard provides an intuitive interface for all configuration:

- **Dashboard** - Real-time status and next check countdown
- **History** - Complete log of IP changes with timestamps
- **Settings** - Schedule configuration and notification setup
- **Notifications** - Discord and Pushover integration

### Schedule Configuration

Choose from preset schedules or create custom CRON expressions:

| Preset | CRON Expression | Description |
|--------|----------------|-------------|
| Every Minute | `* * * * *` | For testing and immediate updates |
| Every 5 Minutes | `*/5 * * * *` | High-frequency monitoring |
| Every 30 Minutes | `*/30 * * * *` | Balanced monitoring |
| Hourly | `0 * * * *` | Standard monitoring |
| Every 6 Hours | `0 */6 * * *` | Low-frequency monitoring |
| Daily | `0 0 * * *` | Once per day monitoring |

### Environment Variables

Customize behavior with environment variables:

```yaml
# docker-compose.yml
environment:
  - PORT=7450                    # Web interface port
  - HOST=0.0.0.0                # Listen address
  - SCHEDULE=*/30 * * * *        # Default schedule
  - DISCORD_WEBHOOK_URL=https... # Discord notifications
  - PUSHOVER_TOKEN=your_token    # Pushover notifications
  - PUSHOVER_USER=your_user      # Pushover user key
```

## 🔔 Notifications

IP Sentinel supports multiple notification methods:

### Discord Integration
Set up a Discord webhook to receive IP change notifications in your server:

1. Create a webhook in your Discord server
2. Add the webhook URL to your configuration
3. Receive instant notifications when your IP changes

### Pushover Integration  
Get push notifications on your mobile device:

1. Create a Pushover account and app
2. Configure your token and user key
3. Receive notifications anywhere

## 🛠️ CLI Usage

IP Sentinel includes a powerful command-line interface:

```bash
# Check current public IP
ip-sentinel check

# View IP change history
ip-sentinel history

# Show current status
ip-sentinel status

# Configure schedule
ip-sentinel schedule set "*/30 * * * *"

# Test notifications
ip-sentinel notify test
```

## 📊 API Reference

RESTful API for integration and automation:

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/status` | Current IP and monitoring status |
| GET | `/api/history` | IP change history |
| GET | `/api/schedule` | Current schedule configuration |
| POST | `/api/schedule` | Update schedule |
| GET | `/api/notifications` | Notification settings |
| POST | `/api/notifications` | Update notification settings |

### Example API Usage

```bash
# Get current status
curl http://localhost:7450/api/status

# Update schedule to check every 15 minutes
curl -X POST http://localhost:7450/api/schedule \
  -H "Content-Type: application/json" \
  -d '{"schedule": "*/15 * * * *"}'
```

## 🐳 Docker Deployment

### Docker Compose (Recommended)

```yaml
version: '3.8'
services:
  ip-sentinel:
    image: ashwidow/ipsentinel:latest
    container_name: ip-sentinel
    ports:
      - "7450:7450"
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    environment:
      - PORT=7450
      - HOST=0.0.0.0
    restart: unless-stopped
```

Start with a single command:
```bash
docker compose up -d
```

### Standalone Docker

```bash
# Build the image
docker build -t ip-sentinel .

# Run the container
docker run -d \
  --name ip-sentinel \
  -p 7450:7450 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  ip-sentinel
```

## 🔧 Development

### Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/ashwidow/IPSentinel.git
cd IPSentinel

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run in development mode
python run.py
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**⭐ Star this repository if you find it useful!**

Made by [Ashwidow](https://github.com/ashwidow)

</div>