from socket import socket, AF_INET, SOCK_STREAM

while True:
    socket_client = socket(AF_INET, SOCK_STREAM)
    socket_client.connect(('127.0.0.1', 12345))
    while True:
        msg = input('entrada: ')
        socket_client.send(msg.encode())
        resposta = socket_client.recv(1024).decode()
        print(resposta)
