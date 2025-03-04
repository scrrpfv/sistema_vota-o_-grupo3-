from socket import socket, AF_INET, SOCK_DGRAM


class DataBase:
    def __init__(self):
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.socket.bind(('127.0.0.1', 11000))
        self.log = {}
        self.conectados = {}
        self.candidatos = {'1': 0, '2': 0}
        self.vencedor = ''
        self.total_votos = 0
    
    def send(self, msg, addr):
        self.socket.sendto(str(msg).encode(), addr)
        print(str(msg) + ' enviado')
    
    def recv(self):
        query, addr = self.socket.recvfrom(512)
        query = query.decode()
        print('query: ' + query)
        return query, addr
    
    def handle_request(self, q, addr): # COMMAND variable_name data(if any)
        q = q.split(' ')
        if q[0] == 'INSERT':
            if q[1] == 'log':
                self.log[q[2]] = q[3]
            elif q[1] == 'conectados':
                self.conectados[q[2]] = q[3]
            response = 'ok'
                
        elif q[0] == 'UPDATE':
            if q[1] == 'log':
                self.log[q[2]] = q[3]
            elif q[1] == 'candidatos':
                if q[2] == '1':
                    self.candidatos['1'] += 1
                elif q[2] == '2':
                    self.candidatos['2'] += 1
            elif q[1] == 'vencedor':
                self.vencedor = q[2]
            elif q[1] == 'total_votos':
                self.total_votos += 1
            response = 'ok'
        
        elif q[0] == 'DELETE':
            if q[1] == 'conectados':
                if q[2] in self.conectados:
                    self.conectados.pop(q[2])
            response = 'ok'
        
        elif q[0] == 'SELECT':
            if q[1] == 'log':
                if q[2] in self.log:
                    response = self.log[q[2]]
                else:
                    response = ''
            elif q[1] == 'conectados':
                if q[2] in self.conectados:
                    response = self.conectados[q[2]]
                else:
                    response = ''
            elif q[1] == 'candidatos':
                if q[2] in self.candidatos:
                    response = self.candidatos[q[2]]
                else:
                    response = ''
            elif q[1] == 'vencedor':
                response = self.vencedor
            elif q[1] == 'total_votos':
                response = self.total_votos
        
        elif q[0] == 'IN':
            if q[1] == 'log':
                response = q[2] in self.log
            elif q[1] == 'conectados':
                response = q[2] in self.conectados
            elif q[1] == 'candidatos':
                response = q[2] in self.candidatos
        
        elif q[0] == 'LEN':
            if q[1] == 'log':
                response = len(self.log)
            elif q[1] == 'conectados':
                response = len(self.conectados)
        
        else:
            response = f'Comando {q[0]} inexistente.'
        
        self.send(response, addr)
    
    def serve_forever(self):
        print('Aguardando solicitacao...')
        while True:
            query, addr = self.recv()
            self.handle_request(query, addr)
            
base_dados = DataBase()
base_dados.serve_forever()