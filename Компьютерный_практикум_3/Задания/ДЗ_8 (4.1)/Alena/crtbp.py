from numba import njit, cfunc
import numpy as np
from scipy.optimize import bisect

jkw = dict(cache=True)


@cfunc('f8[:](f8, f8[:], f8[:])', **jkw)
def crtbp_ode(t, s, mc):
    """
    система уравнений для ограниченной круговой задачи трёх тел
    с набором констант mc
    возвращает производную состояния s'(t,s)  
    """
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


@njit(**jkw)
def ork_step(f, t, s, h, A, b, c, mc):
    """
    шаг h явного метода Рунге-Кутты по таблице Бутчера A, B, C
    для системы (f, mc) в состоянии (t, s)
    """
    N = b.shape[0]
    k = np.empty((N, s.shape[0]))
    s_n = s.copy()
    k[0] = f(t, s, mc)
    for i in range(1, N):
        t_ni = t + h * c[i]
        s_ni = s.copy()
        for j in range(i):
            s_ni += h * A[i,j] * k[j]
        k[i, :] = f(t_ni, s_ni, mc)
        
    for i in range(N):
        s_n += h * k[i] * b[i]
    return s_n


@njit(**jkw)
def ork_nsteps(f, h, A, b, c, mc, n, t, s):
    """
    алгоритм явного метода Рунге-Кутты на n шагов h 
    явного метода Рунге-Кутты по таблице Бутчера A, B, C
    для системы (f, mc) с нач. состоянием (t, s)
    """
    arr = np.empty((n + 1, s.shape[0] + 1))
    arr[:, 0] = t + h * np.arange(n + 1)
    arr[0, 1:] = s
    for i in range(n):
        arr[i + 1, 1:] = ork_step(
                                  f,           # правая часть СОДУ
                                  arr[i, 0],   # t_0
                                  arr[i, 1:],  # s_0
                                  h,           # шаг dt
                                  A,
                                  b,
                                  c,
                                  mc # параметры модели
                                  )  
    return arr

@njit(**jkw)
def ork_nsteps_planes(f, h, A, b, c, mc, n, pl, t, s):
    """
    алгоритм явного метода Рунге-Кутты на n шагов h 
    явного метода Рунге-Кутты по таблице Бутчера A, B, C
    для системы (f, mc) с нач. состоянием (t, s) с ограниченной pl 
    областью расчёта состояний
    """
    arr = np.empty((n + 1, s.shape[0] + 1))
    arr[:, 0] = t + h * np.arange(n + 1)
    arr[0, 1:] = s
    
    i = 0
    for i in range(n):
        arr[i + 1, 1:] = ork_step(
                                  f,           # правая часть СОДУ
                                  arr[i, 0],   # t_0
                                  arr[i, 1:],  # s_0
                                  h,           # шаг dt
                                  A,
                                  b,
                                  c,
                                  mc # параметры модели
                                  ) 
        x = arr[i + 1, 1]
        if x < pl[0] or x > pl[1]:
            break

    return arr[:i + 2]

@njit
def get_plane(vy, s, args):
    """
    вспомогательная функция - преобразует результат моделирования 
    в одним из двух интересующих - 
    когда объект полетел в сторону более массивного объекта -1
    или в сторону менее массивного 1
    при условии начальной скорости vy 
    и параметров функции ork_nsteps_planes (s, args)
    """
    s[4] = vy
    arr = ork_nsteps_planes(*args, 0., s)
    x = arr[-1,1]
    xmean = np.mean(args[-1])
    return -1 if x < xmean else 1


def get_v0(v_ab, s, args1):
    """
    начальная скорость для наиболее долгого полета по вокруг xL1 
    методом бисекции из состояния s (v_star \in v_ab)
    """
    v_a, v_b = v_ab
    v_star = bisect(get_plane, v_a, v_b, args=(s, args1), xtol=1e-16)
    return v_star

def vectorized_get_v0(x, z, v, args1):
    """
    массив начальных скоростей по узлам
    решётки начальных состояний объекта
    """
    N = x.shape[0]
    main_arr = np.empty((N,N))
    s = np.zeros(6)
    for i in range(N):
        for j in range(N):
            s[[0,2]] = x[i], z[j]
            main_arr[i,j] = get_v0(v, s, args1)
    return main_arr