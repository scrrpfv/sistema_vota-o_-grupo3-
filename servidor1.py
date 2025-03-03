from servidor import *


servidor = VotingServer(12345, 2)
servidor.connect_dns()
servidor.serve_forever()