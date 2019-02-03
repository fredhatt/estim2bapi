import numpy as np
import pandas as pd
from collections import deque

class EMA:
    def __init__(self, alpha):
        self.alpha = alpha
        self.ema = None
        self.emv = 0.0

    def __call__(self, value):
        delta = value
        if self.ema is not None: delta -= self.ema

        self.emv = (1.-self.alpha) * (self.emv + self.alpha*delta**2)

        if self.ema is None:
            self.ema = float(value)
        else:
            #self.ema = self.alpha * self.ema + (1.-self.alpha) * value
            self.ema = self.ema + self.alpha * delta

        print(self.ema, self.emv)
        return self.ema, self.emv

    def get_ema(self):
        if self.ema is None: return 0
        return self.ema


class History:
    def __init__(self, max_length=1000):
        self.counter = 0
        self.max_length = max_length
        self.hist = deque()
        self.vhist = deque()
        self.shist = deque()
        self.ahist = deque()

        self.speed_ema = EMA(alpha=0.9)

    def record(self, t, x, y, z):
        self.counter += 1
        self.hist.append( np.array([t, x, y, z]) )

        v = self.calc_velocity()
        self.vhist.append( np.array([t, v[0], v[1], v[2]]) )
        
        s = self.calc_speed()
        #s, sv = self.speed_ema(s)
        #self.speed_means = s
        #self.speed_stds = np.sqrt(sv)
        self.shist.append( np.array([t, s]) )

        pitch, roll = self.calc_angles(-1)
        self.ahist.append( np.array([t, pitch[0], roll[0]]) )

        if len(self.hist) >  self.max_length:
            self.hist.popleft()
        if len(self.vhist) >  self.max_length:
            self.vhist.popleft()
        if len(self.shist) >  self.max_length:
            self.shist.popleft()
        if len(self.ahist) >  self.max_length:
            self.ahist.popleft()

    def __len__(self):
        return len(self.hist)

    def get(self, pos):
        return self.hist[pos]

    def get_stats(self, low=0, high=None):
        means = np.mean(self.hist, axis=0)    
        stds = np.std(self.hist, axis=0)
        return means[low:high], stds[low:high]

    def calc_velocities(self):
        d = np.diff(self.hist, axis=0)
        dt = d[:, 0]
        dt = np.reshape(dt, (-1, 1))
        dxyz = d[:, 1:4]
        return dxyz/dt

    def calc_speeds(self):
        vels = self.calc_velocities()
        return np.sqrt(np.sum(vels**2, axis=-1))

    def calc_angles(self, pos=None):
        if pos is None:
            xyz = np.array(self.hist)[:, 1:4]
        else:
            xyz = np.array(self.hist)[pos, 1:4]
            xyz = np.reshape(xyz, (-1, 3)) # single entry
        pitch = np.arctan(xyz[:, 0] / np.sqrt(xyz[:, 1]**2 + xyz[:, 2]**2)) * 180. / np.pi
        roll = np.arctan(xyz[:, 1] / np.sqrt(xyz[:, 0]**2 + xyz[:, 2]**2)) * 180. / np.pi
        return pitch, roll

    def calc_velocity(self):
        try:
            txyz_this = self.get(-1)
            txyz_last = self.get(-2)
        except IndexError:
            return np.zeros(3, dtype=float)
        d = txyz_this - txyz_last
        dt = d[0]
        dxyz = d[1:4]
        return dxyz/dt

    def calc_speed(self):
        vels = self.calc_velocity()
        return np.sqrt(np.sum(vels**2, axis=-1))

    def calibrate_velocities(self, motionstd=None):
        vels = self.calc_velocities()
        self.vel_means, self.vel_stds = np.mean(vels, axis=0), np.std(vels, axis=0)
        if motionstd is not None:
            self.vel_stds = motionstd

        return self.vel_means, self.vel_stds

    def calibrate_speeds(self, motionstd=None):
        speeds = self.calc_speeds()
        ##df = pd.DataFrame(speeds, columns=['vel'])
        ##ema = pd.ewma(df, alpha=0.5)
        ##self.speed_means = ema.mean().values[-1]
        ##self.speed_stds = ema.std().values[-1]
        self.speed_means, self.speed_stds = np.mean(speeds, axis=0), np.std(speeds, axis=0)
        if self.speed_stds < 1.5: self.speed_stds = 10.0
        
        if motionstd is not None:
            self.speed_stds = motionstd

        return self.speed_means, self.speed_stds

    def calibrate_angles(self, angstd=None):
        angles = self.calc_angles()
        self.angle_means, self.angle_stds = np.mean(angles, axis=1), np.std(angles, axis=1)
        if self.angle_stds[0] < 2.0: self.angle_stds[0] = 0.75
        if self.angle_stds[1] < 2.0: self.angle_stds[1] = 0.75
        if angstd is not None:
            self.angle_stds = np.array([angstd, angstd])

        return self.angle_means, self.angle_stds

    def test_velocity_trigger(self, motion_tol):
        vel = self.calc_velocity()
        trigger, = np.where( np.abs(vel) - motion_tol*self.vel_stds > 0 )
        if len(trigger) > 0:
            return True
        return False

    def test_speed_trigger(self, motion_tol):
        speed = self.calc_speed()
        trigger, = np.where( np.abs(speed) - motion_tol*self.speed_stds > 0 )
        if len(trigger) > 0:
            return True
        return False

    def test_angle_trigger(self, angle_tol):
        dangles = np.array(self.calc_angles(-1)).flatten() - self.angle_means
        trigger, = np.where( np.abs(dangles) > angle_tol*self.angle_stds )
        if len(trigger) > 0:
            return True
        return False


