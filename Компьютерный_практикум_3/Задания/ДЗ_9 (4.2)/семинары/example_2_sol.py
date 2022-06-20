import numpy as np
import matplotlib.pyplot as plt
import spiceypy as spice
from utils import load_kernels_from_path

#%%
load_kernels_from_path(path='kernels')

#%% Задание
# Построить траекторию космического аппарата Спектр-РГ относительно точки L2
# в системе отсчета, описанной в файле SEL2.tf

# Чтобы узнать:
# идентификатор космического аппарата и точки L2,
# допустимый диапазон дат,
# нужно запустить утилиту:
# exe\brief.exe -c kernels\spk\название_ядра.bsp
# для Спектр-РГ: srektr-rg.bsp
# для L2: L2_de431.bsp

# Также можно использовать функции для вычисления временного покрытия:
# window1 = spice.spkcov('путь_к_ядру/название_ядра1.bsp', идентификатор_объекта1)
# window2 = spice.spkcov('путь_к_ядру/название_ядра2.bsp', идентификатор_объекта2)
# res_win = utils.intersect_windows(window1, window2)
# print(utils.window2calendar(res_win))

#%%
from utils import intersect_windows, window2calendar

window1 = spice.spkcov('kernels\\spk\\spektr_rg.bsp', -551)
window2 = spice.spkcov('kernels\\spk\\L2_de431.bsp', 392)
res_arr = intersect_windows(window1, window2, ret_arr=True)
delta = 120
res_arr[0, 0] += delta
res_arr[0, 1] -= delta
res_cal = window2calendar(res_arr)
print(res_cal)

#%%
# date_beg = '2022 JAN 01'
# date_end = '2026 FEB 08'
date_beg, date_end = res_cal[0]

et_beg = spice.str2et(date_beg)
et_end = spice.str2et(date_end)
et_stp = 86400.0

et = np.arange(et_beg, et_end, et_stp)

print(f"{et_beg=}", f"{et_end=}", sep='\n')

#%% Рассчитать положение целевого объекта относительно наблюдателя
trg = '-551'
obs = '392'
frm = 'SUN_EARTH_L2'

pos, lt = spice.spkpos(trg, et, frm, 'NONE', obs)

#%% Построить график на плоскости XOY

plt.plot(pos[:, 0], pos[:, 1])
plt.xlabel('$x$, km')
plt.ylabel('$y$, km')
plt.title(f'{trg.capitalize()} trajectory from {date_beg} to {date_end}\n'
          f'relative to {obs.capitalize()}')
plt.plot(0, 0, 'ok')
plt.text(0, 0, '  L2')
plt.grid()
plt.axis('equal')
plt.show()

