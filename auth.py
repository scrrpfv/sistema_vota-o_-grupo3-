from socket import socket, AF_INET, SOCK_DGRAM
import time


class AuthServer:
    def __init__(self):
        self.web_socket = socket(AF_INET, SOCK_DGRAM)
        self.web_socket.bind(('127.0.0.1', 5000))
        self.public_keys = {}
    
    def handle_GET(self, request):
        print(request)
        if request.startswith('GET / HTTP/1.1'):
            return 'HTTP/1.1 200 OK\n\n'
        
        elif request.startswith('GET /?name='):
            nome = request.split('=')[1].split(' ')[0]
            if nome in self.public_keys:
                return f'HTTP/1.1 200 OK\n\n{self.public_keys[nome]}'
            else:
                return 'HTTP/1.1 404 Not Found\n\nChave pública não encontrada!'
        else:
            return 'HTTP/1.1 400 Bad Request'
    
    def handle_POST(self, request):
        name = request.split('=')[1].split(' ')[0]
        
        if name in self.public_keys:
            print(f'{name} já está registrado.')
            return 'HTTP/1.1 403 Forbidden\n\nO usuário já está registrado.'
            
        public_key = request.split('\n\n')[1]
        self.public_keys[name] = public_key
        print(f'Chave pública de {name} registrada com sucesso!:\n{public_key}')
        return 'HTTP/1.1 200 OK\n\nChave pública registrada com sucesso!'

    def send(self, response, addr):
        self.web_socket.sendto(response.encode(), addr)
    
    def addto_dns(self):
        socket_dns = socket(AF_INET, SOCK_DGRAM)
        socket_dns.bind(('127.0.0.1', 5001))
        
        socket_dns.settimeout(2)
        while True:
            socket_dns.sendto('new_address:auth:127.0.0.1:5000'.encode(), ('127.0.0.1', 10000))
            try:
                response = socket_dns.recv(1024).decode()
            except:
                response = 'DNS_NOT_FOUND'
            print(response)
            if response == 'Endereco adicionado com sucesso':
                socket_dns.close()
                return
            
            time.sleep(5)


servidor = AuthServer()
servidor.addto_dns()
    
print('Aguardando solicitações...')

while True:
    request, addr = servidor.web_socket.recvfrom(1024)
    print(f'Recebendo de {addr}')
    request = request.decode()
    if request.startswith('GET'):
        response = servidor.handle_GET(request)
        servidor.send(response, addr)
    elif request.startswith('POST'):
        response = servidor.handle_POST(request)
        servidor.send(response, addr)