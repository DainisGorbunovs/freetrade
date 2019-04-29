# FreeTrade API
This is an attempt to make an unofficial Python package for [FreeTrade](https://freetrade.io).
There is no official API released, yet. FreeTrade is a zero-fee UK-regulated stockbroker.

## What is supported
* Find list of `tradable securities` with information on the asset class, market, currency, country.
* Create a list of tickers for `Trading View`'s watch list. 
* Find `historical prices` (up to 5 years of past).

## Install
```bash
conda create -n myenv python=3.7
conda activate myenv
pip install -r requirements.txt
```

Alternatively:
```bash
pip install freetrade
```

## API
Create a `FreeTrade` object
```python
from freetrade import FreeTrade

api_key = '...'  # API key
app_id = '...'  # APP ID
ft = FreeTrade(api_key, app_id)
```

The API key and app ID can be found via Charles proxy.

### Get assets
```python
assets = ft.get_assets()
```

Returns a dictionary of different categories, which have subcategories.
These subcategories contain a list of stock assets.
* `currency`
  * `GBP` / `USD`: list of assets
* `exchange`
  * `XLON` / `XNYS` / `XNAS`: list of assets
* `asset_class`
  * `ETF` / `EQUITY` / `ADR`: list of assets
* `country_of_incorporation`
  * `IE` / `GB` / `US` / `KY` / ... : list of assets
* `all`: list of assets

Sample asset for an ETF `LSE:ERNU`:
```json
{
    "asset_class": "ETF",
    "symbol": "ERNU",
    "isin": "IE00BCRY6227",
    "exchange": "XLON",
    "currency": "GBP",
    "country_of_incorporation": "IE",
    "long_title": "iShares $ Ultrashort Bond UCITS ETF (Dist.)",
    "short_title": "$ Ultrashort",
    "subtitle": "Very short maturity $ debt",
    "logo_4x": "//a.storyblok.com/f/41481/640x640/7ec0a292de/ishares-symbol-4x.png",
    "isa_eligible": true,
    "coming_soon": false,
    "required_version": "1.0",
    "objectID": "IE00BCRY6227"
}
```


### Get tickers
```python
tickers = ft.get_tickers()
```

Returns a dictionary, where:
* key is an exchange symbol FreeTrade uses, and
* value is a list of ticker symbols 
```python
tickers = {
    'XLON': ['ERNU', 'III', '3IN', ...],
    'XNYS': ['MMM', 'ABBV', 'BABA', ...],
    'XNAS': ['ATVI', 'ADBE', 'AMD', 'GOOGL', 'AMZN', ...]
}
```

### Get list of tickers for Trading View watch list
```python
tickers_union = ft.get_tradingview_tickers(join_exchanges=True)
```

Returns a string formatted for importing into Trading View watch list.

With `join_exchanges = True`:
```python
tickers_union = 'LSE:ERNU,LSE:III,LSE:3IN,LSE:ABF,LSE:ACA,LSE:ADM,...'
```

Default (when `join_exchanges = False`):
```python
tickers_union = {
    'XLON': 'LSE:ERNU,LSE:III,LSE:3IN,LSE:ABF,LSE:ACA,LSE:ADM,...',
    'XNYS': 'NYSE:MMM,NYSE:ABBV,NYSE:BABA,NYSE:AXP,NYSE:APA,NYSE:T,...',
    'XNAS': 'NASDAQ:ATVI,NASDAQ:ADBE,NASDAQ:AMD,NASDAQ:GOOGL,NASDAQ:AMZN,...'
}
```

### Get ETFs
```python
etfs = ft.get_etfs()
```

Returns a list of ETF assets:
```python
etfs = [<LSE:ERNU asset>, <LSE:CS51 asset>, <LSE:IDVY asset>, ...]
```

### Get price history
```python
prices = ft.get_ticker_history('TSLA', duration='1m')
```
The possible duration values, where `5y` is default: 
* `5y`, `2y`, `1y`, `ytd`, `6m`, `3m`, `1m`, `1d`

Returns a list of data points. Sample output:
```python
prices = [
    {
        "date": "2019-03-28",
        "open": 277.16,
        "high": 280.33,
        "low": 275.1,
        "close": 278.62,
        "volume": 6774093,
        "unadjustedVolume": 6774093,
        "change": 3.79,
        "changePercent": 1.379,
        "vwap": 277.8336,
        "label": "Mar 28",
        "changeOverTime": 0
    }, 
    ...
]
``` 

## Anything else?
* Feel free to make a `GitHub issue`, if you find any issues or have enhancement ideas.

* `Pull requests` are welcome, if you have made improvements to this code.
 