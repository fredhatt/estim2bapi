from adxl345 import ADXL345
import time
import numpy as np  
from collections import deque
from optparse import OptionParser
from estim2b import EstimSocket


parser = OptionParser()
parser.add_option('--sleep', help='The time (s) to sleep between each send to the server.',
                  dest='sleep', default=0.1, type=float)

parser.add_option('--address', help='The IP address of the server',
                  dest='address', default="192.168.0.5", type=str)

parser.add_option('--port', help='The server port',
                  dest='port', default=8089, type=int)

opts, args = parser.parse_args()


'''
By default the range is set to 2G, which is good for most applications.
'''
adxl345 = ADXL345()


def get_axes():
    axes = adxl345.getAxes(gforce=True)
    '''
    We send 4 pieces of information, the current time (which can be used to work out the lag)
    and the x, y, z readings from the accelerometer
    '''
    x = "{},{},{},{}".format(time.time(), axes['x'], axes['y'], axes['z'])
    return x



client = EstimSocket(address=opts.address, port=opts.port)
client.client_connect()

while True:

    time.sleep(opts.sleep)
    x = get_axes()
    client.client_send(x)
    


