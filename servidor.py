from threading import Thread, Lock
from socket import socket, AF_INET, SOCK_STREAM, SOCK_DGRAM
import time
import rsa

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
            while True:
                self.data_socket.sendto(query.encode(), ('127.0.0.1', 11000))
                try:
                    response, _ = self.data_socket.recvfrom(512)
                    break
                except:
                    print('Servidor de dados nao encontrado')
                    time.sleep(5)
            response = response.decode()
            try:
                return int(response)
            except ValueError:
                return response
    
    def register_dns(self, door):
        dns_address = ('127.0.0.1', 10000)
        socket_dns = socket(AF_INET, SOCK_DGRAM)    # Abre socket temporário
        socket_dns.settimeout(2)    # Define timeout para 2 segundos
        
        response = None
        while response is None:
            socket_dns.sendto(f'new_address:votacao:127.0.0.1:{door}'.encode(), dns_address)
            try:
                response = socket_dns.recv(1024).decode()
            except:
                print('DNS nao encontrado')
            
            if response == 'Endereco adicionado com sucesso':
                socket_dns.close()
                print(response)
                return
            time.sleep(5)

    def get_address(self, addr_name):
        dns_address = ('127.0.0.1', 10000)
        socket_dns = socket(AF_INET, SOCK_DGRAM)    # Abre socket temporário
        socket_dns.settimeout(2)    # Define timeout para 2 segundos
        
        response = None
        while response is None:
            socket_dns.sendto(f'get_address:{addr_name}'.encode(), dns_address)
            try:
                response = socket_dns.recv(1024).decode().split(':')
            except:
                print('DNS nao encontrado')
            
            if response is not None:
                if 'Not Found' in response:
                    print('Servidor nao encontrado')
                    response = None
                else:
                    socket_dns.close()
                    return (response[0], int(response[1]))
            time.sleep(5)
    
    def auth_vote(self, voto, assinatura, nome):
        auth_address = self.get_address('auth')
        auth_socket = socket(AF_INET, SOCK_DGRAM)
        
        auth_socket.sendto(f'GET /?name={nome} HTTP/1.1'.encode(), auth_address)
        get_response = auth_socket.recv(1024).decode()
        
        if get_response.startswith('HTTP/1.1 200 OK'):
            public_key_str = get_response.split('\n\n')[1]
            public_key = rsa.PublicKey.load_pkcs1(public_key_str.encode())
            try:
                cifra = rsa.verify(voto.encode(), bytes.fromhex(assinatura), public_key)
            except:
                print('Chave pública inválida')
                cifra = None
        else:
            print('Chave pública não encontrada')
            cifra = None
        
        if cifra != 'SHA-256':
            return '0'
        return voto
        
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
                cifra = request[6:].split(':')
                voto = cifra[0]
                assinatura = cifra[1]
                voto = self.auth_vote(voto, assinatura, eleitor)
                if self.data(f'SELECT log {eleitor}') != 'nao_votou':
                    reply = 'Voce ja votou, aguarde os resultados.'
                elif self.data(f'IN candidatos {voto}') == 'True':
                    self.data(f'UPDATE log {eleitor} votou')
                    self.data(f'UPDATE candidatos {voto}')
                    self.data(f'UPDATE total_votos')
                    reply = f'Voce votou no candidato {voto}. '
                    print(f'Candidato {voto} recebeu um voto')
                elif voto == None:
                    reply = 'Erro com a autenticação.'
                else:
                    reply = f'Candidato {voto} é inválido, tente novamente.'
            else:
                reply = 'Mensagem inválida, Tente novamente.'
            
            socket_client.send(reply.encode())
            
            vencedor = self.data('SELECT vencedor')
            if vencedor != '':
                status = f'Votacao encerrada! O candidato vencedor é o {vencedor}'
            elif self.data('SELECT total_votos') == self.max_votes:
                # Se ainda não chegou no numero de votos final, redireciona
                if self.max_votes < nvotos_fim:
                    status = 'Redirecionando para um novo servidor.'
                    self.register_dns(16000)
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
        self.socket.settimeout(2)
        while self.data('SELECT total_votos') < self.max_votes:
            try:
                socket_client, addr_client = self.socket.accept()
            except:
                continue
            print(f'Recebendo de {addr_client}')
            Thread(target=self.handle_request, args=(socket_client,)).start()
        self.socket.close()
        print('Votacao encerrada e todos desconectados.')