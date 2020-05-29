import time
from estim2b import Estim


e2b = Estim(verbose=2)

# Can add commands to queue before the thread is started
# but only if those are non-blocking e.g.:
# e2b.set_output("A", 100)
# e2b.start()
# print(e2b.get_status())

e2b.set_output("A", 100, block=True)

