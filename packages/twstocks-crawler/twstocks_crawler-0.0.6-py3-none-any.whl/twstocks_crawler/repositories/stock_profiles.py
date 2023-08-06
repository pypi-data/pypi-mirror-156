import io
import pytz
import pandas as pd
import requests
import logging

from datetime import datetime
from typing import List, Dict, AnyStr, Union

TAIPEI_TZ = pytz.timezone('Asia/Taipei')

logger = logging.getLogger(__name__)


def get_stocks_profiles() -> AnyStr:
    url = 'https://isin.twse.com.tw/isin/C_public.jsp?strMode=2'
    logger.info(f'Fetching stock profiles from {url}')
    res = requests.get(url)
    res.raise_for_status()
    return res.text


def parse_stocks_profiles(text: AnyStr, save_json_handler=None) -> List[Dict]:
    dfs = pd.read_html(io.StringIO(text), encoding='big5', header=0, match='有價證券代號及名稱')

    if len(dfs) != 1:
        raise ValueError

    df = dfs[0]

    df.rename(columns={
        '有價證券代號及名稱': 'ticker_name',
        '上市日': 'listed_at',
        '市場別': 'listed',
        '產業別': 'industry'
    }, inplace=True)

    df.drop(columns=['國際證券辨識號碼(ISIN Code)', 'CFICode', '備註'], inplace=True)

    end_index = df[df['ticker_name'] == '上市認購(售)權證'].index

    df = df.iloc[0:end_index.item(), :].copy()

    df[['ticker', 'name']] = df.loc[:, 'ticker_name'].str.split('\u3000', 1, expand=True)
    df = df[df['listed'] == '上市']
    df.drop(columns=['ticker_name', 'listed'], inplace=True)

    data = df.to_dict('records')

    if save_json_handler:
        date = datetime.now(tz=TAIPEI_TZ)
        save_json_handler(data, f'{date:%Y%m%d}_listed.json')

    return data



