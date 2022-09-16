#!/bin/python3

import csv
import datetime
from urllib.error import HTTPError
import requests
from pathlib import Path
import json
import argparse


def getDate(
    args_date: str = None
) -> datetime.datetime:
    if args_date is None:
        return datetime.datetime.now() - datetime.timedelta(days=1)
    else:
        return datetime.datetime.strptime(args_date, "%Y-%m-%d")


def getUrl(
    address: str,
    station: str,
    working_date: datetime.datetime
) -> str:
    channels = f'channels=QW.{station}.*.HN*'
    api = "api/v1/channels/availability/summary/intervals?"
    relative = (f'&startTime={working_date.strftime("%Y-%m-%d")}' +
                f'T00:00:00.000Z&endTime={working_date.strftime("%Y-%m-%d")}' +
                'T23:59:59.999Z&timeFormat=iso8601&intervals=43200&' +
                'arrivalMetrics')
    return "http://" + address + '/' + api + channels + relative


def createDirectory(
    baseDir: str,
    workingDate: datetime.datetime
) -> str:

    dir_str = f'{baseDir}/{workingDate.strftime("%Y/%m/%d")}'
    date_dir = Path(dir_str)

    Path.mkdir(date_dir, mode=0o755, exist_ok=True, parents=True)

    return dir_str


def getStationList(
    binder_file: str
) -> list:
    station_list: list = []
    file = open(binder_file, 'r')

    rows = csv.DictReader(file)

    for row in rows:
        station = row[' STATION_CODE']
        if station not in station_list:
            station_list.append(station)

    return station_list


def main():
    argsparse = argparse.ArgumentParser()

    argsparse.add_argument(
        '-t',
        '--date',
        help='The date to run for',
        default=None
    )
    argsparse.add_argument(
        '-d',
        '--base-dir',
        help='The base directory of the latency archive',
        default='/data/archive/latency'
    )
    argsparse.add_argument(
        '-a',
        '--apollo-address',
        help=('The address, including port number, where the apolloserver can',
              'be reached'),
        default='localhost:8787'
    )
    argsparse.add_argument(
        '-b',
        '--binder',
        help='Location of binder file.',
        default='/home/apollo/binder.csv'
    )

    args = argsparse.parse_args()

    working_date = getDate(args.date)

    jday = working_date.strftime('%j')

    address = args.apollo_address

    baseDir = args.base_dir

    binder = args.binder

    stations = getStationList(binder)

    full_dir = createDirectory(baseDir, working_date)

    for station in stations:

        try:
            soh = requests.get(getUrl(address, station, working_date))

            soh.raise_for_status()

            data = soh.json()

        except HTTPError:
            print(f"Could not fetch data for {station} from server")
        except ValueError:
            print(f"Invalid JSON for {station} fetched from server.")

        with open(f'{full_dir}/QW.{station}.{working_date.year}.{jday}.json',
                  'w+') as f:
            json.dump(data, f, indent=2)
        f.close()


if __name__ == '__main__':
    main()
