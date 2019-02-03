from optparse import OptionParser
from estim2b import EstimSocket
from estim2b import Estim
from collections import deque
import time
import numpy as np
from optparse import OptionParser
from motion import History
from estim2b import Jolt
import sys

parser = OptionParser()
parser.add_option('--motion-tol', help='The tolerance on motion trigger events.',
                  dest='motiontol', default=1.25, type=float)

parser.add_option('--motion-std', help='Overides motion calibration.',
                  dest='motionstd', type=float)

parser.add_option('--angle-tol', help='The tolerance on angle trigger events.',
                  dest='angtol', default=3.0, type=float)

parser.add_option('--angle-std', help='Overides angle calibration.',
                  dest='angstd', type=float)

parser.add_option('--grace-time', help='Number of seconds to recover posture.',
                  dest='gtime', default=3.0, type=float)

parser.add_option('--jolt-time', help='Duration of the jolt',
                  dest='jtime', default=3.5, type=float)

parser.add_option('--jolt-power', help='Power of the jolt',
                  dest='jpower', default=3, type=int)

parser.add_option('--device', help='COM device of Estim 2B hardware',
                  dest='device', default='auto', type=str)

opts, args = parser.parse_args()

if opts.angstd is not None and not opts.angtol == 1.0:
    print()
    print('--angle-std has been set but --angle-tol is not 1')
    print('Note that angle-std will be multiplied by angle-tol.')
    print('(when overiding angle-std like this it is usually best to set angle-tol to 1)')
    print()

print('Read command-line arguments:')
print(opts)
print()

e2b = Estim(opts.device)

jolt = Jolt(e2b, verbose=True)

hist = History()

#outfile = open('xyz.log', 'w')

def callback_history(buf, address):

    try:
        dat = buf.split(',')
        t = float(dat[0].strip())
        x = float(dat[2].strip())
        y = float(dat[3].strip())
        z = float(dat[4].strip())
        valid = True
    except:
        sys.stderr.write('received malformed buffer: {}'.format(buf))
        valid = False
    
    if not valid: return False

    hist.record(t, x, y, z)


def callback_velocity(buf, address):
    # Assumes callback_history ran before it
    
    if hist.counter == hist.max_length:
        vel_means, vel_stds = hist.calibrate_velocities(opts.motionstd)
        print('Calibrated')
        print('  mean movement:', vel_means)
        print('  stdd movement:', vel_stds)
        print()

    if hist.counter >= hist.max_length:
        if hist.test_velocity_trigger(opts.motiontol):
            print('moved at step {}'.format(hist.counter))
            jolt(jtime=opts.jtime, jpower=opts.jpower, gtime=opts.gtime)

    return True
        


def callback_level(buf, address):
    # Assumes callback_history ran before it
    
    if hist.counter == hist.max_length:
        angle_means, angle_stds = hist.calibrate_angles(opts.angstd) 
        print('Calibrated')
        print('  mean angles:', angle_means)
        print('  stdd angles:', angle_stds)
        print()

    if hist.counter >= hist.max_length:
        if hist.test_angle_trigger(opts.angtol):
            print('Unlevel at {}'.format(hist.counter))
            jolt(jtime=opts.jtime, jpower=opts.jpower, gtime=opts.gtime)

    return True



server = EstimSocket(verbose=False, udp=True)
server.start_server(callbacks=[callback_history, callback_velocity, callback_level], on_close=e2b.kill)

