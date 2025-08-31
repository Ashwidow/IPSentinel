def main():
    import logging
    from src.web.app import create_app
    from src.ip_monitor import IPMonitor
    from src.scheduler import Scheduler

    # Set up logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)

    # Initialize the application
    app = create_app()

    # Start the IP monitoring
    ip_monitor = IPMonitor()
    scheduler = Scheduler(ip_monitor)

    # Start the web server
    try:
        app.run(host='0.0.0.0', port=5000)
    except Exception as e:
        logger.error(f"Error starting the server: {e}")

if __name__ == "__main__":
    main()