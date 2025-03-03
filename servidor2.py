from servidor import *


servidor = VotingServer(54321, 5)
servidor.connect_dns()
servidor.serve_forever()