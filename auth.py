from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

public_keys = {}

class handleRequest(BaseHTTPRequestHandler):
    def do_GET(self):
        query = parse_qs(urlparse(self.path).query)
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        
        nome = query.get('nome', [''])[0]
        
        if nome == "":
            response = "status: error, data: nome not provided"
        elif nome not in public_keys:
            response = "status: error, data: nome not found"
        else:
            response = f"status: success; data: {public_keys[nome].decode()}"

        self.wfile.write(response.encode())

    def do_POST(self):
        query = parse_qs(urlparse(self.path).query)
        nome = query.get('nome', [''])[0]

        if nome == "":
            self.send_response(400)
            self.send_header('Content-type', '')
            self.end_headers()
            response = "status: error; data: nome not provided"
            self.wfile.write(response.encode())
            return

        if nome in public_keys:
            self.send_response(400)
            self.send_header('Content-type', '')
            self.end_headers()
            response = f"status: error; data: {nome} already exists"
            self.wfile.write(response.encode())
            return
        
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        public_keys[nome] = post_data

        print(f"Received public key from {nome}")
        
        self.send_response(200)
        self.send_header('Content-type', '')
        self.end_headers()
        response = f"status: success, Public key for {nome} added"
        self.wfile.write(response.encode())


port = 5000
httpServer = HTTPServer(('localhost', port), handleRequest)
print(f'Starting HTTP server on port {port}')
httpServer.serve_forever()