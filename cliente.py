from socket import socket, AF_INET, SOCK_STREAM, SOCK_DGRAM
import time
import rsa


class Eleitor:
    def __init__(self):
        self.nome = None
        self.socket = None
        self.private_key = None

    def get_address(self, addr_name):
        dns_address = ('127.0.0.1', 10000)
        socket_dns = socket(AF_INET, SOCK_DGRAM)    # Abre socket temporário
        socket_dns.settimeout(2)    # Define timeout para 2 segundos
        
        response = None
        while response is None:
            socket_dns.sendto(f'get_address:{addr_name}'.encode(), dns_address)
            try:
                response = socket_dns.recv(1024).decode().split(':')
            except:
                print('DNS nao encontrado')
            
            if response is not None:
                if 'Not Found' in response:
                    print('Servidor nao encontrado')
                    response = None
                else:
                    socket_dns.close()
                    return (response[0], int(response[1]))
            time.sleep(5)
        
    def connect_server(self):
        server_address = self.get_address('votacao')
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.socket.connect(server_address)
        print(f'Conectado ao servidor Com porta {server_address[1]}')
    
    def atribuir_nome(self, nome):
        self.nome = nome
        
    def enviar(self, msg):
        self.socket.send(msg.encode())

    def receber(self):
        return self.socket.recv(1024).decode()
    
    def check_username(self, socket_http, http_address):
        get_request = f"GET /?name={self.nome} HTTP/1.1"
        socket_http.sendto(get_request.encode(), http_address)
        get_response = socket_http.recv(1024).decode()
        
        if get_response.startswith('HTTP/1.1 200 OK'):
            public_key_str = get_response.split('\n\n')[1]
            public_key = rsa.PublicKey.load_pkcs1(public_key_str.encode())
            return public_key
        else:
            return None
    
    def generate_keys(self):
        http_address = self.get_address('auth')
        socket_http = socket(AF_INET, SOCK_DGRAM)
        
        public_key = self.check_username(socket_http, http_address)
        if public_key != None:
            print('Usuario já está registrado')
            print('Digite o código de acesso para entrar (finalize com uma linha em branco):')
            while self.private_key == None:
                private_key_lines = []
                while True:
                    line = input().strip()
                    if line == '':
                        break
                    private_key_lines.append(line)
                private_key_str = '\n'.join(private_key_lines)
                try:
                    self.private_key = rsa.PrivateKey.load_pkcs1(private_key_str.encode(), format='PEM')
                    # Testa a chave privada descriptografando uma mensagem de teste
                    test_message = rsa.encrypt('test'.encode(), public_key)
                    rsa.decrypt(test_message, self.private_key)
                    print('Chave privada validada com sucesso')
                except:
                    print(f'Chave privada incorreta. Tente novamente')
                    self.private_key = None
        else:
            public_key, private_key = rsa.newkeys(512)
            self.private_key = private_key
            
            private_key_str = private_key.save_pkcs1().decode()
            print(f'Lembre-se do seu código de acesso:\n{private_key_str}')
            
            post_data = public_key.save_pkcs1().decode()
            post_request = f"POST /?name={self.nome} HTTP/1.1\n\n{post_data}"
            socket_http.sendto(post_request.encode(), http_address)
            post_response = socket_http.recv(1024).decode()
            print(post_response.split('\n\n')[1])
            socket_http.close()
    
    def start_voting(self):
        while True:
            msg = input('entrada: ')
            if msg.startswith('votar'):
                voto = msg[6:]
                signature = rsa.sign(voto.encode(), self.private_key, 'SHA-256')
                msg = f'votar {voto}:{signature.hex()}'
            
            self.enviar(msg)
            resposta = self.receber()
            print(resposta)

            status = self.receber()
            print(status)
            
            if status.startswith('Redirecionando'):
                self.enviar('sair')
                self.socket.close()
                time.sleep(1)
                redirected = False
                while not redirected:
                    try:
                        self.connect_server()
                        redirected = True
                    except:
                        redirected = False
                        print("Servidor redirecionado ainda não está disponível...")
                        time.sleep(5)
                self.enviar(self.nome)
                reception = self.receber()
                print(reception)
                
            elif status.startswith('Votacao encerrada!'):
                return

eleitor = Eleitor()
eleitor.atribuir_nome(input('Nome: '))
eleitor.generate_keys()

eleitor.connect_server()

eleitor.enviar(eleitor.nome)

reception = eleitor.receber()
print(reception)

eleitor.start_voting()
    