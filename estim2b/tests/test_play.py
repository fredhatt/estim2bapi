import time
from estim2b import Estim
from estim2b import play


e2b = Estim(verbose=2)
e2b.start()
print(e2b.get_status())

play.jolt(e2b, 100, 3.5)
print("jolting now for 3.5s")
time.sleep(8)

play.jolt(e2b, 50, 3.5, block=True)
print("did just do a 3.5s jolt at 50%")
print(5)

play.jolt(e2b, 25, 3.5, mode="bounce", power="L")
print("3.5s jolt, 25% on Bounce mode (low power).")
# time.sleep(7)


print("Ramping up....")
play.ramp(e2b, 0, 30, 1)
print("Ramping back down...")
play.ramp(e2b, 30, 0, 1, block=True)


e2b.stop()