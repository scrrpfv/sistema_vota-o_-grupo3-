from socket import socket, AF_INET, SOCK_STREAM

socket_client = socket(AF_INET, SOCK_STREAM)
socket_client.connect(('127.0.0.1', 12345))

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
