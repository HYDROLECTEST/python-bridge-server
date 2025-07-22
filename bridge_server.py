from http.server import BaseHTTPRequestHandler, HTTPServer
import requests
import json

# --- Configure Target Server ---
FORWARD_URL = 'http://listener.dev.novaassure.com:8080/plc/listener' # 'http://34.214.30.9:8090'

class ForwardHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        # Read the incoming POST data from PLC
        content_length = int(self.headers.get('Content-Length', 0))
        post_body = self.rfile.read(content_length)
        print(f"[Bridge] Received from PLC: {post_body.decode()}")

        try:
            # Forward the data to the real receiver
            headers = {'Content-Type': 'application/json'}
            response = requests.post(FORWARD_URL, data=post_body, headers=headers)

            print(f"[Bridge] Forwarded to {FORWARD_URL} - Status: {response.status_code}")
            print(f"[Bridge] Receiver Response: {response.text}")

            # Respond to the PLC
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status":"ok"}')

        except Exception as e:
            print(f"[Bridge] Error forwarding: {e}")
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status":"error"}')

# Run the local bridge on port 8080
if __name__ == '__main__':
    print("Starting bridge server on port 8080...")
    server = HTTPServer(('0.0.0.0', 8080), ForwardHandler)
    server.serve_forever()
