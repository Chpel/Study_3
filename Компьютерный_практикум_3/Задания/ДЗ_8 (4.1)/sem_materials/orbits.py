from numba import njit, cfunc
import numpy as np

jkw = dict(cache=True)


@cfunc('f8[:](f8, f8[:], f8[:])', **jkw)
def crtbp_ode(t, s, mc):
    x, y, z, vx, vy, vz = s
    mu2 = mc[0]
    mu1 = 1. - mu2

    r1 = ((x + mu2)**2 + y**2 + z**2)**0.5
    r2 = ((x - mu1)**2 + y**2 + z**2)**0.5

    ax = 2*vy + x - (mu1 * (x + mu2)/r1**3 + mu2 * (x - mu1)/r2**3)
    c = (mu1 / r1**3 + mu2 / r2**3)
    ay = -2*vx + y - c * y
    az = -c * z

    return np.array([vx, vy, vz, ax, ay, az])
