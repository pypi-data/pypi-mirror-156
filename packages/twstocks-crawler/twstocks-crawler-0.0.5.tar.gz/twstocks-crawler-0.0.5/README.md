## 系統需求

- Python > 3.9
- Linux 環境 (Windows 尚未測試過)

## 如何使用

建議先啟用python 虛擬環境

```

# -m venv: 使用 python 內建套件 venv
# venv: 虛擬環境目錄名稱
$ python3 -m venv venv

# 啟用虛擬環境
# source venv/bin/activate

# 安裝測試版本
(venv) $ pip install -i https://test.pypi.org/simple/ twstocks-crawler --extra-index-url https://pypi.org/simple/

(venv) $ python -m twstocks_crawler.main


```

## 參數說明

```
(venv)$ python -m twstocks_crawler.main -h
usage: main.py [-h] [-o OUTPUT] [--logfile LOGFILE] [-w CONN_WORKERS] [-i INDUSTRY] [-p PROXY]

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Output destination directory
  --logfile LOGFILE     log filename
  -w CONN_WORKERS, --conn_workers CONN_WORKERS
                        connection workers
  -i INDUSTRY, --industry INDUSTRY
                        specific industry
  -p PROXY, --proxy PROXY
                        proxy url
```

- -i 要爬取的產業別名稱
- -o, --output 輸出的 json 檔目錄位置，目錄需先存在
- --logfile log 輸出檔名，相對路徑或絕對路徑皆可
- -w, --conn_workers 在爬取所有個股時的 worker 數量，建議需與 -p, --proxy 同時使用
- -p, --proxy 建議使用 SOCKS5 proxy ，其他形式 proxy 尚未測試過。注意：就算有設定 proxy 在爬取時也有可能不使用 proxy (亂數決定)。

  可同時輸入多組 proxy 例如： -p socks5://127.0.0.1:7777 -p socks5://127.0.0.1:7070

worker 需與 proxy 同時使用，因為當只有設定 worker = 2 並未設定 proxy 時，代表同時會有兩個爬蟲連線，就算每次爬取中有間格數秒也容易被對方發現進而阻擋爬蟲。

目前每個 worker 每股的爬取間格設定為 3.5 秒比較不會被對方伺服器阻擋。

所以建議 proxy 的數量為 worker - 1

### 範例

```

(venv) $ python -m twstocks_crawler.main -p socks5://127.0.0.1:7777 -w 2 --logfile /tmp/socks.log -o stocks

```

代表爬蟲同時有兩個連線 worker ，隨機取用 proxy 或直接連線，並且將 log 檔輸出至 /tmp/socks.log 位置，輸出的 json 檔位置為當下路徑的 stocks 資料夾

## 輸出

預設輸出的 json 會有：

1. {date|yyyymmdd}_listed.json： 當日上市股票的匯整
2. {date|yyyymmdd}_{產業別}_diff.json：當日各產業別收盤漲幅前 3 名的股票

## 原始碼說明

```
src
└── twstocks_crawler
    ├── __init__.py
    ├── log.py                  # 設定 log
    ├── main.py                 # 控制流程及接收 cli 參數
    ├── repositories            # 爬取外部資源的資料夾分類
    │   ├── industry_diff.py    # 擷取產業別漲幅模組
    │   ├── __init__.py
    │   └── stock_profiles.py   # 擷取當日上市的股票資訊
    ├── utils.py                # 跟股票無關的小工具
    └── version.py              # 版本資訊
```

![This is an image](/Flowchart.jpg)

main() 控制主要流程：

- get_stocks_profiles 取得上市股票基本資訊
- parse_stocks_profiles 基本資料清理
  - 輸出 json

- get_industry_diff 整理過後的股票基本資訊根據產業別做分類，取得股票代號
  - pick_proxy 亂數取得 proxy url
  - worker_cosumer 建立 worker consumer 抓資料
    - worker 從 queue 中取出要抓取的股票代號
      - get_price 取得股票當日收盤價
  - 輸出 json

