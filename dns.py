from socket import socket, AF_INET, SOCK_DGRAM


class DnsServer:
    def __init__(self):
        self.table = {}
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.socket.bind(('127.0.0.1', 10000))
        print('Aguardando solicitacao')

    def send(self, msg, addr):
        self.socket.sendto(msg.encode(), addr)
    
    def recv(self):
        query, addr = self.socket.recvfrom(512)
        query = query.decode()
        return query, addr
    
    def handle_request(self, query, addr):
        print(f'Recebendo de {addr}')
        
        query = query.split(':')
        if query[0] == 'new_address': # new_address:name:x.x.x.x:door
            name = query[1]
            ip   = query[2]
            door = query[3]
            
            server_address = (ip, int(door))
            self.table[name] = server_address
            
            self.send('Endereco adicionado com sucesso', addr)
            print(f'Endereco {name} adicionado com sucesso')
        elif query[0] == 'get_address': # get_address:name
            name = query[1]
            if name in self.table:
                address = self.table[name]
                self.send(f'{address[0]}:{address[1]}', addr)
                print(f'Endereco {name} enviado com sucesso')
            else:
                self.send('Not Found', addr)
                print(f'Endereco {name} nao encontrado')
        else:
            dns_socket.sendto('Busca inválida'.encode(), addr)
            print('Busca inválida')

    def serve_forever(self):
        while True:
            query, addr = self.recv()
            self.handle_request(query, addr)
            print(self.table)

dns = DnsServer()
dns.serve_forever()