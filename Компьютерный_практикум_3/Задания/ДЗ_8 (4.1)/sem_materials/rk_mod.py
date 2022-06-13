from numba import njit, cfunc
import numpy as np
from rk_examples import rk4_step

jkw = dict(cache=True)


@njit(**jkw)
def rk4_nsteps_planes(f, t, s, h, mc, n, pl):
    arr = np.empty((n + 1, s.shape[0] + 1))
    arr[:, 0] = t + h * np.arange(n + 1)
    arr[0, 1:] = s

    i = 0
    for i in range(n):
        arr[i + 1, 1:] = rk4_step(f,           # правая часть СОДУ
                                  arr[i, 0],   # t_0
                                  arr[i, 1:],  # s_0
                                  h,           # шаг dt
                                  mc)          # параметры модели
        x = arr[i + 1, 1]
        if x < pl[0] or x > pl[1]:
            break

    return arr[:i + 2]
