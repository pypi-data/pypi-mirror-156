# Hellebore OtcStreaming

API Wrapper for the [OTCStreaming](https://www.otcstreaming.com/)'API.

## Features :
- ISDA Calculator on the base of the [OTCStraming's calculator](https://www.otcstreaming.com/calculator)


## Installation

```sh
pip install ...
```

## Usage

### ISDA Calculator

In order to get ISDA prices for the index `ITXEB536` :
 
```python
from hellebore_otcstreaming import isda_calculator, ProductInfo

ticker = ProductInfo.from_mnemonic("ITXEB535", "2022-05-01")

prices = isda_calculator(ticker, "2022-05-01", price = 10)
```
`prices` is a dict holding values of several price types :
```json
{"cashAmount": 38144.17450850366,
 "isdaInterestCurve": "02-May-2022 EUR",
 "prices": {"CS01": 4.23495037684285,
            "DirtyUpfront": -3.8144174508503657,
            "FullUpfront": 0.410861198242655,
            "Price": 103.6977507841837,
            "RiskyBp": 4.108611982426353,
            "Spread": 10.0,
            "Upfront": -3.697750784183699}}
```
