import csv
from argparse import ArgumentParser
from multiprocessing import Pool
from functools import partial
from math import tan, pi
import os
from datetime import datetime, timedelta
import time
# import leapseconds


def deg_to_perc(deg):
    return tan(deg * pi / 180) * 100


def gpstodatetime(gwk, gms):
    gps_epoch = datetime(1980, 1, 6, 0, 0, 0)
    leap_ms = (37 - 19) * 1000
    return gps_epoch + timedelta(weeks=gwk, milliseconds=(gms - leap_ms))


def merge(row):
    # gps logs the slowest so we'll use that as the timestamp
    # print row
    # columns: seconds since pixhawk turned on, gps time, lat, lon, alt
    outrow = [(float(row[1]) / 1E+6), gpstodatetime(int(row[4]), int(row[3])), float(row[7]), float(row[8]), float(row[9])]
    print outrow
    # take the average of the ATT within one second of the gps log
    # find all the ATT +- gpstime
    pitch = 0.
    roll = 0.
    count = 0
    att = [x for x in data if x[0] == 'ATT' and (outrow[0] - 1 <= (float(x[1]) / 1E+6) <= outrow[0] + 1)]
    print att or None
    if len(att) > 0:
        for attrow in att:
            count += 1
            pitch += float(attrow[3])
            roll += float(attrow[5])
        if count != 0:
            pitch = pitch / count
            perc_pitch = deg_to_perc(pitch)
            roll = roll / count
            perc_roll = deg_to_perc(roll)
            outrow += [perc_pitch, perc_roll]
        return outrow


if __name__ == "__main__":
    # argparse
    parser = ArgumentParser()

    parser.add_argument('file', metavar='LOG', help='The log file')

    args = parser.parse_args()

    # Check if file exists:
    if not os.path.isfile(args.file):
        print "{0} is not a file".format(args.file)
        exit(1)

    # Get file root
    fileroot = os.path.dirname(args.file)

    # parse through each line and create a line of data for a time point
    data = []
    with open(args.file) as f:
        logreader = csv.reader(f)
        for row in logreader:
            if row[0] in ['GPS', 'ATT']: # 'ATT', 'IMU',
                data += [row]

    print 'number of rows: {0}'.format(len(data))
    csvheader = ['timestamp','Status','GMS','GWk','NSats','HDop','Lat','Lng','Alt','Spd','GCrs','VZ','U','DesRoll','Roll','DesPitch','Pitch','DesYaw','Yaw','ErrRP','ErrYaw']

    # write to file
    with open('{0}/out.csv'.format(os.path.dirname(args.file)), 'wb') as outcsv:
        writer = csv.writer(outcsv)
        # d = data
        # out = Pool().map(
        #     partial(merge, data),
        #     [x for x in data if x[0] == 'GPS']
        # )
        #
        # writer.writerows(out)

        # write header row
        header = ['time', 'datetime', 'lat', 'long', 'alt', 'slope', 'cross_slope']
        writer.writerow(header)

        gps = [x for x in data if x[0] == 'GPS' and int(x[2]) not in [0, 1]]
        # offset = int(gps[0][1])
        # for g in gps:
        #     g[1] = int(g[1]) - offset
        for row in gps:
            try:
                writer.writerow(merge(row))
            except:
                pass
