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
        return query, addr
    
    def handle_request(self, q, addr): # COMMAND variable_name data(if any)
        q = q.split(' ')
        if q[0] == 'INSERT':
            if q[1] == 'log':
                self.log[q[2]] = q[3]
            elif q[1] == 'conectados':
                self.conectados[q[2]] = q[3]
            self.send('ok', addr)
                
        elif q[0] == 'UPDATE':
            if q[1] == 'log':
                self.log[q[2]] = q[3]
            elif q[1] == 'candidatos':
                if q[2] == '1':
                    candidatos[1] += 1
                elif q[2] == '2':
                    candidatos[2] += 1
            elif q[1] == 'vencedor':
                self.vencedor = q[2]
            elif q[1] == 'total_votos':
                self.total_votos += 1
            self.send('ok', addr)
        
        elif q[0] == 'DELETE':
            if q[1] == 'conectados':
                if q[2] in self.conectados:
                    self.conectados.pop[q[2]]
            self.send('ok', addr)
        
        elif q[0] == 'SELECT':
            if q[1] == 'log':
                if q[2] in self.log:
                    self.send(self.log[q[2]], addr)
                else:
                    self.send('', addr)
            elif q[1] == 'conectados':
                if q[2] in self.conectados:
                    self.send(self.conectados[q[2]], addr)
                else:
                    self.send('', addr)
            elif q[1] == 'candidatos':
                if q[2] in self.candidatos:
                    self.send(self.candidatos[q[2]], addr)
                else:
                    self.send('', addr)
            elif q[1] == 'vencedor':
                self.send(self.vencedor, addr)
            elif q[1] == 'total_votos':
                self.send(self.total_votos, addr)
        
        elif q[0] == 'IN':
            if q[1] == 'log':
                self.send(q[2] in self.log, addr)
            elif q[1] == 'conectados':
                self.send(q[2] in self.conectados, addr)
            elif q[1] == 'candidatos':
                self.send(q[2] in self.candidatos, addr)
        
        elif q[1] == 'LEN':
            if q[1] == 'log':
                self.send(len(self.log), addr)
            elif q[1] == 'conectados':
                self.send(len(self.conectados), addr)
        
        else:
            self.send(f'Comando {q[0]} inexistente.', addr)
    
    def serve_forever(self):
        print('Aguardando solicitacao...')
        while True:
            query, addr = self.recv()
            self.handle_request(query, addr)
            
base_dados = DataBase()
base_dados.serve_forever()