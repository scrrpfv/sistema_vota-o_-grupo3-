from threading import Thread, Lock
from socket import socket, AF_INET, SOCK_STREAM, SOCK_DGRAM
import time

nvotos_fim = 5
data_lock = Lock()

class VotingServer:
    def __init__(self):
        self.door = None
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.data_socket = socket(AF_INET, SOCK_DGRAM)
        self.max_votes = None
    
    def set_door(self, door):
        self.door = door
        self.socket.bind(('127.0.0.1', door))
        self.socket.listen()
        self.data_socket.bind(('127.0.0.1', 11000 + door))
    
    def set_max_votes(self, max_votes):
        self.max_votes = max_votes
    
    def data(self, query):
        with data_lock:
            self.data_socket.sendto(query.encode(), ('127.0.0.1', 11000))
            response, _ = self.data_socket.recvfrom(512)
            response = response.decode()
            try:
                return int(response)
            except ValueError:
                return response
    
    def connect_dns(self):
        query = f'new_address:votacao:127.0.0.1:{self.door}'
        dns_socket = socket(AF_INET, SOCK_DGRAM)
        dns_socket.sendto(query.encode(), ('127.0.0.1', 10000))
        response = dns_socket.recv(1024).decode()
        print(response)

    def handle_request(self, socket_client):
        eleitor = socket_client.recv(1024).decode() # Recebe o nome do eleitor

        if not self.data(f'IN log {eleitor}') == 'True':
            self.data(f'INSERT log {eleitor} nao_votou')
            self.data(f'INSERT conectados {eleitor} {socket_client}')
            start_msg = f'Bem vindo ao sistema de votacao, {eleitor}. Para votar no candidato 1, digite "votar 1". Para votar no candidato 2, digite "votar 2".'
            socket_client.send(start_msg.encode())
            
        else:
            if self.data(f'SELECT log {eleitor}')!= 'nao_votou':
                start_msg = f'Bem vindo de volta ao sistema de votacao, {eleitor}. Você já votou, aguarde os resultados.'
            else:
                start_msg = f'Bem vindo de volta ao sistema de votacao, {eleitor}. Para votar no candidato 1, digite "votar 1". Para votar no candidato 2, digite "votar 2".'
            socket_client.send(start_msg.encode())

        while self.data('SELECT total_votos') < self.max_votes:
            request = socket_client.recv(1024).decode()
            if request == 'sair' and self.data(f'SELECT log {eleitor}') != 'nao_votou':
                if self.data(f'LEN conectados') > 1:
                    break
                else:
                    reply = 'Nao e possivel sair, pois e o unico eleitor conectado.'

            elif request.startswith('votar'):
                voto = request[6:]
                if self.data(f'SELECT log {eleitor}') != 'nao_votou':
                    reply = 'Voce ja votou, aguarde os resultados.'
                elif self.data(f'IN candidatos {voto}') == 'True':
                    self.data(f'UPDATE log {eleitor} votou')
                    self.data(f'UPDATE candidatos {voto}')
                    self.data(f'UPDATE total_votos')
                    reply = f'Voce votou no candidato {voto}. '
                    print(f'Candidato {voto} recebeu um voto')

                else:
                    reply = f'Candidato {voto} é inválido, tente novamente.'
            else:
                reply = 'Mensagem inválida, Tente novamente.'
            
            socket_client.send(reply.encode())

            if self.data('SELECT total_votos') == self.max_votes:
                # Se ainda não chegou no numero de votos final, redireciona
                if self.max_votes < nvotos_fim:
                    status = 'Redirecionando para um novo servidor.'
                # Se chegou no numero de votos final, finaliza a votação.
                else: 
                    votos1, votos2 = self.data('SELECT candidatos 1'), self.data('SELECT candidatos 2')
                    if votos1 > votos2:
                        vencedor = 'candidato 1'
                    else:
                        vencedor = 'candidato 2'
                    self.data(f'UPDATE vencedor {vencedor}')
                    status = f'Votacao encerrada! O candidato vencedor é o {vencedor}'
            else:
                status = 'Votacao continua'
            socket_client.send(status.encode())
        self.data(f'DELETE conectados {eleitor}')
        socket_client.close()
        print(f'{eleitor} foi desconectado')

    def serve_forever(self):
        print('Aguardando solicitacoes...')
        while self.data('SELECT total_votos') < self.max_votes:
            socket_client, addr_client = self.socket.accept()
            print(f'Recebendo de {addr_client}')
            Thread(target=self.handle_request, args=(socket_client,)).start()
        self.socket.close()
        print('Votacao encerrada e todos desconectados.')