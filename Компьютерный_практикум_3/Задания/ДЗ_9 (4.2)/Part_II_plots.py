import numpy as np
from datetime import timedelta, datetime, time
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import YearLocator, MonthLocator, DateFormatter

# Task 3 - повторить графики

#%%
date_beg = '2022 JUN 01'
date_end = '2026 JUN 01'

df_wins = {'Луна-Глоб (сол.)': pd.read_pickle('lg_site1_sun_bear.pkl'),
           'Спектр-РГ': pd.read_pickle('spektr_rg_bear.pkl'),
           'Экзомарс': pd.read_pickle('exomars_bear.pkl'),
           'Марс': pd.read_pickle('mars_bear.pkl'),
           }

df_wins_u = {'Луна-Глоб (сол.)': pd.read_pickle('lg_site1_sun_u.pkl'),
           'Спектр-РГ': pd.read_pickle('spektr_rg_u.pkl'),
           'Экзомарс': pd.read_pickle('exomars_u.pkl'),
           'Марс': pd.read_pickle('mars_u.pkl'),
           }

#%%

def hour2float(col) -> float:
    """перевод часов даты в действительное число (кол-во прошедших часов и его долей от полуночи)"""
    return col.hour + col.minute / 60 + col.second / 3600

def trunctime(d: datetime):
    """обнуления времени в дате (полночь того же дня)"""
    return d.replace(hour=0, minute=0, second=0, microsecond=0)

def split_interval_to_days(start: datetime, end: datetime) -> pd.DataFrame:
    """
    :param start: начало промежутка
    :param end: конец промежутка
    :return: разбиение на таблицу для каждого дня: начало, конец, длительность (может быть полной, все 24 часа)
    """
    s = hour2float(start)
    d = (end - start).seconds / 3600
    if (end - start).days > 1:
        res = pd.DataFrame({
            'start': [start] + [(trunctime(start) + timedelta(days=i)) for i in range(1,(end-start).days + 2)],
            'end': [trunctime(start + timedelta(days=i)) - timedelta(seconds=1) for i in range(1,(end-start).days+2)] + [end]})
        res['duration'] = res.end - res.start
    elif s + d > 24:
        res = pd.DataFrame({
            'start': [start, start.date() + timedelta(days=1)],
            'end': [start.date() + timedelta(days=1) - timedelta(microseconds=1), end]})
        res['duration'] = res.end - res.start
    else:
        res = pd.DataFrame({
            'start': [start],
            'end': [end],
            'duration': [end - start]})
    return res

#%%

plt.figure(figsize=(15, 5))

names = ('Спектр-РГ', 'Экзомарс', 'Марс', 'Луна-Глоб (сол.)')

lines = {}
for i, name in enumerate(names):
    df = df_wins[name]
    dfs = [split_interval_to_days(row.start, row.end) for _, row in df.iterrows()]
    df_full = pd.concat(dfs)

    bottom = hour2float(df_full.start.dt)
    height = df_full.duration.dt.total_seconds() / 3600
    line = plt.bar(df_full.start.dt.date, height=height, bottom=bottom, width=1.0, alpha=0.7)
    lines[i] = line

# см. пример 3
xax = plt.gca().xaxis
xax.set_major_locator(YearLocator())
xax.set_minor_locator(MonthLocator())
xax.set_major_formatter(DateFormatter('%m\n%Y'))
xax.set_minor_formatter(DateFormatter('%m'))
plt.xlabel('Дата')
plt.ylabel('длительность, ч')
plt.title(f'Карта видимости объектов с наземного пункта Медвежьи озера от {date_beg} до {date_end}')
plt.grid(axis='y', which='major', ls='--', alpha=0.5)
plt.grid(axis='x', which='minor', ls='--', alpha=0.5)
plt.grid(axis='x', which='major', ls='--')
plt.tight_layout()
plt.xlim(pd.to_datetime(date_beg), pd.to_datetime(date_end))
plt.ylim(0, 24)
plt.yticks(np.arange(25))
plt.legend(lines.values(), names)
plt.savefig('Bear_plot.png')

#%%

plt.figure(figsize=(15, 5))

names = ('Спектр-РГ', 'Экзомарс', 'Марс', 'Луна-Глоб (сол.)')

lines = {}
for i, name in enumerate(names):
    df = df_wins_u[name]
    dfs = [split_interval_to_days(row.start, row.end) for _, row in df.iterrows()]
    df_full = pd.concat(dfs)

    bottom = hour2float(df_full.start.dt)
    height = df_full.duration.dt.total_seconds() / 3600
    line = plt.bar(df_full.start.dt.date, height=height, bottom=bottom, width=1.0, alpha=0.7)
    lines[i] = line

# см. пример 3
xax = plt.gca().xaxis
xax.set_major_locator(YearLocator())
xax.set_minor_locator(MonthLocator())
xax.set_major_formatter(DateFormatter('%m\n%Y'))
xax.set_minor_formatter(DateFormatter('%m'))
plt.xlabel('Дата')
plt.ylabel('длительность, ч')
plt.title(f'Карта видимости объектов с наземного пункта Уссурийск от {date_beg} до {date_end} ')
plt.grid(axis='y', which='major', ls='--', alpha=0.5)
plt.grid(axis='x', which='minor', ls='--', alpha=0.5)
plt.grid(axis='x', which='major', ls='--')
plt.tight_layout()
plt.xlim(pd.to_datetime(date_beg), pd.to_datetime(date_end))
plt.ylim(0, 24)
plt.yticks(np.arange(25))
plt.legend(lines.values(), names)
plt.savefig('Ussuriysk_plot.png')
