from threading import Thread
from socket import socket, AF_INET, SOCK_STREAM

log_eleitores = {}
eleitores_conectados = []
candidatos = {"1": 0, "2": 0}
votacao_encerrada = False

def Handle_Request(socket_client, addr_client):
    global log_eleitores
    global eleitores_conectados
    global candidatos
    global votacao_encerrada    

    log_eleitores[addr_client] = "Nao votou"
    eleitores_conectados.append(addr_client)
    if log_eleitores[addr_client] != "Nao votou":
        start_msg = "Voce ja votou, aguarde os resultados"
    else:
        start_msg = "Bem vindo ao sistema de votacao. Para votar no candidato 1, digite 'votar 1'. Para votar no candidato 2, digite 'votar 2'. Para sair do sistema, digite 'sair'."
    socket_client.send(start_msg.encode())
    
    while not votacao_encerrada:
        request = socket_client.recv(1024).decode()
        
        if request == "sair" and len(eleitores_conectados) > 1:
            break

        elif request.startswith("votar"):
            if log_eleitores[addr_client] != "Nao votou":
                reply = "Voce ja votou, aguarde os resultados."
                
            elif request.endswith("1"):
                log_eleitores[addr_client] = "Votou"
                reply = "Voce votou no candidato 1."
                print("Candidato 1 recebeu um voto")

            elif request.endswith("2"):
                log_eleitores[addr_client] = "Votou"
                reply = "Voce votou no candidato 2."
                print("Candidato 2 recebeu um voto")

            else:
                reply = "Candidato inválido, tente novamente."
        else:
            reply = "Mensagem inválida, Tente novamente."
        
        socket_client.send(reply.encode())
        if candidatos["1"] + candidatos["2"] == 15:
            votacao_encerrada = True
    
    if votacao_encerrada:
        if candidatos["1"] > candidatos["2"]:
            vencedor = "candidato 1"
        else:
            vencedor = "candidato 2"
        resultado = f"Votacao encerrada! O candidato eleito é o {vencedor}"
        socket_client.send(reply.encode())
    
    eleitores_conectados.remove(addr_client)
    socket_client.close()


server_socket = socket(AF_INET, SOCK_STREAM)
server_socket.bind(('127.0.0.1', 12345))
server_socket.listen()
print('Aguardando solicitacao...')

while not votacao_encerrada:
    socket_client, addr_client = server_socket.accept()
    print(f'Recebendo de {addr_client}')
    Thread(target=Handle_Request, args=(socket_client, addr_client)).start()

while len(eleitores_conectados) > 0:
    pass

print("Votacao encerrada e todos desconectados.")
        
    