流程中只要某一股票的 get_price 失敗，exception 會一路傳到 get_industry_diff 處理，讓該產業別跳過不處理，否則會在資料不全的情況下計算前三名的漲幅。

若觀察到 Log 檔中有某些產業別未成功產出，就可以再針對未產出的產業別重新執行一次，如下：

```
(venv)$ python -m twstocks_crawler.main -p socks5://127.0.0.1:7777 -w 2 --logfile /tmp/socks.log -o stocks -i 食品工業 -i  電腦及週邊設備業

```

### 設計考量

從 pick_proxy、worker_cosumer、worker 到 get_price 都是非同步機制實作的。
在一開始設計時是採用同步 requests 抓個股收盤價，此時發現 IP 時常會被阻擋，
所以才設計出 proxy 池的概念，從中挑選 proxu url 並開多個 worker 來消化要抓的股票資料，加速整體爬蟲流程。

爬取時間比較：

- 非同步機制: 30 分鐘左右
  (worker=2, 並增加一個 proxy 來處理)
- 同步機制: 60 分鐘左右

另外有發現 TWSE 有提供當日的所有股價 CSV 資料，或許直接爬這個 API 就可以了，不需這麼麻煩分一個個股票去爬。

https://www.twse.com.tw/exchangeReport/MI_INDEX?response=csv&date={datestr}&type=ALL


### 開發說明

需要 git clone 整個專案才能進行開發

```
$ git clone https://github.com/sunaley/stocks.git stocks

$ cd stocks

# 建立並進入虛擬環境
$ python3 -m venv venv

# 安裝
$ pip install -e .
$ pip install -r requirements.txt

# 開發完畢於 src/twstocks_crawler/version.py 修改版本資訊
# 因尚未串接 Github action 發佈仍須以下手動步驟
# 發佈測試
$ make release-test

# 發佈正式版
$ make release

```

### 測試說明

需要 git clone 整個專案才能進行測試

```
$ git clone https://github.com/sunaley/stocks.git stocks

$ cd stocks

# 建立並進入虛擬環境
$ python3 -m venv venv
$ source venv/bin/activate

# 開始測試
(venv) $ make test

```

目前只有測試
parse_stocks_profiles, get_industry_diff 兩個 function，會依據事先準備好的 html, json 檔當作資料來源，替換模組中發送 request 的部分，將模擬爬蟲抓到的資料當作參數傳給 parse_stocks_profiles, get_industry_diff ，最後檢查輸出是否符合邏輯。

在 pick_proxy、worker_cosumer、worker 到 get_price 這些 function 都是以非同步的機制實作並且使用 worker consumer 的方式，要加上測試有些困難，這次實作並未加入測試。

## 如何部署

因實作時間不夠，預計有以下工作待完成：

- 使用 boto3 設計一個 upload script 讓 twstocks_crawler.main 可呼叫

  並提供一個 cli 介面(或 config file) 可以設定好相關 credentials 資訊，執行時輸出 json 檔案並上傳到 AWS S3
- 部署至 AWS EC2 主機
  - pip install twstocks_crawler
  - 在 crontab 中加入

      ```* 9 * * * /usr/bin/python3.9 twstocks_crawler.main --logfile stocks.log```

      (每日執行，假設為 UTC 的 9 點也就是台灣時間 17 點資料應該都出來了，)

## 總結

在整個實作過程中，有些顧此失彼的狀態。在一開始發現對方網站會阻擋 IP 的情況，就開始思考非同步的解決方案，然而也因為使用非同步的方式不容易實作，光開發就花許多時間了，最終導致測試不完整，部署也沒有完整的規劃並實作。
應該先以簡單使用 requests 的方式爬取每個股票，雖然比較慢，但至少可以先把整個架構完成，也可以增加測試覆蓋程度，在部署規劃的時間應該也足夠。
先做一個基礎可運作、可測試的版本，未來若有效能考量再重構會是比較好的方式。

問題應該歸咎在於太悶著頭實作，缺少溝通，無法讓其他人可以發現這個狀況進而提醒。
