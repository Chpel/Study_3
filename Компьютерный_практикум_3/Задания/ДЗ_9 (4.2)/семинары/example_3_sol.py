import numpy as np
import matplotlib.pyplot as plt
import spiceypy as spice
from utils import (load_kernels_from_path, merge_intervals,
                   window2df, split_by_max_duration)

#%%
load_kernels_from_path(path='kernels')

#%% Задание
# Рассчитать интервалы видимости Спектр-РГ с наземного пункта Медвежьи озера.
# Идентификатор наземного пункта - BEAR, система отсчета - BEAR_TOPO.
# Минимальный угол места - 10 градусов.
# Построить график длительность интервала видимости от момента начала интервала.

#%%
date_beg = '2022 JAN 01'
date_end = '2026 FEB 01'

et_beg = spice.str2et(date_beg)
et_end = spice.str2et(date_end)
et_stp = 86400.0

et = np.arange(et_beg, et_end, et_stp)

print(f"{et_beg=}", f"{et_end=}", sep='\n')


#%% Определяем параметры расчета

trg = '-551'
obs = 'BEAR'
frm = 'BEAR_TOPO'
abc = 'CN+S'

search_wnd = merge_intervals(np.array([[et_beg, et_end]]))
angle = 10  # deg

#%% Используя geometric finder находим интервалы видимости согласно условию
# широта космического аппарата в топоцентрической системе отсчета должна быть
# больше 10 градусов

#window2calendar(spice.spkcov('kernels/spk/20211231_222209.bsp', -551))

cell = spice.utils.support_types.SPICEDOUBLE_CELL(10000)
window = spice.gfposc(trg, frm, abc, obs,
                      'LATITUDINAL', 'LATITUDE', '>', np.deg2rad(angle),
                      0.0, 600, 10000, search_wnd, cell)

df = window2df(window)

#%% Строим простой график длительности интервалов видимости

plt.figure(figsize=(15, 5))
plt.plot(df.start, df.duration.dt.seconds / 3600)
plt.show()

#%%
from matplotlib.dates import YearLocator, MonthLocator, WeekdayLocator, DateFormatter

dfs = split_by_max_duration(df, max_duration_hours=24)

plt.figure(figsize=(15, 5))
for df_ in dfs:
    plt.plot(df_.start, df_.duration.dt.seconds / 3600, '-k')
ax = plt.gca()
ax.xaxis.set_major_locator(YearLocator())
ax.xaxis.set_minor_locator(MonthLocator())
ax.xaxis.set_major_formatter(DateFormatter('%m\n%Y'))
ax.xaxis.set_minor_formatter(DateFormatter('%m'))
#ax.get_xaxis().set_tick_params(which='major', pad=15)
plt.xlabel('Дата')
plt.ylabel('длительность, ч')
plt.title(f'Длительность видимости {trg.capitalize()} от {date_beg} до {date_end} '
          f'с наземного пункта {obs.capitalize()}')
plt.yticks(np.arange(25))
plt.grid(axis='y', which='major', ls='--', alpha=0.5)
plt.grid(axis='x', which='minor', ls='--', alpha=0.5)
plt.grid(axis='x', which='major', ls='--')
plt.tight_layout()
plt.xlim(df.start.iloc[0], df.end.iloc[-1])
plt.show()

