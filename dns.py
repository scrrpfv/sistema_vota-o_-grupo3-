from socket import socket, AF_INET, SOCK_DGRAM

dns_table = {}
dns_door = 10001

def handle_dns_request(query, addr, dns_socket):
    print(f'Recebendo de {addr}')

    query = query.split(':')
    if query[0] == 'new_address': # new_address:name:door
        name = query[1]
        door = query[2]
        ip = addr[0]

        server_address = (ip, int(door))
        dns_table[name] = server_address

        dns_socket.sendto('Endereco adicionado com sucesso'.encode(), addr)

        print(f'Endereco {name} adicionado com sucesso')

    elif query[0] == 'get_address': # get_address:name
        name = query[1]
        if name in dns_table:
            address = dns_table[name]
            dns_socket.sendto(f'{address[0]}:{address[1]}'.encode(), addr)
            print(f'Endereco {name} enviado com sucesso')
        else:
            dns_socket.sendto('Not Found'.encode(), addr)
            print(f'Endereco {name} nao encontrado')

dns_socket = socket(AF_INET, SOCK_DGRAM)
dns_socket.bind(('127.0.0.1', dns_door))
print('Aguardando solicitacao...')

while True:
    query, addr = dns_socket.recvfrom(512)
    query = query.decode()
    handle_dns_request(query, addr, dns_socket)