from threading import Thread
from socket import socket, AF_INET, SOCK_STREAM
import time

log_eleitores = {}
eleitores_conectados = []
candidatos = {"1": 0, "2": 0}
vencedor = ""
total_votos = 0


def Check_Winner():
    global candidatos
    global vencedor
    global total_votos

    while vencedor == "":
        time.sleep(0.05)
        if total_votos == 3:
            if candidatos["1"] > candidatos["2"]:
                vencedor = "candidato 1"
            elif candidatos["2"] > candidatos["1"]:
                vencedor = "candidato 2"
            print(f"Votacao encerrada! O candidato eleito é o {vencedor}")
    return


def Handle_Request(socket_client, addr_client):
    global log_eleitores
    global eleitores_conectados
    global candidatos
    global vencedor
    global total_votos

    log_eleitores[addr_client] = "Nao votou"
    eleitores_conectados.append(addr_client)
    if log_eleitores[addr_client] != "Nao votou":
        start_msg = "Voce ja votou, aguarde os resultados"
    else:
        start_msg = "Bem vindo ao sistema de votacao. Para votar no candidato 1, digite 'votar 1'. Para votar no candidato 2, digite 'votar 2'. Para sair do sistema, digite 'sair'."
    socket_client.send(start_msg.encode())
    
    while vencedor == "":
        request = socket_client.recv(1024).decode()
        reply = ""
        
        if request == "sair":
            if len(eleitores_conectados) > 1:
                break
            else:
                reply = "Nao e possivel sair, pois e o unico eleitor conectado."

        elif request.startswith("votar"):
            voto = request[6:]
            if log_eleitores[addr_client] != "Nao votou":
                reply = "Voce ja votou, aguarde os resultados."
            elif voto in candidatos:
                log_eleitores[addr_client] = "Votou"
                candidatos[voto] += 1
                total_votos += 1
                reply = f'Voce votou no candidato {voto}. '
                print(f'Candidato {voto} recebeu um voto')

            else:
                reply = f'Candidato {voto} é inválido, tente novamente.'
        else:
            reply = "Mensagem inválida, Tente novamente."
        
        time.sleep(0.1)
        if vencedor != "":
            break

        socket_client.send(reply.encode())
    
    if vencedor == "":
        reply = "dc Voce foi desconectado."
    else:
        if reply.endswith(" "):
            reply = f'dc {reply}Votacao encerrada! O candidato eleito é o {vencedor}'
        else:
            reply = f'dc Votacao encerrada! O candidato eleito é o {vencedor}'
    socket_client.send(reply.encode())
    eleitores_conectados.remove(addr_client)
    socket_client.close()
    return

Thread(target=Check_Winner).start()
server_socket = socket(AF_INET, SOCK_STREAM)
server_socket.bind(('127.0.0.1', 12345))
server_socket.listen()
print('Aguardando solicitacao...')

while vencedor == "":
    socket_client, addr_client = server_socket.accept()
    print(f'Recebendo de {addr_client}')
    Thread(target=Handle_Request, args=(socket_client, addr_client)).start()
    print(vencedor, candidatos, eleitores_conectados)

while len(eleitores_conectados) > 0:
    print("Eleitores conectados: ", eleitores_conectados)
    time.sleep(1)

print("Votacao encerrada e todos desconectados.")