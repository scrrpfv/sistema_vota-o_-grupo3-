from socket import socket, AF_INET, SOCK_STREAM, SOCK_DGRAM
import requests
import time
import rsa


class Eleitor:
    def __init__(self):
        self.nome = None
        self.socket = None
        self.server_name = 'votacao'
        self.server_address = None
        self.private_key = None

    def get_address(self, addr_name):
        dns_address = ('127.0.0.1', 10000)
        socket_dns = socket(AF_INET, SOCK_DGRAM) # Abre socket temporário
        socket_dns.bind(('127.0.0.1', 10100))

        socket_dns.sendto(f'get_address:{addr_name}'.encode(), dns_address)
        
        socket_dns.settimeout(2)  # Define timeout para 2 segundos
        try:
            response = socket_dns.recv(1024).decode().split(':')
        except:
            return 'DNS_NOT_FOUND'
        socket_dns.close()
        
        if 'Not Found' not in response:
            self.server_address = (response[0], int(response[1]))
        
    def connect_server(self):
        while self.server_address is None:
            self.get_address(self.server_name)
            if self.server_address == 'DNS_NOT_FOUND':
                print('DNS nao encontrado')
                self.server_address = None
                time.sleep(5)
            elif self.server_address is None:
                print('Servidor nao encontrado')
                time.sleep(5)

        self.socket = socket(AF_INET, SOCK_STREAM)
        self.socket.connect(self.server_address)
        print('Conectado ao servidor')
    
    def atribuir_nome(self, nome):
        self.nome = nome
        
    def enviar(self, msg):
        self.socket.send(msg.encode())

    def receber(self):
        return self.socket.recv(1024).decode()
    
    def generate_keys(self):
        public_key, private_key = rsa.newkeys(512)
        self.private_key = private_key
        
        url = f"http://localhost:5000/?nome={self.nome}"
        post_data = public_key.save_pkcs1().decode()
        headers = {"Content-Type": "text/plain"}
        post_response = requests.post(url, data=post_data, headers=headers)
        print("Response:", post_response.text)
        

eleitor = Eleitor()
eleitor.connect_server()

reception = eleitor.receber()
print(reception)

eleitor.atribuir_nome(input('Nome: '))
eleitor.enviar(eleitor.nome)
eleitor.generate_keys()

reception = eleitor.receber()
print(reception)

resultado = ''
resposta = ''
while not resultado.startswith('Votacao encerrada') and not resposta.startswith('Votacao encerrada'):
    msg = input('entrada: ')
    eleitor.enviar(msg)
    resposta = eleitor.receber()
    print(resposta)

    resultado = eleitor.receber()
    if resultado.startswith('Votacao encerrada') or resposta.startswith('Votacao encerrada'):
        print(resultado)
        break
