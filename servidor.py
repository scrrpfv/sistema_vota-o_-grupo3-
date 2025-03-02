from threading import Thread
from socket import socket, AF_INET, SOCK_STREAM, SOCK_DGRAM
import time

dns_address = ('127.0.0.1', 10000)

class VotingServer:
    def __init__(self):
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.socket.bind(('127.0.0.1', 12345))
        self.socket.listen()
        self.log = {}
        self.conectados = {}
        self.candidatos = {'1': 0, '2': 0}
        self.vencedor = ''
        self.total_votos = 0
    
    def connect_dns(self):
        query = f'new_address:votacao:127.0.0.1:12345'
        dns_socket = socket(AF_INET, SOCK_DGRAM)
        dns_socket.sendto(query.encode(), ('127.0.0.1', 10000))
        response = dns_socket.recv(1024).decode()
        print(response)

    def check_winner(self):
        while self.vencedor == '':
            time.sleep(0.05)
            if self.total_votos == 3:
                if self.candidatos['1'] > self.candidatos['2']:
                    self.vencedor = 'candidato 1'
                elif self.candidatos['2'] > self.candidatos['1']:
                    self.vencedor = 'candidato 2'
                reply = f'Votacao encerrada! O candidato eleito é o {vencedor}'

                for addr_client in list(self.eleitores_conectados):
                    socket_client = self.eleitores_conectados[addr_client]
                    socket_client.send(reply.encode())
                print(reply)

    def handle_request(self, socket_client):
        start_msg = 'Digite seu nome para se conectar ao sistema de votacao:'
        socket_client.send(start_msg.encode())
        eleitor = socket_client.recv(1024).decode()

        if eleitor not in self.log:
            self.log[eleitor] = 'Nao votou'
            self.conectados[eleitor] = socket_client
            start_msg = f'Bem vindo ao sistema de votacao, {eleitor}. Para votar no candidato 1, digite "votar 1". Para votar no candidato 2, digite "votar 2".'
            socket_client.send(start_msg.encode())
        
        else:
            if self.log[eleitor] != 'Nao votou':
                start_msg = f'Bem vindo de volta ao sistema de votacao, {eleitor}. Você já votou, aguarde os resultados.'
            else:
                start_msg = f'Bem vindo de volta ao sistema de votacao, {eleitor}. Para votar no candidato 1, digite "votar 1". Para votar no candidato 2, digite "votar 2".'
            socket_client.send(start_msg.encode())
        
        while self.vencedor == '':
            request = socket_client.recv(1024).decode()
            if request == 'sair' and self.log[eleitor] != 'Nao votou':
                if len(self.conectados) > 1:
                    break
                else:
                    reply = 'Nao e possivel sair, pois e o unico eleitor conectado.'

            elif request.startswith('votar'):
                voto = request[6:]
                if self.log[eleitor] != 'Nao votou':
                    reply = 'Voce ja votou, aguarde os resultados.'
                elif voto in self.candidatos:
                    self.log[eleitor] = 'Votou'
                    self.candidatos[voto] += 1
                    self.total_votos += 1
                    reply = f'Voce votou no candidato {voto}. '
                    print(f'Candidato {voto} recebeu um voto')

                else:
                    reply = f'Candidato {voto} é inválido, tente novamente.'
            else:
                reply = 'Mensagem inválida, Tente novamente.'
            
            socket_client.send(reply.encode())
            
            time.sleep(0.1)
            if self.vencedor != '':
                break
            else:
                socket_client.send('Votacao continua'.encode())
        if vencedor != '':
            self.conectados.pop(eleitor)
            print(f'{eleitor} desconectou')
            socket_client.close()

servidor = VotingServer()
servidor.connect_dns()

print('Aguardando solicitacao...')
Thread(target=servidor.check_winner).start()

while servidor.vencedor == '':
    socket_client, addr_client = servidor.socket.accept()
    print(f'Recebendo de {addr_client}')
    Thread(target=servidor.handle_request, args=(socket_client,)).start()
server_socket.close()
print('Votacao encerrada e todos desconectados.')