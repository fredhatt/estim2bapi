import numpy as np
from collections import deque

class History:
    def __init__(self, max_length=100):
        self.counter = 0
        self.max_length = max_length
        self.hist = deque()

    def record(self, t, x, y, z):
        self.counter += 1
        self.hist.append( np.array([t, x, y, z]) )
        if len(self.hist) >  self.max_length:
            self.hist.popleft()

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
        txyz_this = self.get(-1)
        txyz_last = self.get(-2)
        d = txyz_this - txyz_last
        dt = d[0]
        dxyz = d[1:4]
        return dxyz/dt

    def calibrate_velocities(self, motionstd=None):
        vels = self.calc_velocities()
        self.vel_means, self.vel_stds = np.mean(vels, axis=0), np.std(vels, axis=0)
        if motionstd is not None:
            self.vel_stds = motionstd

        return self.vel_means, self.vel_stds

    def calibrate_angles(self, angstd=None):
        angles = self.calc_angles()
        self.angle_means, self.angle_stds = np.mean(angles, axis=1), np.std(angles, axis=1)
        if angstd is not None:
            self.angle_stds = np.array([angstd, angstd])

        return self.angle_means, self.angle_stds

    def test_velocity_trigger(self, motion_tol):
        vel = self.calc_velocity()
        trigger, = np.where( np.abs(vel) - motion_tol*self.vel_stds > 0 )
        if len(trigger) > 0:
            return True
        return False

    def test_angle_trigger(self, angle_tol):
        dangles = np.array(self.calc_angles(-1)).flatten() - self.angle_means
        trigger, = np.where( np.abs(dangles) > angle_tol*self.angle_stds )
        if len(trigger) > 0:
            return True
        return False


