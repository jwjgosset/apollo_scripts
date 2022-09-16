# import obspy
import datetime
import argparse
from pathlib import Path


def getDate(
    args_date: str = None
) -> datetime.datetime:
    if args_date is None:
        return datetime.datetime.now() - datetime.timedelta(days=1)
    else:
        return datetime.datetime.strptime(args_date, "%Y-%m-%d")


def getDirectory(
    baseDir: str,
    workingDate: datetime.datetime
) -> Path:

    dir_str = f'{baseDir}/{workingDate.strftime("%Y/%m/%d")}'

    dir_path = Path(dir_str)

    if not dir_path.exists():
        raise FileNotFoundError((f"No directory for {workingDate} exists in " +
                                baseDir))

    if not dir_path.is_dir():
        raise TypeError(f"{dir_str} is a file, not a directory.")

    return dir_path


def getMiniseedList(
    dir_path: Path
) -> list:

    miniseed_list = []
    for file in dir_path.iterdir():
        if file.is_file():
            miniseed_list.append(file)

    return miniseed_list


def main():
    argsparse = argparse.ArgumentParser()

    argsparse.add_argument(
        '-t',
        '--date',
        help='The date to run the script for, in format YYYY-MM-DD',
        default=None
    )
    argsparse.add_argument(
        'd',
        '--basedirectory',
        help='The base directory to find the miniseed archive in.',
        default='/data/archive/miniseed'
    )

    args = argsparse.parse_args()

    working_date = getDate(args.date)

    miniseed_dir = getDirectory(argsparse.basedirectory, working_date)

    return miniseed_dir


if __name__ == '__main__':
    main()
