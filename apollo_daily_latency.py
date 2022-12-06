#!/usr/bin/env python3
'''
This script's purpose is to retrieve latency information for all Nanometrics
devices and store them in the long-term archive
'''


import logging
import csv
import datetime
from typing import List
from urllib.error import HTTPError
import requests
from pathlib import Path
import json
import argparse


def getDate(
    args_date: str = None
) -> datetime.datetime:
    '''
    Return a datetime object for the date to be processed

    If a date isn't provided, yesterday's date is used
    '''
    if args_date is None:
        return datetime.datetime.now() - datetime.timedelta(days=1)
    else:
        return datetime.datetime.strptime(args_date, "%Y-%m-%d")


def getUrl(
    address: str,
    station: str,
    working_date: datetime.datetime,
    network: str = 'QW'
) -> str:
    '''
    Assemble the url used to query the apollo server availability API

    Parameters
    ----------
    address: str
        The IP address or url of the apolloserver, uncluding the port number.
        Ex apollo-a1:8787

    station: str
        The station code for the station to perform a query about

    working_date: datetime
        Datetime object containing the date to retrieve statistics for

    network: str
        The network the desired station belongs to. Default: QW

    Returns
    -------

    str: The full url used to retrieve availability information
    '''
    channels = f'channels={network}.{station}.*.HN*'
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
    '''
    Ensured that the subdirectory for the specified date exists in the long
    term archive

    Parameters
    ----------
    baseDir: str
        The parent directory of the latency archive

    workingDate: datetime
        The date to create a subdirectory for
    '''
    dir_str = f'{baseDir}/{workingDate.strftime("%Y/%m/%d")}'
    date_dir = Path(dir_str)

    # Exists_ok so it just passes if it already exists
    Path.mkdir(date_dir, mode=0o755, exist_ok=True, parents=True)

    return dir_str


def getStationList(
    binder_file: str
) -> List[tuple]:
    '''
    Reads the binder file to get a list of stations to query Apolloserver about

    Parameters
    ----------
    binder_file: str
        The path to the binder file to read

    Returns
    -------
    List: List of tuples containing network code and station code
    '''
    station_list: List[tuple] = []
    file = open(binder_file, 'r')

    rows = csv.DictReader(file)

    for row in rows:
        station = row[' STATION_CODE']
        network = row['#NETWORK_CODE']

        entry = tuple([network, station])
        if entry not in station_list:
            station_list.append(entry)

    return station_list


def main():
    argsparse = argparse.ArgumentParser()
    argsparse.add_argument(
        '-t',
        '--date',
        help="The date to run for. Default is yesterday's",
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
        help='The address where the apolloserver can be reached',
        default='localhost:8787'
    )
    argsparse.add_argument(
        '-b',
        '--binder',
        help='Location of binder file.',
        default='/home/apollo/binder.csv'
    )
    argsparse.add_argument(
        '-v',
        '--verbose',
        action='store_true',
        help='Sets the logging level to verbose'
    )

    args = argsparse.parse_args()

    # Set logging parameters
    logging.basicConfig(
        format='%(asctime)s:%(levelname)s:%(message)s',
        datefmt="%Y-%m-%d %H:%M:%S",
        level=logging.DEBUG if args.verbose else logging.INFO)

    # Get a date to work with
    working_date = getDate(args.date)

    # Find the julian date to use in file naming
    jday = working_date.strftime('%j')

    address = args.apollo_address

    baseDir = args.base_dir

    binder = args.binder

    # Get a list of stations to query for
    stations = getStationList(binder)

    # Ensure the directory exists to write in
    full_dir = createDirectory(baseDir, working_date)

    for entry in stations:
        try:
            # Request availability information for the station from the
            # apolloserver
            network = entry[0]
            station = entry[1]
            soh = requests.get(getUrl(
                address=address,
                network=network,
                station=station,
                working_date=working_date))
            soh.raise_for_status()
            data = soh.json()

            # Write availability information to file
            with open(f'{full_dir}/{network}.{station}.{working_date.year}.{jday}.json',
                      'w+') as f:
                json.dump(data, f, indent=2)
            f.close()

        except HTTPError:
            print(f"Could not fetch data for {station} from server")
        except ValueError:
            print(f"Invalid JSON for {station} fetched from server.")


if __name__ == '__main__':
    main()
