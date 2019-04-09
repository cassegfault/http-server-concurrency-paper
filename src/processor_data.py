import csv
import seaborn
import numpy
import math
import pandas
import re
from scipy import stats
from datetime import date
from datetime import datetime
from jupyterthemes import jtplot
import matplotlib.pyplot as plt
import matplotlib.style as style
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()
pal = seaborn.cubehelix_palette(8, start=2.4, rot=.5, dark=0.25, reverse=True, hue=1.0)
seaborn.set_palette(pal)
seaborn.palplot(pal)
seaborn.set_style("white")
seaborn.set_style("whitegrid")

def str_to_hz(s):
    s = s.lower()
    if len(s) < 1:
        return None
    num = re.sub(r"[^\d.]+", "", s);
    if 'ghz' in s:
        return int(float(num) * 1000000000)
    elif 'mhz' in s:
        return int(float(num) * 1000000)

def quarter_to_datetime(s):
    split = s.split("'")
    if len(split) < 2:
        return None
    quarter = int(re.sub("\D", "",split[0]))
    month = ((quarter - 1) * 3)+1
    year = int(split[1])
    if year > 30:
        year += 1900
    else:
        year += 2000
    # convoluted way of getting unix timestamps -- not necessarily exactly right
    d = date(year=year,day=1,month=month)
    d = datetime.combine(d, datetime.min.time())
    return (year * 4) + quarter #(d - datetime(1970, 1, 1)).total_seconds()

def str_to_float(s):
    n = re.sub(r"[^\d.]+", "", s)
    if len(n) < 1:
        return None
    else:
        return float(re.sub(r"[^\d.]+", "", s))

def str_to_int(s):
    n = re.sub(r"[^\d.]+", "", s)
    if len(n) < 1:
        return None
    else:
        return int(re.sub(r"[^\d.]+", "", s))

cpus = []
with open('data/Intel_CPUs.csv') as csvfile:
    r = csv.reader(csvfile)
    headers = None
    for row in r:
        if headers is None:
            headers = row
            continue
        if row[1] != "Desktop" or row[4] is None:
            continue
        cpu = {}
        for idx,h in enumerate(headers):
            if len(row) > idx:
                if h in ["Processor_Base_Frequency", "Max_Turbo_Frequency"]:
                    cpu[h] = str_to_hz(row[idx])
                elif h == "Launch_Date":
                    cpu[h] = quarter_to_datetime(row[idx])
                elif h == "Max_Memory_Bandwidth":
                    cpu[h] = str_to_float(row[idx])
                elif h in ['nb_of_Cores','nb_of_Threads']:
                    cpu[h] = str_to_int(row[idx])
                else:
                    cpu[h] = row[idx]
        cpus.append(cpu)
    cpus = pandas.DataFrame(data=cpus)

def quarter_format(value, tick_number):
    year = int(value / 4)
    quarter = (value % 4) + 1
    return "Q%d'%d" % (quarter, year)

def hz_format(value, tick_number):
    return "%.1f GHz" % (value / 1000000000.0)

def int_format(value, tick_number):
    return "%d" % (value)

def bandwidth_format(value, tick_number):
    return "%.1f GB/s" % (value)

fig, axs = plt.subplots(nrows=3, figsize=(20,15))

ax = seaborn.regplot(x="Launch_Date", y="Processor_Base_Frequency", data=cpus,  lowess=True, ax=axs[0]);
ax.xaxis.set_major_locator(plt.MaxNLocator(5))
ax.set( ylabel='Base Clock Speed')
ax.xaxis.set_major_formatter(plt.FuncFormatter(quarter_format))
ax.yaxis.set_major_formatter(plt.FuncFormatter(hz_format))

ax2 = seaborn.regplot(x="Launch_Date", y="nb_of_Cores", lowess=True, data=cpus, ax=axs[2]);
ax2.xaxis.set_major_locator(plt.MaxNLocator(5))
ax2.set(ylim=(0,20), ylabel='Core Count')
ax2.yaxis.set_major_formatter(plt.FuncFormatter(int_format))
ax2.xaxis.set_major_formatter(plt.FuncFormatter(quarter_format))

ax3 = seaborn.regplot(x="Launch_Date", y="Max_Memory_Bandwidth", lowess=True, data=cpus, ax=axs[1]);
ax3.xaxis.set_major_locator(plt.MaxNLocator(5))
ax3.set(ylabel='Memory Bandwidth')
ax3.xaxis.set_major_formatter(plt.FuncFormatter(quarter_format))
ax3.yaxis.set_major_formatter(plt.FuncFormatter(bandwidth_format))
fig.savefig("images/processor_advancements.png")
