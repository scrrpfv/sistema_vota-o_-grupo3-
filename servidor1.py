from servidor import *


servidor = VotingServer()
servidor.set_door(12344)
servidor.set_max_votes(2)

servidor.connect_dns()
servidor.serve_forever()