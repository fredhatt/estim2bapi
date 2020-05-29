import time

from estim2b import Estim

def jolt(e2b, level, jolt_time, mode=None, power=None, block=False):
    '''
    Increase the output level, and optionally mode/power for a set time period.
    e2b: A running instance of Estim.
    level: the output level for channels A and B.
    jolt_time: the length of time to increase output for before it's set to 0.
    mode: the mode to use, if not None. If None existing mode is used.
    power: the power level (H or L) to use. If None existing power level will be used.
    block: if block=True this function won't return until the jolt has finished.
    '''
    if power is not None:
        if power == "H":
            e2b.set_high()
        else:
            e2b.set_low()

    if mode is not None:
        e2b.set_mode(mode)

    e2b.set_output("A", level)
    e2b.set_output("B", level)
    e2b.wait(jolt_time)
    e2b.kill(block=block)


def ramp(e2b, start_level, end_level, dt, mode=None, power=None, block=False):
    '''
    Gradually increase (or decrease) from start_level to end_level with time steps of dt.
    e2b: A running instance of Estim.
    start_level: the initial output level for channels A and B.
    end_level: the final output level for channels A and B.
    dt: the time (in seconds) between each increment.
    mode: the mode to use, if not None. If None existing mode is used.
    power: the power level (H or L) to use. If None existing power level will be used.
    block: if block=True this function won't return until the jolt has finished.
    '''
    if power is not None:
        if power == "H":
            e2b.set_high()
        else:
            e2b.set_low()

    if mode is not None:
        e2b.set_mode(mode)

    direction = 1
    if end_level < start_level:
        direction = -1

    for level in range(start_level, end_level + 1, direction):
        e2b.set_output("A", level)
        e2b.set_output("B", level)
        e2b.wait(dt, block=block)