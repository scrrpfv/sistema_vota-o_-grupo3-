from http.server import BaseHTTPRequestHandler, HTTPServer
import json

class handleRequest(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        response = {"message": "Hello from the HTTP server!"}
        self.wfile.write(json.dumps(response).encode())

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data)
        print(f"Received POST data: {data}")
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        response = {"status": "success", "data": data}
        self.wfile.write(json.dumps(response).encode())
        
port = 5000
httpServer = HTTPServer(('localhost', port), handleRequest)
print(f'Starting HTTP server on port {port}')
httpServer.serve_forever()