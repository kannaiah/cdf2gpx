from __future__ import print_function

import gpxpy  # pip install gpxpy
import gpxpy.gpx
import json
from datetime import datetime
import tzlocal  # $ pip install tzlocal
import math
import sys
import os


def utc2datetime(unix_timestamp):
    local_timezone = tzlocal.get_localzone()  # get pytz timezone
    return datetime.fromtimestamp(unix_timestamp, local_timezone)


def ddmm2decimal(val):
    degrees = math.floor(val / 100.0)
    minutes = val - (degrees * 100.0)
    degrees = degrees + (minutes / 60.0)
    return degrees


def read_cdf(filename):
    with open(filename) as fp:
        lines = fp.readlines()

    header = []
    data = []
    list2append = header

    for line in lines:
        if "END-HEADER" in line:
            # change
            list2append = data
        list2append.append(line.strip())

    data = data[1:]

    header = ''.join(header)
    head = json.loads(header)

    return(head, data)


def convet_cdf2gpx(filename):
    print("Converting " + filename + " to gpx format")

    (head, data) = read_cdf(filename)
    outname = filename[:-3] + "gpx"

    gpx = gpxpy.gpx.GPX()

    # Create first track in our GPX:
    gpx_track = gpxpy.gpx.GPXTrack()
    gpx.tracks.append(gpx_track)

    # Create first segment in our GPX track:
    gpx_segment = gpxpy.gpx.GPXTrackSegment()
    gpx_track.segments.append(gpx_segment)

    points = [line.split(',') for line in data if '49' == line.split(',')[0]]

    names = 'sys_tick ,utc,lat,lon,altRef,hAcc,vAcc,sog_kmh,cogt,vVel,hdop,vdop,tdop,numSV'.split(',')

    for point in points:
        dp = dict(zip(names, point[1:]))

        gpxPoint = gpxpy.gpx.GPXTrackPoint(latitude=ddmm2decimal(float(dp['lat'])),
                                           longitude=ddmm2decimal(float(dp['lon'])), time=utc2datetime(float(dp['utc'])),
                                           horizontal_dilution=float(dp.get('hdop')) if dp.get('hdop') else None,
                                           vertical_dilution=float(dp.get('vdop')) if dp.get('vdop') else None,
                                           elevation=float(dp.get('altRef')) if dp.get('altRef') else None,
                                           speed=(5.0 / 18.0) * float(dp.get('sog_kmh')) if dp.get('sog_kmh') else None)

        # Create points:
        gpx_segment.points.append(gpxPoint)

    with open(outname, mode='w') as f:
        print("Writing to file " + outname)
        f.write(gpx.to_xml())


if __name__ == "__main__":
    filename = sys.argv[1]
    convet_cdf2gpx(filename)
