import asyncio
import json
import argparse
import pathlib

from .repositories.industry_diff import get_industry_diff, worker_cosumer
from .repositories.stock_profiles import get_stocks_profiles, parse_stocks_profiles
from .log import get_logger

BASE_DIR = pathlib.Path(__file__).parent

parser = argparse.ArgumentParser()
parser.add_argument("-o", '--output', help="Output destination directory", default='.')
parser.add_argument("--logfile", help="log filename")
parser.add_argument("-w", "--conn_workers", help="connection workers", default=1)
parser.add_argument("-i", "--industry", help="specific industry", action='append')
parser.add_argument("-p", "--proxy", help="proxy url", action='append')
args = parser.parse_args()
output_dir = args.output
log_filename = args.logfile

logger = get_logger('', log_filename)


def main():
    industry = args.industry if args.industry else []
    proxy = args.proxy if args.proxy else []
    workers = int(args.conn_workers) if args.conn_workers else 1

    text = get_stocks_profiles()

    profiles = parse_stocks_profiles(text, save_json)

    asyncio.run(get_industry_diff(profiles, worker_cosumer, industry, workers, save_json, proxy))


def save_json(data, filename):
    if output_dir:
        filename = pathlib.Path(output_dir).joinpath(pathlib.Path(filename))

    with open(filename, 'w') as fout:
        fout.write(json.dumps(data, ensure_ascii=False, separators=(',', ':')))


if __name__ == '__main__':
    main()
