import json
import logging
import asyncio
import itertools
import aiohttp
import pytz
import pandas as pd

from http import HTTPStatus
from datetime import datetime
from aiohttp_socks import ProxyConnector

from ..utils import pick_proxy


TAIPEI_TZ = pytz.timezone('Asia/Taipei')

logger = logging.getLogger(__name__)


class FetchError(Exception):
    def __init__(self, msg, error):
        self.msg = msg
        self.error = error

    def __str__(self):
        return f'{self.msg}, {self.error}'


def collect_data(ticker, response):
    return [{
            'ticker': ticker,
            **dict(zip(response['fields'], data))
        } for data in response['data']
    ]


async def get_price(ticker, proxy_generator):
    url = 'https://www.twse.com.tw/exchangeReport/STOCK_DAY'
    dtime = datetime.now(tz=TAIPEI_TZ)

    def get_session():
        if proxy_url := next(proxy_generator):
            connector = ProxyConnector.from_url(proxy_url)
            return aiohttp.ClientSession(read_timeout=5, connector=connector), proxy_url

        return aiohttp.ClientSession(read_timeout=5), proxy_url

    session, proxy = get_session()
    async with session as session:
        result = []
        try:
            params = {
                'stockNo': ticker,
                'date': dtime.strftime('%Y%m01')
            }
            logger.info(f'Fetching {ticker} price at {params["date"]}, proxy={proxy}, task={asyncio.current_task().get_name()}')
            async with session.get(url, params=params) as resp:
                if resp.status != HTTPStatus.OK:
                    logger.warning(f'Fetching {resp.url} fails.')

                res_dict = await resp.json()

                if 'data' not in res_dict:
                    logger.warning(f'Fetching {resp.url} fails.')
                    logger.debug(f'Response: {res_dict}')
                    raise ValueError('no data found')

                result = collect_data(ticker, res_dict)
                return result
        except Exception as e:
            logger.exception(e)
            raise


def parse_diff(data):
    industry_df = pd.DataFrame.from_records(data)

    date_df = industry_df['日期'].str.split('/', expand=True).astype(int)
    date_df[0] += 1911
    date_df = date_df.astype(str)

    industry_df['date'] = pd.to_datetime(date_df[0] + '-' + date_df[1] + '-' + date_df[2])

    today = industry_df['date'].max()

    industry_df.drop(columns=['日期', '成交股數', '成交金額', '開盤價', '最高價', '最低價', '成交筆數'], inplace=True)
    industry_df.loc[: , '收盤價'] = industry_df['收盤價'].str.replace(',', '')
    industry_df = industry_df[industry_df['收盤價'] != '--']
    industry_df.loc[: , '漲跌價差'] = industry_df['漲跌價差'].str.replace(',', '').str.replace('X', '')
    idx = industry_df.groupby('ticker')['date'].rank('max', ascending=False)

    industry_df.loc[idx == 1, '前一日收盤'] =  industry_df.loc[idx == 2, '收盤價'].tolist()
    industry_df = industry_df.loc[idx == 1, :]
    industry_df[['收盤價', '漲跌價差', '前一日收盤']] = industry_df[['收盤價', '漲跌價差', '前一日收盤']].astype(float)
    industry_df['diff'] = industry_df['漲跌價差'] / industry_df['前一日收盤'] * 100
    industry_df = industry_df.nlargest(3, 'diff')

    industry_df['diff'] = industry_df['diff'].astype(str) + '%'

    industry_df.drop(columns=['收盤價', '前一日收盤', '漲跌價差', 'date'], inplace=True)

    return today, industry_df.to_dict('records')


def empty_queue(queue):
    for _ in range(queue.qsize()):
        queue.get_nowait()
        queue.task_done()


async def worker(name, len_of_tickers, ticker_quene, responses, lock, proxy_generator):
    while True:
        # Get a "work item" out of the queue.
        ticker = await ticker_quene.get()
        try:
            task = asyncio.create_task(get_price(ticker, proxy_generator))
            res, _ = await asyncio.wait([task], return_when=asyncio.ALL_COMPLETED)
            for r in res:
                result = r.result()
                async with lock:
                    if isinstance(result, list):
                        responses.extend(result)

            await asyncio.sleep(3.5)

            logger.info(f'{name} has processed {ticker}, {len_of_tickers - ticker_quene.qsize()}/{len_of_tickers}')

            ticker_quene.task_done()
        except Exception as e:
            ticker_quene.task_done()
            empty_queue(ticker_quene)
            raise FetchError(f'Fetch {ticker} error, giveup whole industry.', e)


async def worker_cosumer(tickers, workers=1, proxy_generator=None):
    # Create a queue that we will use to store our "workload".
    ticker_queue = asyncio.Queue()

    lock = asyncio.Lock()
    responses = []

    for ticker in tickers:
        ticker_queue.put_nowait(ticker)

    # Create three worker tasks to process the queue concurrently.
    tasks = []
    for i in range(workers):
        task = asyncio.create_task(worker(f'worker-{i}', len(tickers), ticker_queue, responses, lock, proxy_generator))
        tasks.append(task)

    # Wait until the queue is fully processed.
    await ticker_queue.join()

    # Cancel our worker tasks.
    for task in tasks:
        task.cancel()

    # Wait until all worker tasks are cancelled.
    worker_result = await asyncio.gather(*tasks, return_exceptions=True)

    for w_r in worker_result:
        if isinstance(w_r, Exception):
            raise w_r

    data = []
    for res in responses:
        if isinstance(res, dict):
            data.append(res)
    return data


async def get_industry_diff(stock_profiles, worker_cosumer, industries=[], workers=1, save_json_handler=None, proxies=[]):
    df = pd.DataFrame.from_records(stock_profiles)

    proxy_generator = pick_proxy(proxies)

    industry_diff = {}
    for industry, tickers_idx in df.groupby('industry').groups.items():
        if industries and industry not in industries:
            continue

        try:
            logger.info(f'Start to fetch {industry} price')
            data = await asyncio.gather(worker_cosumer(df.loc[tickers_idx,:].ticker.tolist(), workers, proxy_generator), return_exceptions=True)
            for _data in data:
                if isinstance(_data, Exception):
                    raise _data

            data = itertools.chain(*data)

            today, diff_data = parse_diff(list(data))
            industry_diff.update({
                industry: diff_data
            })

            if save_json_handler:
                save_json_handler(diff_data, f'{today:%Y%m%d}_{industry}_diff.json')

        except Exception as e:

            logger.error(f'Process {industry} failed.')
            logger.exception(e)

    return industry_diff
