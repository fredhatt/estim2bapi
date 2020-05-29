import time
from estim2b import Estim

test_value_ = 11

e2b = Estim(recv_responses=True, verbose=2)
e2b.start()
print(e2b.get_status())
r = e2b.set_output(channel="A", value=test_value_, block=True)
status = e2b.get_status()

assert status["A"] == 2 * test_value_
print(f"Passed: set channel A to {test_value_}")

time.sleep(1)
print()

r = e2b.set_output(channel="A", value=0, block=True)
print(":", e2b.status)
assert e2b.status["A"] == 0
print(f"Passed: set channel A to {test_value_}")

print("Passed all.")
