from servidor import *


servidor = VotingServer()
servidor.set_door(54321)
servidor.set_max_votes(5)

servidor.connect_dns()
servidor.serve_forever()