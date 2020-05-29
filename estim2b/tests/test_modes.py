import time
from estim2b import Estim


e2b = Estim(recv_responses=True, verbose=2)
e2b.start()
print(e2b.get_status())

print("Check display on 2B for correct mode...")

for mode in e2b.available_modes:
    print(mode)
    e2b.set_mode(mode, block=True)
    time.sleep(1.5)


print("Testing high/low modes...")
e2b.set_low(block=True)
time.sleep(2)
e2b.set_high(block=True)

e2b.link_channels(block=True)
e2b.set_output("A", 100)
time.sleep(2)
e2b.kill(instant=True, block=True)

e2b.stop()