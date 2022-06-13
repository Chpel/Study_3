from numba import njit, cfunc
import numpy as np

jkw = dict(cache=True)


# декоратор cfunc вместо njit используется для того,
# чтобы не перекомпилировать rk4_step, rk4_nsteps
# для разных моделей
@cfunc('f8[:](f8, f8[:], f8[:])', **jkw)
def lv_ode(t, s, mc):
    x, y = s
    a, b, c, d = mc
    return np.array([( a - b*y)*x,
                     (-c + d*x)*y])


@cfunc('f8[:](f8, f8[:], f8[:])', **jkw)
def mp_ode(t, s, mc):
    theta, omega = s
    g, L = mc
    return np.array([omega,
                     -g/L * np.sin(theta)])


@njit(**jkw)
def rk4_step(f, t, s, h, mc):
    k1 = f(t, s, mc)
    k2 = f(t + h*0.5, s + h*0.5*k1, mc)
    k3 = f(t + h*0.5, s + h*0.5*k2, mc)
    k4 = f(t + h, s + h*k3, mc)
    return s + h/6 * (k1 + 2*k2 + 2*k3 + k4)


@njit(**jkw)
def rk4_nsteps(f, t, s, h, mc, n):
    arr = np.empty((n + 1, s.shape[0] + 1))
    arr[:, 0] = t + h * np.arange(n + 1)
    arr[0, 1:] = s

    for i in range(n):
        arr[i + 1, 1:] = rk4_step(f,           # правая часть СОДУ
                                  arr[i, 0],   # t_0
                                  arr[i, 1:],  # s_0
                                  h,           # шаг dt
                                  mc)          # параметры модели
    return arr
