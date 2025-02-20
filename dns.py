from socket import socket, AF_INET, SOCK_DGRAM

dns_table = {}
dns_address = ('127.0.0.1', 10000)


def handle_dns_request(query, addr, dns_socket):
    print(f'Recebendo de {addr}')

    query = query.split(':')
    if query[0] == 'new_address': # new_address:name:x.x.x.x:door
        name = query[1]
        ip   = query[2]
        door = query[3]

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
    
    else:
        dns_socket.sendto('Busca inválida'.encode(), addr)
        print('Busca inválida')


dns_socket = socket(AF_INET, SOCK_DGRAM)
dns_socket.bind(dns_address)
print('Aguardando solicitacao...')

while True:
    query, addr = dns_socket.recvfrom(512)
    query = query.decode()
    handle_dns_request(query, addr, dns_socket)
    print(dns_table)