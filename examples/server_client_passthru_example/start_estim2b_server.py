from optparse import OptionParser
from estim2b import EstimSocket
from estim2b import Estim

e2b = Estim('/dev/ttyUSB0')

def callback_command_passthru(buf, address):
    e2b.send(buf)

def set_outputs_to_zero():
    e2b.kill()

server = EstimSocket()
server.start_server(callbacks=[callback_command_passthru], on_close=e2b.kill)

