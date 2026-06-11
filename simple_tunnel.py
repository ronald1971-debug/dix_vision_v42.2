#!/usr/bin/env python3
"""
Simple HTTP Tunnel for localhost:8080
Run this script to make your local service accessible
"""

import http.server
import socketserver
import urllib.request
import urllib.error

class TunnelHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        try:
            # Forward request to localhost:8080
            url = f'http://localhost:8080{self.path}'
            
            # Get query string if present
            if self.path.endswith('?'):
                url = url.rstrip('?')
            
            print(f"Forwarding: {self.path} -> {url}")
            
            # Make request to local service
            with urllib.request.urlopen(url) as response:
                content = response.read()
                content_type = response.getheader('Content-Type', 'application/json')
                
                # Send response
                self.send_response(200)
                self.send_header('Content-Type', content_type)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(content)
                
        except urllib.error.URLError as e:
            self.send_error(502, f"Unable to reach local service: {e}")
        except Exception as e:
            self.send_error(500, f"Server error: {e}")
    
    def do_POST(self):
        try:
            # Get POST data
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            # Forward request to localhost:8080
            url = f'http://localhost:8080{self.path}'
            
            print(f"Forwarding POST: {self.path} -> {url}")
            
            # Make request to local service
            req = urllib.request.Request(url, data=post_data, method='POST')
            
            # Copy headers
            for header, value in self.headers.items():
                if header.lower() not in ['host', 'content-length']:
                    req.add_header(header, value)
            
            with urllib.request.urlopen(req) as response:
                response_content = response.read()
                content_type = response.getheader('Content-Type', 'application/json')
                
                # Send response
                self.send_response(200)
                self.send_header('Content-Type', content_type)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(response_content)
                
        except urllib.error.URLError as e:
            self.send_error(502, f"Unable to reach local service: {e}")
        except Exception as e:
            self.send_error(500, f"Server error: {e}")

def run_tunnel(port=8888):
    """Run the tunnel server"""
    print(f"Starting tunnel on port {port}...")
    print(f"Forwarding http://localhost:{port} -> http://localhost:8080")
    print(f"Access your service at: http://YOUR_LOCAL_IP:{port}")
    print(f"Press Ctrl+C to stop")
    
    with socketserver.TCPServer(('', port), TunnelHandler) as httpd:
        httpd.serve_forever()

if __name__ == '__main__':
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8888
    run_tunnel(port)