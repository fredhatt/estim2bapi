import socket, traceback
from motion import History

hist = History()


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
    print address[0],
    print hist.calc_velocity(),
    print hist.calc_angles(-1)


host = ''
port = 5555

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
s.bind((host, port))

while 1:
  try:
    message, address = s.recvfrom(8192)
    #print message
    callback_history(message, address)
  except (KeyboardInterrupt, SystemExit):
    raise
  except:
    traceback.print_exc()
