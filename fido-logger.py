import csv
from multiprocessing import Pool
from functools import partial
from math import tan, pi


def deg_to_perc(deg):
    return tan(deg * pi / 180) * 100


def merge(row):
    # gps logs the slowest so we'll use that as the timestamp
    outrow = [int(row[1]), float(row[7]), float(row[8]), float(row[9])]
    # print outrow
    # take the average of the ATT within one second of the gps log
    # find all the ATT +- gpstime
    pitch = 0.
    roll = 0.
    yaw = 0.
    count = 0
    att = [x for x in data if x[0] == 'ATT' and (outrow[0] - 1000 <= int(x[1]) <= outrow[0] + 1000)]
    print att or None
    if len(att) > 0:
        for row in att:
            count += 1
            pitch += float(row[3])
            roll += float(row[5])
            # yaw += float(row[7])
        if count != 0:
            pitch = pitch / count
            perc_pitch = deg_to_perc(pitch)
            roll = roll / count
            perc_roll = deg_to_perc(roll)
            # yaw = yaw / count
            outrow += [perc_pitch, perc_roll]
        return outrow


if __name__ == "__main__":
    # argparse

    # parse through each line and create a line of data for a time point
    data = []
    with open("data/SnakeHill/2017-05-22 14-28-45.log") as f:
        logreader = csv.reader(f)
        for row in logreader:
            if row[0] in ['GPS', 'ATT']: # 'ATT', 'IMU',
                data += [row]

    csvheader = ['timestamp','Status','GMS','GWk','NSats','HDop','Lat','Lng','Alt','Spd','GCrs','VZ','U','DesRoll','Roll','DesPitch','Pitch','DesYaw','Yaw','ErrRP','ErrYaw']

    # write to file
    with open('data/SnakeHill/out.csv', 'wb') as outcsv:
        writer = csv.writer(outcsv)
        # d = data
        # out = Pool().map(
        #     partial(merge, data),
        #     [x for x in data if x[0] == 'GPS']
        # )
        #
        # writer.writerows(out)

        gps = [x for x in data if x[0] == 'GPS' and int(x[2]) not in [0, 1]]
        offset = int(gps[0][1])
        for g in gps:
            g[1] = int(g[1]) - offset
        for row in gps:
            try:
                writer.writerow(merge(row))
            except:
                pass
