from socket import socket, AF_INET, SOCK_STREAM, SOCK_DGRAM
import requests
import time
import rsa


def get_address(name):
    dns_address = ('127.0.0.1', 10000)
    socket_dns = socket(AF_INET, SOCK_DGRAM)
    socket_dns.bind(('127.0.0.1', 10100))

    socket_dns.sendto(f'get_address:{name}'.encode(), dns_address)
    
    socket_dns.settimeout(2)  # set a timeout of 2 seconds
    try:
        response = socket_dns.recv(1024).decode().split(':')
    except:
        return 'DNS_NOT_FOUND'
    socket_dns.close()
    
    if 'Not Found' in response:
        return None

    server_address = (response[0], int(response[1]))
    return server_address


def connect_server(server_name):
    server_address = None
    while server_address is None:
        server_address = get_address(server_name)
        if server_address == 'DNS_NOT_FOUND':
            print('DNS nao encontrado')
            server_address = None
        elif server_address is None:
            print('Servidor nao encontrado')
        time.sleep(5)

    socket_client = socket(AF_INET, SOCK_STREAM)
    socket_client.connect(server_address)
    print('Conectado ao servidor')
    return socket_client


socket_client = connect_server('votacao')

reception = socket_client.recv(1024).decode()
print(reception)
nome = input('')
socket_client.send(nome.encode())

reception = socket_client.recv(1024).decode()
print(reception)

resultado = ''
resposta = ''
while not resultado.startswith('Votacao encerrada') and not resposta.startswith('Votacao encerrada'):
    msg = input('entrada: ')
    socket_client.send(msg.encode())
    resposta = socket_client.recv(1024).decode()
    print(resposta)

    resultado = socket_client.recv(1024).decode()
    if resultado.startswith('Votacao encerrada') or resposta.startswith('Votacao encerrada'):
        print(resultado)
        break
