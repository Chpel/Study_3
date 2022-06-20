import numpy as np
import matplotlib.pyplot as plt
import spiceypy as spice
from utils import load_kernels_from_path

#%% Загрузить ядра spice
load_kernels_from_path(path='kernels')

#%% Задать временной интервал
date_beg = '2022-01-01'
date_end = '2028-01-01'

# convert calendar dates to ephemeris time
et_beg = spice.str2et(date_beg)
et_end = spice.str2et(date_end)
et_stp = 86400.0

et = np.arange(et_beg, et_end, et_stp)

print(f"{et_beg=}", f"{et_end=}", sep='\n')

#%% Рассчитать положение целевого объекта относительно наблюдателя
trg = 'MARS'
obs = 'EARTH'
frm = 'J2000'

pos, lt = spice.spkpos(trg, et, frm, 'NONE', obs)

#%% Построить график на плоскости XOY

plt.plot(pos[:, 0], pos[:, 1])
plt.xlabel('$x$, km')
plt.ylabel('$y$, km')
plt.title(f'{trg.capitalize()} trajectory from {date_beg} to {date_end}\n'
          f'relative to {obs.capitalize()}')
plt.plot(0, 0, 'ok')
plt.text(0, 0, '  Earth')
plt.grid()
plt.axis('equal')
plt.show()

#%% Задание

# Построить проекцию траектории на плоскость XOZ.
# Что показывает эта проекция?

#%% первый подход
# проекция на XOZ выглядит почти такой же, как и на XOY (масштабы осей близки)
# это происходит вследствие того, что система отсчета J2000
# ориентирована по экватору Земли

plt.plot(pos[:, 0], pos[:, 2])
plt.xlabel('$x$, km')
plt.ylabel('$z$, km')
plt.title(f'{trg.capitalize()} trajectory from {date_beg} to {date_end}\n'
          f'relative to {obs.capitalize()}')
plt.plot(0, 0, 'ok')
plt.text(0, 0, '  Earth')
plt.grid()
plt.axis('equal')
plt.show()

#%% если использовать J2000, ориентированную по эклиптике, то
# результат будет отражать отличия плоскостей движения
# Земли и Марса относительно эклиптики;
# разница мастабов осей - 2 порядка

pos, lt = spice.spkpos(trg, et, 'ECLIPJ2000', 'NONE', obs)

plt.plot(pos[:, 0], pos[:, 2])
plt.xlabel('$x$, km')
plt.ylabel('$z$, km')
plt.title(f'{trg.capitalize()} trajectory from {date_beg} to {date_end}\n'
          f'relative to {obs.capitalize()}')
plt.plot(0, 0, 'ok')
plt.text(0, 0, '  Earth')
plt.grid()
#plt.axis('equal')
plt.show()