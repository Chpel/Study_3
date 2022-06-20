import numpy as np
import spiceypy as spice
from utils import window2calendar, merge_intervals, intersect_windows, window2df, load_kernels_from_path

load_kernels_from_path(path='kernels')

# Task 0 - узнать:
# допустимый диапазон дат объектов через комманду
# # exe\brief.exe -c kernels\spk\название_ядра.bsp

target = ['LG_SITE1', 'SUN', '-551', '-172', 'MARS']
fTar = ['LunaGlob_site', 'de432s', 'spektr_rg', 'exomars', 'mar097_2022_2032']

# lunaglob   201:     2020 JAN 01 00:00:00.000            2040 JAN 01 00:00:00.000
#       SUN   10:     1949 DEC 14 00:00:00.000            2050 JAN 02 00:00:00.000
# spectr_rg -551:     2021 DEC 31 22:23:18.367            2026 FEB 08 22:23:18.368
# exomars   -172:     2022 SEP 22 23:46:48.830            2023 JUN 08 07:28:55.642
# mars       499:     2022 JAN 01 00:01:09.183            2032 JAN 01 00:01:09.183

# Task 1 - расчёты участков видимости

#          target      obs         frame            abcorr  min_angle   date_beg       date_end
params = (('LG_SITE1', 'BEAR',     'BEAR_TOPO',     'CN+S', 10,         '2022-JUN-01', '2026-JUN-01'),
          ('SUN',      'LG_SITE1', 'LG_SITE1_TOPO', 'CN+S', 5,          '2022-JUN-01', '2026-JUN-01'),
          ('-551',     'BEAR',     'BEAR_TOPO',     'CN+S', 10,         '2022-JUN-01', '2026-FEB-07'),
          ('-172',     'BEAR',     'BEAR_TOPO',     'CN+S', 10,         '2022-SEP-23', '2023-JUN-07'),
          ('MARS',      'BEAR',     'BEAR_TOPO',     'CN+S', 10,         '2022-JUN-01', '2026-JUN-01'),

          ('LG_SITE1', 'USSURIYSK',     'USSURIYSK_TOPO',     'CN+S', 10,         '2022-JUN-01', '2026-JUN-01'),
          ('-551',     'USSURIYSK',     'USSURIYSK_TOPO',     'CN+S', 10,         '2022-JUN-01', '2026-FEB-07'),
          ('-172',     'USSURIYSK',     'USSURIYSK_TOPO',     'CN+S', 10,         '2022-SEP-23', '2023-JUN-07'),
          ('MARS',     'USSURIYSK',     'USSURIYSK_TOPO',     'CN+S', 10,         '2022-JUN-01', '2026-JUN-01'),
          )

windows = {}
for trg, obs, frm, abc, min_angle, d_b, d_e in params:
    cell = spice.utils.support_types.SPICEDOUBLE_CELL(10000)
    et_beg = spice.str2et(d_b)
    et_end = spice.str2et(d_e)
    et_stp = 86400.0
    et = np.arange(et_beg, et_end, et_stp)
    search_wnd = merge_intervals(np.array([[et_beg, et_end]]))
    window = spice.gfposc(trg, frm, abc, obs,
                          'LATITUDINAL', 'LATITUDE', '>', np.deg2rad(min_angle),
                          0.0, 600, 10000, search_wnd, cell)
    windows[trg+'_'+obs] = window
    print(trg+'_'+obs, ' done!')

windows['LG_SITE1+SUN_BEAR'] = intersect_windows(windows['LG_SITE1_BEAR'], windows['SUN_LG_SITE1'])
windows['LG_SITE1+SUN_USSURIYSK'] = intersect_windows(windows['LG_SITE1_USSURIYSK'], windows['SUN_LG_SITE1'])

df_wins = {key: window2df(win) for key, win in windows.items()}

# Task 2 - сохранить всё в форматах .csv и .pkl

df_wins['LG_SITE1+SUN_BEAR'].to_pickle('lg_site1_sun_bear.pkl')
df_wins['-551_BEAR'].to_pickle('spektr_rg_bear.pkl')
df_wins['-172_BEAR'].to_pickle('exomars_bear.pkl')
df_wins['MARS_BEAR'].to_pickle('mars_bear.pkl')

df_wins['LG_SITE1+SUN_BEAR'].to_csv('lg_site1_sun_bear.csv')
df_wins['-551_BEAR'].to_csv('spektr_rg_bear.csv')
df_wins['-172_BEAR'].to_csv('exomars_bear.csv')
df_wins['MARS_BEAR'].to_csv('mars_bear.csv')

df_wins['LG_SITE1+SUN_USSURIYSK'].to_pickle('lg_site1_sun_u.pkl')
df_wins['-551_USSURIYSK'].to_pickle('spektr_rg_u.pkl')
df_wins['-172_USSURIYSK'].to_pickle('exomars_u.pkl')
df_wins['MARS_USSURIYSK'].to_pickle('mars_u.pkl')

df_wins['LG_SITE1+SUN_USSURIYSK'].to_csv('lg_site1_sun_u.csv')
df_wins['-551_USSURIYSK'].to_csv('spektr_rg_u.csv')
df_wins['-172_USSURIYSK'].to_csv('exomars_u.csv')
df_wins['MARS_USSURIYSK'].to_csv('mars_u.csv')
