from threading import Thread
from socket import socket, AF_INET, SOCK_STREAM
import time

log_eleitores = {}
eleitores_conectados = {}
candidatos = {"1": 0, "2": 0}
vencedor = ""
total_votos = 0


def check_winner():
    global candidatos
    global vencedor
    global total_votos
    global eleitores_conectados

    while vencedor == "":
        time.sleep(0.05)
        if total_votos == 3:
            if candidatos["1"] > candidatos["2"]:
                vencedor = "candidato 1"
            elif candidatos["2"] > candidatos["1"]:
                vencedor = "candidato 2"
            reply = f'Votacao encerrada! O candidato eleito é o {vencedor}'

            for addr_client in list(eleitores_conectados):
                socket_client = eleitores_conectados[addr_client]
                socket_client.send(reply.encode())
            print(reply)


def handle_request(socket_client, addr_client):
    global log_eleitores
    global eleitores_conectados
    global candidatos
    global vencedor
    global total_votos

    start_msg = "Digite seu nome para se conectar ao sistema de votacao:"
    socket_client.send(start_msg.encode())
    eleitor = socket_client.recv(1024).decode()

    if eleitor not in log_eleitores:
        log_eleitores[eleitor] = "Nao votou"
        eleitores_conectados[eleitor] = socket_client
        start_msg = f"Bem vindo ao sistema de votacao, {eleitor}. Para votar no candidato 1, digite 'votar 1'. Para votar no candidato 2, digite 'votar 2'."
        socket_client.send(start_msg.encode())
    
    else:
        if log_eleitores[eleitor] != "Nao votou":
            start_msg = f"Bem vindo de volta ao sistema de votacao, {eleitor}. Você já votou, aguarde os resultados."
        else:
            start_msg = f"Bem vindo de volta ao sistema de votacao, {eleitor}. Para votar no candidato 1, digite 'votar 1'. Para votar no candidato 2, digite 'votar 2'."
        socket_client.send(start_msg.encode())
    
    while vencedor == "":
        request = socket_client.recv(1024).decode()
        if request == "sair" and log_eleitores[addr_client] != "Nao votou":
            if len(eleitores_conectados) > 1:
                break
            else:
                reply = "Nao e possivel sair, pois e o unico eleitor conectado."

        elif request.startswith("votar"):
            voto = request[6:]
            if log_eleitores[eleitor] != "Nao votou":
                reply = "Voce ja votou, aguarde os resultados."
            elif voto in candidatos:
                log_eleitores[eleitor] = "Votou"
                candidatos[voto] += 1
                total_votos += 1
                reply = f'Voce votou no candidato {voto}. '
                print(f'Candidato {voto} recebeu um voto')

            else:
                reply = f'Candidato {voto} é inválido, tente novamente.'
        else:
            reply = "Mensagem inválida, Tente novamente."
        
        socket_client.send(reply.encode())
        
        time.sleep(0.1)
        if vencedor != "":
            break
        else:
            socket_client.send('Votacao continua'.encode())
    if vencedor != "":
        eleitores_conectados.pop(eleitor)
        print(f'{eleitor} desconectou')
        socket_client.close()

server_socket = socket(AF_INET, SOCK_STREAM)
server_socket.bind(('127.0.0.1', 12345))
server_socket.listen()
print('Aguardando solicitacao...')
Thread(target=check_winner).start()

while vencedor == "":
    socket_client, addr_client = server_socket.accept()
    print(f'Recebendo de {addr_client}')
    Thread(target=handle_request, args=(socket_client, addr_client)).start()
server_socket.close()
print("Votacao encerrada e todos desconectados.")