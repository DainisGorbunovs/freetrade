# FreeTrade API
This is an attempt to make an unofficial Python package for [FreeTrade](https://freetrade.io).
There is no official API released, yet. FreeTrade is a zero-fee UK-regulated stockbroker.

## What is supported
* Find list of `tradable securities` with information on the asset class, market, currency, country.
* Create a list of tickers for `Trading View`'s watch list. 
* `Historical prices`
* Logging into Freetrade account and saving the session into `ft-session.json` file.

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

## Prerequisites
Before running this, it is necessary to set the API keys. Edit `ft-keys.json` to include the necessary API keys. 
These keys can be found using a tool, which can extract StringCare secrets, e.g. [DeStringCare](https://github.com/DainisGorbunovs/DeStringCare).

## API
### Creating `ft` FreeTrade object
#### Without authentication
```python
from freetrade import FreeTrade

ft = FreeTrade()
```
The only thing which will work is `Index` class, i.e. getting the list of supported stock tickers.

#### With authentication
```python
from freetrade import FreeTrade

email = '...'  # Email to use for the login
ft = FreeTrade(email)
```

By default when creating the object, it will try to load an older authenticated session from `ft-session.json` file.
Otherwise it logs in again, and requests a one time password (OTP), which is sent to the email.

The code parses OTP from the standard user input. Alternatively specify `otp_parser` parameter in `FreeTrade` object
 to a function which can fetch the email and parse the OTP itself.

### `Index` - no authentication needed
#### Get assets
```python
assets = ft.index.get_assets()
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
    "objectID": "IE00BCRY6227",
    ...
}
```

#### Get tickers
```python
tickers = ft.index.get_tickers()
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

#### Get list of tickers for Trading View watch list
```python
tickers_union = ft.index.get_tradingview_tickers(join_exchanges=True)
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

### `API` - requires authentication
#### Ticker history
Assuming `ft` object is created, here is how one month of historical price for a stock.
```python
prices = ft.api.get_ticker_history('TSLA', 'XNAS')

for history_date, price in prices.items():
    print(f'{history_date}: ${price:.2f}')
```

#### Finding the address for a post code
```python
postcode = 'E15JL'
address = ft.api.get_address_by_postcode(postcode)
```

Returns a list of addresses, e.g. sample address:
```json
[{
    "summaryline": "Freetrade, 68-80 Hanbury Street, London, Greater London, E1 5JL",
    "organisation": "Freetrade",
    "number": "68-80",
    "premise": "68-80",
    "street": "Hanbury Street",
    "posttown": "London",
    "county": "Greater London",
    "postcode": "E1 5JL"
}]
```

#### Verifying bank number
```python
bank = ft.api.validate_bank('308012', '15887060')
```

Returns a lot of information on the account number, e.g. sample values:
```json
{
    "result": "VALID",
    "sortcode": "308012",
    "bicbank": "LOYDGB21",
    "bankname": "CITY OFFICE (308012)",
    "owningbank": "LLOYDS BANK PLC",
    "chapssrbicbank": "LOYDGB2L",
    "chapssrbicbr": "XXX",
    ...
}
```

### Get price history
```python
tesla = ft.api.get_ticker_history('TSLA', 'XNAS', duration='1m')
national_grid = ft.api.get_ticker_history('NG.', 'XLON', duration='1m')
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

### `DataStore` - requires authentication
#### Download or update historical prices
```python
ft.datastore.update_historical_prices()
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

#### Load the historical data as `pd.DataFrame`
This function loads the historical data from `history` directory.

Note that some assets have missing prices as they were not traded during that day, thus they show up as `nan`.

```python
df = ft.datastore.load_historical_data_as_dataframe()
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
 