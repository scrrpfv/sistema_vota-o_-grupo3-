from servidor import *

socket_intercom = socket(AF_INET, SOCK_DGRAM)
socket_intercom.bind(('127.0.0.1', 15001))

servidor = VotingServer()
servidor.set_door(15000)
servidor.set_max_votes(2)

servidor.register_dns(servidor.door)
servidor.serve_forever()

print('Redirecionando para o servidor 2')
socket_intercom.sendto('start'.encode(), ('127.0.0.1', 16001))
print('Redirecionamento concluido')