import numpy as np
import time
#from threading import Thread
from queue import Queue
from estim2b import Estim
import _thread


class Jolt:

    def __init__(self, e2b, verbose=False):
        # connection to the E-stim 2B unit
        self._e2b = e2b
        # print when jolting
        self._verbose = verbose
        # record of each jolt
        self._jolt_history = []

    def test_grace_period(self, gtime):
        # returns true if we're still in the grace period
        if len(self._jolt_history) == 0: 
            return False
        return self.time_since_last_jolt() < gtime

    def __call__(self, mode='throb', jtime=3.5, jpower=3, gtime=1):
        # first we see if we're within the grace time
        ltime = self.time_since_last_jolt()
        if self.test_grace_period(gtime):# + np.max([0, ltime-jtime])):
            if self._verbose: print('No jolt: within grace period')
            return False

        if mode is not None:
            self._e2b.setMode(mode)

        if self._verbose: print('Jolting.. ({} in last 60s)'.format(self.count_jolts(60)))
        #self._e2b.setOutputs(jpower, jpower, kill_after=jtime)
        _thread.start_new_thread(self._e2b.setOutputs, (jpower, jpower, jtime))
        self._jolt_history += [time.time()]
        return True

    def time_since_last_jolt(self):
        if len(self._jolt_history) == 0: return np.inf
        return time.time() - self._jolt_history[-1]

    def count_jolts(self, t):
        needle = time.time() - t
        tarray = np.array(self._jolt_history)
        return len(tarray[tarray >= needle])






