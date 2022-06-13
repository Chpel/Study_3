from numba import njit, cfunc
import numpy as np
from scipy.optimize import bisect

jkw = dict(cache=True)


@cfunc('f8[:](f8, f8[:], f8[:])', **jkw)
def crtbp_ode(t, s, mc):
    """
    расчёт системы уравнений для ограниченной круговой задачи трёх тел
    в момент времени t, в состоянии s с константами mc
    
    возвращает производную состояния
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

# пункт 1 
# Реализовать обобщенный метод Рунге-Кутты на основе таблицы Бутчера для интегрирования систем ОДУ первого порядка

@njit(**jkw)
def rk_step_b(f, t, s, h, A, b, c, mc):
    """
    шаг обобщенного алгоритма Рунге-Кутта размера h
    в момент времени t с состоянием s
    с временным шагом h и таблицей бутчера из A, b, c
    и константами mc
    """
    N = b.shape[0]
    k = np.empty((N, s.shape[0]))
    ds = np.zeros(s.shape[0])
    for i in range(N):
        t_step = t + h * c[i]
        s_step = np.zeros(s.shape[0])
        for j in range(i):
            s_step += A[i,j] * k[j]
        k[i, :] = f(t_step, s + h * s_step, mc)
        ds += b[i] * k[i]
    return s + h * ds


@njit(**jkw)
def rk_nsteps_b(f, t, s, h, butcherTab, mc, n):
    """
    функция решения ограниченной круговой задачи трёх тел на n шагов
    (в виде набора состояний arr в каждый из n дискретных моментов времени)
    с функцией правой части f от начального момента времени t и состояния s,
    с временным шагом h и таблицей бутчера из butcherTab
    и константами mc
    """
    A, b, c = butcherTab
    arr = np.empty((n + 1, s.shape[0] + 1))
    arr[:, 0] = t + h * np.arange(n + 1)
    arr[0, 1:] = s
    for i in range(n):
        arr[i + 1, 1:] = rk_step_b(
                                  f,           # правая часть СОДУ
                                  arr[i, 0],   # t_0
                                  arr[i, 1:],  # s_0
                                  h,           # шаг dt
                                  A,b,c, #таблица Бутчера
                                  mc # параметры модели
                                  )  
    return arr

# пункт 2
# модификация функции (1) для досрочной остановки интегрирования при условии пересечения одной из плоскостей
@njit(**jkw)
def rk_nsteps_planes_b(f, t, s, h, butcherTab, mc, n, pl):
    """
    модификация rk_nsteps_b на ограничение области расчёта (при выходе из неё программа выводит список
    состояний ровно до выхода из неё)
    """
    A, b, c = butcherTab
    arr = np.empty((n + 1, s.shape[0] + 1))
    arr[:, 0] = t + h * np.arange(n + 1)
    arr[0, 1:] = s
    
    i = 0
    for i in range(n):
        arr[i + 1, 1:] = rk_step_b(
                                  f,           # правая часть СОДУ
                                  arr[i, 0],   # t_0
                                  arr[i, 1:],  # s_0
                                  h,           # шаг dt
                                  A,b,c,
                                  mc # параметры модели
                                  ) 
        x = arr[i + 1, 1]
        if x < pl[0] or x > pl[1]:
            break

    return arr[:i + 2]


# функция для расчета начальной скорости  𝑣𝑦0  на основе метода бисекции для орбиты,
# заданной начальным положением  (𝑥0,0,𝑧0)  и условием ортогональности вектора скорости
# и плоскости  𝑋𝑂𝑍  в начальный момент времени

@njit
def get_plane(vy, f, s, h, butcherTab, mc, n, pl):
    """
    вспомогательная функция - определяет конечное положение из двух интересующих - в сторону более массивного объекта -1
    или в сторону менее массивного 1
    при условии начальной скорости vy и параметров функции rk_nsteps_planes_b
    """
    s0 = s.copy()
    s0[4] = vy
    arr = rk_nsteps_planes_b(f, 0.,s0,h,butcherTab,mc,n, pl)
    x = arr[-1,1]
    xmean = np.mean(pl)
    return -1 if x < xmean else 1


def get_v0(v_ab, f, s_0, h, butcherTab, mc, pl):
    """
    функция нахождения оптимальной начальной скорости методом бисекции
    как точку разрыва функции get_plane с областью поиска v_ab
    """
    s = np.zeros(6)
    s[:3] = s_0
    v_a, v_b = v_ab
    v_star = bisect(get_plane, v_a, v_b, args=(f, s, h, butcherTab, mc, 100000, pl), xtol=1e-16)
    return v_star

# пунтк 3
# Реализовать алгоритм вычисления начальных скоростей орбит, 
# начальные состояния которых заданы на решетке

def get_v0_over_grid(xs, zs, vs, f, h, b_t, mc, pl):
    """
    функция расчёта начальной скорости по узлам решётки [xs] x [zs],
    отвечающих за начальное состояние
    """
    N = xs.shape[0]
    main_arr = np.empty((N,N))
    for i in range(N):
        for j in range(N):
            main_arr[i,j] = get_v0(vs, f, (xs[i], 0, zs[j]), h, b_t, mc, pl)
    return main_arr