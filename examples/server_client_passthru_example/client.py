import time
from estim2b import EstimSocket

client = EstimSocket()
client.client_connect()

while True:
    time.sleep(0.1)

    command = raw_input('Enter E-stim 2B compatible command: ')
    client.client_send('{}'.format(command))

