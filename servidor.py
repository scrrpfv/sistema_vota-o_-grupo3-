from threading import Thread
from socket import socket, AF_INET, SOCK_STREAM, SOCK_DGRAM
import time


class VotingServer:
    def __init__(self, door, max_votes):
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.socket.bind(('127.0.0.1', door))
        self.socket.listen()
        self.data_socket = socket(AF_INET, SOCK_DGRAM)
        self.data_socket.bind(('127.0.0.1', 11000 + door))
        self.max_votes = max_votes
    
    def data(self, query):
        self.data_socket.sendto(query.encode(), ('127.0.0.1', 11000 + door))
        response, _ = self.socket.recvfrom(512)
        response = response.decode()
        return response
    
    def connect_dns(self):
        query = f'new_address:votacao:127.0.0.1:{door}'
        dns_socket = socket(AF_INET, SOCK_DGRAM)
        dns_socket.sendto(query.encode(), ('127.0.0.1', 10000))
        response = dns_socket.recv(1024).decode()
        print(response)

    def check_winner(self):
        while self.vencedor == '':
            time.sleep(0.05)
            if self.total_votos == max_votes:
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
        eleitor = socket_client.recv(1024).decode() # Recebe o nome do eleitor

        if not self.data(f'IN log {eleitor}'):
            self.data(f'INSERT log {eleitor} nao_votou')
            self.data(f'INSERT conectados {eleitor} {socket_client}')
            start_msg = f'Bem vindo ao sistema de votacao, {eleitor}. Para votar no candidato 1, digite "votar 1". Para votar no candidato 2, digite "votar 2".'
            socket_client.send(start_msg.encode())
        
        else:
            if self.data(f'SELECT log eleitor')!= 'nao_votou':
                start_msg = f'Bem vindo de volta ao sistema de votacao, {eleitor}. Você já votou, aguarde os resultados.'
            else:
                start_msg = f'Bem vindo de volta ao sistema de votacao, {eleitor}. Para votar no candidato 1, digite "votar 1". Para votar no candidato 2, digite "votar 2".'
            socket_client.send(start_msg.encode())
        
        while self.data(f'SELECT vencedor') == '':
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
                elif self.data(f'IN candidatos {voto}'):
                    self.data(f'UPDATE log eleitor votou')
                    self.data(f'UPDATE candidatos voto')
                    self.data(f'UPDATE total_votos')
                    reply = f'Voce votou no candidato {voto}. '
                    print(f'Candidato {voto} recebeu um voto')

                else:
                    reply = f'Candidato {voto} é inválido, tente novamente.'
            else:
                reply = 'Mensagem inválida, Tente novamente.'
            
            socket_client.send(reply.encode())

            if self.data('SELECT total_votos') == self.max_votes:
                socket_client.send(reply.encode())
            else:
                socket_client.send('Votacao continua'.encode())
        if vencedor != '':
            self.conectados.pop(eleitor)
            print(f'{eleitor} desconectou')
            socket_client.close()

        def serve_forever(self):
            while self.data('SELECT total_votos') < self.max_votes:
                socket_client, addr_client = self.socket.accept()
                print(f'Recebendo de {addr_client}')
                Thread(target=self.handle_request, args=(socket_client,)).start()
            server_socket.close()
            print('Votacao encerrada e todos desconectados.')
