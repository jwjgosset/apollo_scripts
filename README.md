This repo contains a script to download the used to download the daily availability for each station streaming into an Apollo Server.

The script uses the binder file to get a list of all stations, and then makes a quiery to the ApolloSever's availability SOH API for each station for the date specified.

The API returns a json file with 2 second intervals, showing the number of packets recieved during each interval, the average, min and max latency.

**Usage**

```
usage: apollo_daily_latency.py [-h] [-t DATE] [-d BASE_DIR]
                               [-a APOLLO_ADDRESS] [-b BINDER]

optional arguments:
  -h, --help            show this help message and exit
  -t DATE, --date DATE  The date to run for. If none is specified, yesterday's
                        date is used
  -d BASE_DIR, --base-dir BASE_DIR
                        The base directory of the latency archive
  -a APOLLO_ADDRESS, --apollo-address APOLLO_ADDRESS
                        The address where the apolloserver can be reached
  -b BINDER, --binder BINDER
                        Location of binder file.
```