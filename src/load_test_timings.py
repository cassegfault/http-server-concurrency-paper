import csv
import seaborn
import numpy
import math
from scipy import stats
from datetime import datetime
from jupyterthemes import jtplot
import matplotlib.pyplot as plt
import matplotlib.style as style

from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()
pal = seaborn.cubehelix_palette(8, start=2.4, rot=.5, dark=0.25, reverse=True, hue=1.0)
seaborn.set_palette(pal)
seaborn.palplot(pal)
seaborn.set_style("whitegrid")
int_headers = ['timeStamp','elapsed','bytes','sentBytes','Latency','IdleTime','Connect']
def consume_file(csvfile):
    records = []
    r = csv.reader(csvfile)
    headers = None
    for row in r:
        if headers is None:
            headers = row
            continue
        record = {}
        for idx,h in enumerate(headers):
            if len(row) > idx:
                if h in int_headers:
                    record[h] = float(row[idx])
                else:
                    record[h] = row[idx]
                
        records.append(record)
    return records

async_records = []
with open('data/10k_24t10w_worksteal.csv') as csvfile:
    async_records = consume_file(csvfile)

tpc_records = []
with open('data/10k_24t1w_worksteal3.csv') as csvfile:
    tpc_records = consume_file(csvfile)

st_records = []
with open('data/10k_1t10w_worksteal.csv') as csvfile:
    st_records = consume_file(csvfile)

tpc_latencies = [int(i['Latency']) if 'Latency' in i else 0 for i in tpc_records]
tpc_connects = [int(i['Connect']) if 'Connect' in i else 10000 for i in tpc_records]
tpc_elapsed = [int(i['elapsed']) if 'elapsed' in i else 0 for i in tpc_records]

async_latencies = [int(i['Latency']) if 'Latency' in i else 0 for i in async_records]
async_connects = [int(i['Connect']) if 'Connect' in i else 10000 for i in async_records]
async_elapsed = [int(i['elapsed']) if 'elapsed' in i else 0 for i in async_records]

st_latencies = [int(i['Latency']) if 'Latency' in i else 0 for i in st_records]
st_connects = [int(i['Connect']) if 'Connect' in i else 10000 for i in st_records]
st_elapsed = [int(i['elapsed']) if 'elapsed' in i else 0 for i in st_records]

plot_data = [ [datetime.utcfromtimestamp(math.floor(d['timeStamp'] / 100.0) / 10.0) for d in tpc_records], [d['elapsed'] for d in tpc_records] ]
aplot_data = [ [datetime.utcfromtimestamp(math.floor(d['timeStamp'] / 100.0) / 10.0) for d in async_records], [d['elapsed'] for d in async_records] ]
splot_data = [ [datetime.utcfromtimestamp(math.floor(d['timeStamp'] / 100.0) / 10.0) for d in st_records], [d['elapsed'] for d in st_records] ]

def get_duration(data):
    ds = [int(d['timeStamp']) for d in data]
    return float(max(ds) - min(ds)) / 1000.0

fig, axs = plt.subplots(ncols=3, figsize=(21,5))

ax3 = seaborn.lineplot(x=splot_data[0], y=splot_data[1], ci=None, ax=axs[0])
ax3.set(ylim=(0,17500), xticks=[], ylabel='ms')
ax3.set_xlabel('Single Thread, Multi Worker\nSD: %d | median: %dms\nTest Duration: %.2fs' % (numpy.std(splot_data[1]), numpy.average(splot_data[1]), get_duration(st_records)))


ax = seaborn.lineplot(x=plot_data[0], y=plot_data[1], ci=None, ax=axs[1])
ax.set(ylim=(0,17500), xticks=[], ylabel='ms')
ax.set_xlabel('Multi Thread, Single Worker\nSD: %d | median: %dms\nTest Duration: %.2fs' % (numpy.std(plot_data[1]), numpy.average(plot_data[1]), get_duration(tpc_records)))

ax2 = seaborn.lineplot(x=aplot_data[0], y=aplot_data[1], ci=None, ax=axs[2])
ax2.set(ylim=(0,17500), xticks=[], ylabel='ms')
ax2.set_xlabel('Multi Thread, Multi Worker\nSD: %d | median: %dms\nTest Duration: %.2fs' % (numpy.std(aplot_data[1]), numpy.average(aplot_data[1]), get_duration(async_records)))
fig.savefig("images/request_timings.png")

connect_data = [ [datetime.utcfromtimestamp(math.floor(d['timeStamp'] / 100.0) / 10.0) for d in tpc_records], [d['Connect'] for d in tpc_records] ]
aconnect_data = [ [datetime.utcfromtimestamp(math.floor(d['timeStamp'] / 100.0) / 10.0) for d in async_records], [d['Connect'] for d in async_records] ]

fig, axs = plt.subplots(ncols=2, figsize=(14,5))
ax = seaborn.lineplot(x=connect_data[0], y=connect_data[1], ci=None, ax=axs[0])
ax.set(ylim=(0,100), xticks=[], ylabel='ms')
ax.set_xlabel('Multi Thread, Single Worker\nSD: %.2f | median: %.2fms | mode: %.2fms' % (numpy.std(connect_data[1]), numpy.average(connect_data[1]), stats.mode(connect_data[1])[0]))

ax2 = seaborn.lineplot(x=aconnect_data[0], y=aconnect_data[1], ci=None, ax=axs[1])
ax2.set(ylim=(0,100), xticks=[], ylabel='ms')
ax2.set_xlabel('Multi Thread, Multi Worker\nSD: %.2f | median: %.2fms | mode: %.2fms' % (numpy.std(aconnect_data[1]), numpy.average(aconnect_data[1]), stats.mode(aconnect_data[1])[0]))
fig.savefig("images/connect_timings.png")


