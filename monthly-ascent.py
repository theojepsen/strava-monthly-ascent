#!/usr/bin/env python
import os, sys
import csv
import gzip
import tcxparser
import gpxpy
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
from multiprocessing import Pool, cpu_count


act_types = None
archive_diretory = None

if len(sys.argv) < 2:
    sys.stderr.write("Usage: %s PATH_TO_EXTRACTED_STRAVA_ARCHIVE [ACTIVITY_TYPES]\n" % sys.argv[0])
    sys.exit(1)

archive_diretory = sys.argv[1]
os.chdir(os.path.abspath(archive_diretory))

if len(sys.argv) > 2:
    act_types = sys.argv[2].split(',')
    print "Analyzing only the following activity types:", ', '.join(act_types)


def calcGPXAscent(gpx):
    ascent = 0
    last_elevation = None
    for track in gpx.tracks:
        for seg in track.segments:
            for point in seg.points:
                if last_elevation is not None:
                    ascent += max(0, point.elevation - last_elevation)
                last_elevation = point.elevation
    return ascent

# Some files exported from Strava begin with whitespaces, instead of a "<". The
# XML parser doesn't like this, so we seek the file cursor to the "<".
def skipWhitespace(f):
    s = f.read(1024)
    assert '<' in s
    f.seek(s.index('<'))
    return f

def parseActivity(act):
    fn_key = 'filename'
    date_key = 'date'
    type_key = 'type'
    distance_key = 'distance'
    ascent_key = 'elevation'

    if 'Filename' in act:
        fn_key = 'Filename'
        date_key = 'Activity Date'
        type_key = 'Activity Type'
        distance_key = 'Distance'
        ascent_key = 'Elevation Gain'

    if not act[fn_key]:
        return None

    if act[fn_key].endswith('gpx.gz'):
        with skipWhitespace(gzip.open(act[fn_key], 'r')) as f:
            gpx = gpxpy.parse(f)
        ascent = calcGPXAscent(gpx)
    elif act[fn_key].endswith('tcx.gz'):
        with skipWhitespace(gzip.open(act[fn_key], 'r')) as f:
            tcx = tcxparser.TCXParser(f)
        ascent = tcx.ascent
    elif act[fn_key].endswith('fit.gz'):
        # TODO: parse fit.gz
        if ascent_key in act:
            ascent = float(act[ascent_key])
        else:
            return None
    else:
        raise Exception("Unknown activity file type")

    distance = 0
    distance_str = act[distance_key].replace(',', '')
    if distance_str: distance = float(distance_str)

    return dict(date=act[date_key], ascent=ascent,
            distance=distance,
            type=act[type_key])

def parseActivities():
    with open('activities.csv', 'r') as f:
        activities = list(csv.DictReader(f))

    print "Parsing activity files in paralell with", cpu_count(), "threads."
    activities2 = Pool(processes=cpu_count()).map(parseActivity, activities)

    cols = ['date', 'ascent', 'distance', 'type']
    data = dict((col,[]) for col in cols)
    for x in filter(None, activities2):
        for col in cols: data[col].append(x[col])

    df = pd.DataFrame(data, columns=cols)
    df['date'] = pd.to_datetime(df['date'])
    return df

if os.path.isfile('activities_ascent.pkl'):
    df = pd.read_pickle('activities_ascent.pkl')
else:
    df = parseActivities()
    df.to_pickle('activities_ascent.pkl')

df = df.set_index('date')

print df

if act_types:
    masks = [df['type'] == t for t in act_types]
    df = df[np.logical_or.reduce(masks)]

total_ascent = df['ascent'].sum()
total_distance = df['distance'].sum()

print df.set_index('type', append=True)['ascent'].unstack().sum().sort_values()

print 'total_distance:', total_distance, "km"

ascent_by_month = df.set_index('type', append=True)['ascent'].unstack().resample('M').sum()

# Sort columns
if act_types:
    ascent_by_month.columns = pd.CategoricalIndex(ascent_by_month.columns.values,
                                     ordered=True, categories=act_types)
    ascent_by_month = ascent_by_month.sort_index(axis=1)

ax = ascent_by_month.plot.bar(stacked=True,figsize=(10,8))
#ax = ascent_by_month.plot.area(stacked=True,figsize=(10,8))

plt.title('Monthly Ascent (total: %s m)' % format(int(total_ascent), ','))
plt.ylabel('Ascent (m)')
plt.xlabel('Month')

plt.gcf().autofmt_xdate()
ticklabels = [x.strftime('%b %y') for x in ascent_by_month.index]
ax.xaxis.set_major_formatter(ticker.FixedFormatter(ticklabels))
ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: format(int(x), ',')))

plt.axhline(y=8848, linewidth=1, color='k', linestyle='--', alpha=0.4)
plt.text(-0.4,8400,'Everest (8,848 m)', alpha=0.4)

plt.show()
