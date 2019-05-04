# FreeTrade API
This is an attempt to make an unofficial Python package for [FreeTrade](https://freetrade.io).
There is no official API released, yet. FreeTrade is a zero-fee UK-regulated stockbroker.

## What is supported
* Find list of `tradable securities` with information on the asset class, market, currency, country.
* Create a list of tickers for `Trading View`'s watch list. 
* `Historical prices`:
  * Find up to 5 years of past;
  * Download or update in `csv` files into `history` directory;
  * Load as `pandas.DataFrame`.

## Install
Install through `pip` package manger:
```bash
pip install freetrade
```

Alternatively, for developing this package:
```bash
conda create -n myenv python=3.7
conda activate myenv
pip install -r requirements.txt
```
## API
Create a `FreeTrade` object
```python
from freetrade import FreeTrade

api_key = '...'  # Algolia API key
app_id = '...'  # Algolia APP ID
quandl_api_key = '...' # Quandl API key
ft = FreeTrade(api_key, app_id, quandl_api_key)
```

The above keys and IDs can be found via Charles proxy:
* `Algolia` key and ID - when browsing/discovering list of assets;
* `Quandl` key - when browsing assets from LSE (London Stock Exchange).

### Sample code of using `ft` object
Assuming `ft` object is created, here is how one month of historical price for a stock.
```python
prices = ft.get_ticker_history('XNAS', 'TSLA')

for history_date, price in prices.items():
    print(f'{history_date}: ${price:.2f}')
```

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

### Get price history
```python
tesla = ft.get_ticker_history('XNAS', 'TSLA', duration='1m')
national_grid = ft.get_ticker_history('XLON', 'NG.', duration='1m')
```

The possible duration values, where `1m` is default: 
* `5y`, `2y`, `1y`, `ytd`, `6m`, `3m`, `1m`, `1d`

Returns an `OrderedDict` of data points `(date, adjusted closing price)` sorted by date in ascending order.

Sample output:
```python
tesla = OrderedDict([
    ('2019-04-04', 267.78),
    ('2019-04-05', 274.96),
    ('2019-04-08', 273.2),
    ('2019-04-09', 272.31),
    ('2019-04-10', 276.06),
    ...
])
``` 

Notes:
* use `Quandl` for UK securities;
* uses `IEXTrading` for other securities.

### Download or update historical prices
```python
ft.update_historical_prices()
```

Saves the adjusted historical closing prices for the assets into `history` directory. If it does not exist, it is created.

The file name is the ticker's symbol, and each the prices are saved in ascending order.

Sample in `history/TSLA.csv`:
```csv
2014-05-05,216.61
2014-05-06,207.28
2014-05-07,201.35
2014-05-08,178.59
2014-05-09,182.26
2014-05-12,184.67
2014-05-13,190.16
...
```

### Load the historical data as `pandas.DataFrame`
This function loads the historical data from `history` directory.
Before this, run `ft.update_historical_prices()` to download the historical data.

Note that some assets have missing prices as they were not traded during that day, thus they show up as `nan`.

```python
df = ft.load_historical_data_as_dataframe()
print(df.head(), df.shape)
```


Sample output:
```text
               CSCO          SVT  ...          WTB          NXT
Date                              ...                          
2014-05-05  19.5875  1486.452691  ...  3650.414898  5184.507159
2014-05-06  19.3870  1489.696450  ...  3659.383977  5137.446580
2014-05-07  19.5150  1509.159006  ...  3645.033451  5094.307715
2014-05-08  19.6413  1510.780885  ...  3677.322133  5082.542570
2014-05-09  19.6430  1512.402765  ...  3676.425226  5070.777425

[5 rows x 341 columns] (1305, 341)
```
## Anything else?
* Feel free to make a `GitHub issue`, if you find any issues or have enhancement ideas.

* `Pull requests` are welcome, if you have made improvements to this code.
 