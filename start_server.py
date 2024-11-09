import os
import sys
import base64
import webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler
from socketserver import ThreadingMixIn
from urllib.parse import parse_qs
from io import BytesIO

# Constants
MAX_UPLOAD_FOLDER_SIZE = 10 * 1024 * 1024 * 1024  # 10 GB

class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread for better performance."""
    daemon_threads = True

class AuthHandler(SimpleHTTPRequestHandler):
    """HTTP request handler with basic authentication and file upload support."""
    
    username = None
    password = None
    upload_directory = "uploads"

    def do_HEAD(self):
        """Handle HEAD request."""
        self._authenticate()

    def do_GET(self):
        """Handle GET request."""
        if not self._authenticate():
            return
        
        # Check if the request is for the upload form or root directory listing
        if self.path == '/upload':
            self._render_upload_form()
        else:
            # For any other request, serve the files and directories using the base class method
            super().do_GET()


    def do_POST(self):
        """Handle POST request for file uploads."""
        if not self._authenticate():
            return

        if self.path == '/upload':
            self._handle_file_upload()

    def _authenticate(self):
        """Check for basic authentication if enabled."""
        if AuthHandler.username and AuthHandler.password:
            auth_header = self.headers.get('Authorization')
            if auth_header is None or not self._is_authenticated(auth_header):
                self.send_response(401)
                self.send_header('WWW-Authenticate', 'Basic realm="Authentication Required"')
                self.end_headers()
                self.wfile.write(b"Authentication required.")
                return False
        return True

    def _is_authenticated(self, auth_header):
        """Verify the Authorization header matches the username and password."""
        auth_type, encoded_credentials = auth_header.split(' ', 1)
        if auth_type.lower() == 'basic':
            credentials = base64.b64decode(encoded_credentials).decode('utf-8')
            username, password = credentials.split(':', 1)
            return username == AuthHandler.username and password == AuthHandler.password
        return False

    def _render_directory_listing(self):
        """Render the directory listing with an upload button."""
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        # Generate the HTML for the directory listing
        html = """
        <html><body>
        <h2>Directory Listing</h2>
        <button onclick="window.location.href='/upload'">Upload File</button>
        <ul>
        """
        
        # List files and directories
        for entry in os.listdir('.'):
            if os.path.isdir(entry):
                html += f'<li><strong>[DIR]</strong> <a href="{entry}/">{entry}</a></li>'
            else:
                html += f'<li><a href="{entry}">{entry}</a></li>'
        
        html += "</ul></body></html>"
        self.wfile.write(html.encode('utf-8'))

    def _render_upload_form(self):
        """Display the file upload form."""
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        form_html = """
        <html><body>
        <h2>Upload File</h2>
        <form enctype="multipart/form-data" method="post" action="/upload">
            <input type="file" name="file"><br><br>
            <input type="submit" value="Upload">
        </form>
        <button onclick="window.location.href='/'">Back to Directory Listing</button>
        </body></html>
        """
        self.wfile.write(form_html.encode('utf-8'))

    def _handle_file_upload(self):
        """Handle the file upload using `io` and boundary parsing."""
        content_type = self.headers['Content-Type']
        if not content_type.startswith('multipart/form-data'):
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Invalid request.")
            return

        # Extract boundary from content type
        boundary = content_type.split("boundary=")[-1].encode()
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)

        # Check upload folder size
        if self._get_upload_folder_size() >= MAX_UPLOAD_FOLDER_SIZE:
            self.send_response(413)
            self.end_headers()
            self.wfile.write(b"Upload folder size limit exceeded (10 GB).")
            return

        # Split the body data by the boundary
        parts = body.split(b'--' + boundary)
        for part in parts:
            if b'Content-Disposition:' in part and b'name="file"; filename="' in part:
                headers, file_data = part.split(b'\r\n\r\n', 1)
                file_data = file_data.rstrip(b'\r\n--')  # Trim the trailing boundary

                # Extract the filename
                filename = headers.split(b'filename="')[1].split(b'"')[0].decode()

                # Save the uploaded file
                file_path = os.path.join(self.upload_directory, filename)
                with open(file_path, 'wb') as f:
                    f.write(file_data)

                self.send_response(200)
                self.end_headers()
                self.wfile.write(f"File '{filename}' uploaded successfully.".encode('utf-8'))
                return

        self.send_response(400)
        self.end_headers()
        self.wfile.write(b"No file was uploaded.")

    def _get_upload_folder_size(self):
        """Calculate the total size of the upload folder."""
        total_size = 0
        for dirpath, _, filenames in os.walk(self.upload_directory):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total_size += os.path.getsize(fp)
        return total_size

    def log_message(self, format, *args):
        """Override to log requests to the console."""
        sys.stdout.write(f"{self.client_address[0]} - {self.log_date_time_string()} - {format % args}\n")

def get_local_ip():
    """Helper function to get the local IP address."""
    try:
        ip = os.popen("hostname -I").read().strip()
        if ip:
            return ip.split()[0]
    except:
        pass
    return "127.0.0.1"

def start_server():
    print("\n--- Python HTTP Server Setup ---")
    default_dir = os.getcwd()
    selected_dir = input(f"Enter the directory to serve (default is current directory: {default_dir}): ") or default_dir

    if not os.path.isdir(selected_dir):
        print(f"Invalid directory: {selected_dir}. Using default directory: {default_dir}")
        selected_dir = default_dir

    os.chdir(selected_dir)

    # Create uploads directory
    upload_path = os.path.join(selected_dir, 'uploads')
    if not os.path.exists(upload_path):
        os.makedirs(upload_path)
    AuthHandler.upload_directory = upload_path

    port = int(input("Enter the port to use (default 8080): ") or 8080)
    enable_auth = input("Enable basic authentication? (y/n, default n): ").strip().lower() == 'y'
    if enable_auth:
        username = input("Enter the username: ").strip()
        password = input("Enter the password: ").strip()
        AuthHandler.username = username
        AuthHandler.password = password

    auto_open = input("Auto-open browser? (y/n, default n): ").strip().lower() == 'y'

    if auto_open:
        webbrowser.open(f"http://localhost:{port}/")

    print(f"Serving at http://localhost:{port} and {get_local_ip()}:{port}")

    server = ThreadingHTTPServer(('', port), AuthHandler)
    server.serve_forever()

if __name__ == "__main__":
    start_server()

