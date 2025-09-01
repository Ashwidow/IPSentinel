from src.web.app import create_app
import socket
import os
import logging
import sys
import subprocess
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
        # Use HOST_IP environment variable if set
        host_ip = os.environ.get('HOST_IP')
        if host_ip and host_ip.strip():
            return host_ip.strip()
        
        return 'localhost'
    except:
        return 'localhost'

if __name__ == '__main__':
    port = 7450
    local_ip = get_local_ip()
    
    # Print startup message to stderr so it shows in Docker logs
    print(f"\n✨ IP Sentinel is running!", file=sys.stderr)
    print(f"✅ App is accessible at:", file=sys.stderr)
    print(f"   - http://localhost:{port}", file=sys.stderr)
    
    # Show the detected host IP if it's not localhost
    if local_ip != 'localhost':
        print(f"   - http://{local_ip}:{port}", file=sys.stderr)
    
    print("", file=sys.stderr)  # Empty line
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