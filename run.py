from src.web.app import create_app
import socket
import os
import logging
import sys
from io import StringIO

# Completely suppress all Flask and Werkzeug logging
logging.getLogger('werkzeug').setLevel(logging.CRITICAL)
logging.getLogger('werkzeug').disabled = True
logging.getLogger('flask').setLevel(logging.CRITICAL)
logging.getLogger('flask').disabled = True

# Suppress click (used by Flask for CLI output)
os.environ['WERKZEUG_RUN_MAIN'] = 'true'

def get_local_ip():
    try:
        # Get local IP address
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return 'localhost'

if __name__ == '__main__':
    port = int(os.getenv('PORT', 7450))
    local_ip = get_local_ip()
    
    # Print startup message to stderr so it shows in Docker logs
    print(f"\n✨ IP Sentinel is running!", file=sys.stderr)
    print(f"📡 Local access:  http://localhost:{port}", file=sys.stderr)
    print(f"🌐 Network:       http://{local_ip}:{port}\n", file=sys.stderr)
    sys.stderr.flush()
    
    # Redirect stdout and stderr to suppress Flask startup messages
    class DevNull:
        def write(self, msg):
            pass
        def flush(self):
            pass
    
    original_stdout = sys.stdout
    original_stderr = sys.stderr
    
    try:
        app = create_app()
        app.logger.disabled = True
        
        # Use a completely silent run
        from werkzeug.serving import make_server
        server = make_server('0.0.0.0', port, app, threaded=True)
        
        # Only suppress output after the server starts
        sys.stdout = DevNull()
        sys.stderr = DevNull()
        
        server.serve_forever()
        
    except KeyboardInterrupt:
        sys.stdout = original_stdout
        sys.stderr = original_stderr
        print("\n👋 IP Sentinel stopped", file=sys.stderr)