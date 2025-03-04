from servidor import *

socket_intercom = socket(AF_INET, SOCK_DGRAM)
socket_intercom.bind(('127.0.0.1', 16001))

start_server, _ = socket_intercom.recvfrom(512)

servidor = VotingServer()
servidor.set_door(16000)
servidor.set_max_votes(5)

servidor.connect_dns()
servidor.serve_forever()