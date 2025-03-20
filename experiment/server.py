from http.server import HTTPServer, SimpleHTTPRequestHandler
import os
import webbrowser
import argparse
import socket
import mimetypes
import sys
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger('ARServer')

# Ensure proper MIME types are registered
mimetypes.add_type('video/mp4', '.mp4')
mimetypes.add_type('application/javascript', '.js')
mimetypes.add_type('text/css', '.css')

def get_local_ip():
    """Get the local IP address to allow other devices to connect"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't need to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

class ARServer(SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        """Override to reduce verbose logging"""
        if args[0].startswith('GET') and (args[0].endswith('200') or args[0].endswith('304')):
            return  # Skip logging successful GET requests
        logger.info("%s - %s", self.address_string(), format % args)

    def end_headers(self):
        # Add CORS headers to allow camera access and video playback
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'X-Requested-With, Content-type')
        SimpleHTTPRequestHandler.end_headers(self)
    
    def do_OPTIONS(self):
        # Handle preflight requests
        self.send_response(200)
        self.end_headers()
    
    def copyfile(self, source, outputfile):
        """Override copyfile to handle connection resets gracefully"""
        try:
            SimpleHTTPRequestHandler.copyfile(self, source, outputfile)
        except ConnectionResetError:
            logger.debug("Connection reset by client - this is normal browser behavior")
        except BrokenPipeError:
            logger.debug("Broken pipe - client closed connection")
        except Exception as e:
            logger.error(f"Error serving file: {e}")

def check_requirements():
    """Check if the necessary files exist in the current directory"""
    required_files = ['index.html']
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_files:
        logger.warning("The following required files are missing:")
        for file in missing_files:
            logger.warning(f"- {file}")
        logger.warning("Please make sure these files exist in the current directory.")
        return False
    return True

def check_video_file():
    """Check for video files in the current directory"""
    video_files = [f for f in os.listdir('.') if f.endswith(('.mp4', '.webm', '.ogg'))]
    
    if not video_files:
        logger.warning("No video files found in the current directory.")
        logger.warning("For testing, create a video file named 'your-video-file.mp4' or update the HTML file.")
        return False
    
    logger.info(f"Found video files: {', '.join(video_files)}")
    return True

def run_server(port=8000, open_browser=True):
    """Run the web server to host the AR application"""
    # Check requirements
    requirements_ok = check_requirements()
    video_ok = check_video_file()
    
    if not requirements_ok or not video_ok:
        logger.warning("Some requirements are missing. Server will still start, but the application may not work correctly.")
    
    # Try to find an available port if the specified one is in use
    max_port_attempts = 10
    current_port = port
    server = None
    
    for attempt in range(max_port_attempts):
        try:
            server_address = ('', current_port)
            server = HTTPServer(server_address, ARServer)
            break
        except OSError as e:
            if e.errno == 98 or e.errno == 10048:  # Port already in use
                logger.warning(f"Port {current_port} is already in use, trying {current_port + 1}")
                current_port += 1
            else:
                raise
    
    if server is None:
        logger.error(f"Could not find an available port after {max_port_attempts} attempts.")
        return
    
    local_ip = get_local_ip()
    
    print("\n" + "="*50)
    print("AR Hologram Web Server")
    print("="*50)
    print(f"Server running at:")
    print(f"- Local: http://localhost:{current_port}")
    print(f"- Network: http://{local_ip}:{current_port}")
    print("\nHow to use:")
    print("1. On your laptop: Visit the local URL in your browser")
    print("2. On your phone: Connect to the same WiFi network and visit the Network URL")
    print("3. Grant camera permissions when prompted")
    print("4. Point camera at the QR code to see the hologram")
    print("\nCommon issues:")
    print("- Connection errors in the console are normal when browsers refresh")
    print("- If camera doesn't start, try a different browser (Chrome works best)")
    print("\nPress Ctrl+C to stop the server")
    print("="*50)
    
    if open_browser:
        webbrowser.open(f"http://localhost:{current_port}")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped by user.")
    except Exception as e:
        logger.error(f"Server error: {e}")
    finally:
        server.server_close()
        print("Server closed.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Start AR web server')
    parser.add_argument('--port', type=int, default=8000, help='Port to run server on')
    parser.add_argument('--no-browser', action='store_true', help='Don\'t open browser automatically')
    
    args = parser.parse_args()
    run_server(args.port, not args.no_browser)