from datetime import datetime, date
from typing import Dict, Union

import requests

from .exceptions import RequestFailedException

BASE_URL = "https://www.otcstreaming.com/api/calculator"


class ProductInfo:
    """A ProductInfo object aggregates information on a product to assist in requesting ISDA Calculator. It also controls the existence and the format of each attributes.

    Parameters
    ----------
    maturity: str
        Maturity of product : date in ISO format representing the date of end of the contract.
    coupon: float
        Coupon
    currency: str
        Currency in which the product is traded.
    recovery: float
        Recovery
    factor: float
        Factor
    """

    def __init__(
        self,
        maturity: Union[str, date] = "5Y",
        coupon: float = 500.0,
        currency: str = "EUR",
        recovery: float = 40.0,
        factor: float = 100.0,
    ):

        if isinstance(maturity, date):
            self.maturity = maturity.isoformat()
        elif isinstance(maturity, str):
            maturities = self.get_maturities()
            if maturity in maturities.keys():
                self.maturity = maturities[maturity]
            else:
                self.maturity = maturity
        else:
            raise TypeError(
                "Maturity must be either : a string in 0Y, 0.25Y, ... 4.5Y, 5Y, 5.5Y, ..., 14.75Y, 15Y, or a date as a date object or as a string in ISO format."
            )

        if isinstance(coupon, (int, float)):
            self.coupon = coupon
        else:
            raise TypeError("coupon must be a number (int or float).")

        if isinstance(currency, str):
            if currency in ["EUR", "USD", "GBP", "JPY"]:
                self.currency = currency
            else:
                raise ValueError(
                    'currency can only be in ["EUR", ""USD", "GBP", "JPY"]'
                )
        else:
            raise TypeError("currency must be a string.")

        if isinstance(recovery, (int, float)):
            self.recovery = recovery
        else:
            raise TypeError("recovery must be a number (int or float).")

        if isinstance(factor, (int, float)):
            self.factor = factor
        else:
            raise TypeError("factor must be a number (int or float).")

    @classmethod
    def from_mnemonic(
        cls,
        mnemonic: str,
        as_of_date: Union[str, date] = date.today(),
    ):
        """Retrieve product information from the mnemonic and the data of trade given.

        Parameters
        ----------
        mnemonic : str
            Mnemonic for the product.
        as_of_date : Union[str, date]
            Date at which to retrieve the information of the product, by default current date.

        Returns
        -------
        ProductInfo
            Information on the product.
        """
        if isinstance(mnemonic, str):
            if isinstance(as_of_date, date):
                as_of_date = as_of_date.isoformat()
            if isinstance(as_of_date, str):
                request_product_info = requests.post(
                    f"{BASE_URL}/productinfo",
                    json={
                        "productMnemonic": mnemonic,
                        "tradeDate": as_of_date,
                    },
                )
                if request_product_info.status_code == 200:
                    product_info = request_product_info.json()
                    return cls(**product_info)
                else:
                    raise RequestFailedException(
                        request_product_info.status_code, request_product_info.json()
                    )
            else:
                raise TypeError(
                    "trade_date must be either a date object or a string in ISO format (YYYY-MM-DD)"
                )
        else:
            raise TypeError("Mnemomic must be a string.")

    @staticmethod
    def get_maturities() -> Dict[str, str]:
        """Retrieve matches between year format maturities and end-date format maturities (ex :5Y <-> 2027-06-20T00:00:00Z)"""
        maturities = {}

        request_maturities_matches = requests.get(
            f"{BASE_URL}/maturities",
            params={"tradeDate": datetime.utcnow().isoformat() + "Z"},
        )

        if request_maturities_matches.status_code == 200:
            maturities_matches = request_maturities_matches.json()
            for match in maturities_matches:
                maturities[match["maturity"]] = match["endDate"]

            return maturities
        else:
            raise RequestFailedException(
                request_maturities_matches.status_code,
                request_maturities_matches.json(),
            )


def isda_calculator(
    productInfo: ProductInfo,
    trade_date: Union[str, date],
    price: Union[int, float],
    price_format: str = "spread",
    size: Union[str, int, float] = "1M",
    direction: str = "buy",
) -> Dict:
    """Request https://www.otcstreaming.com/api/calculator to compute prices for the product information given and other parameters.

    Parameters
    ----------
    productInfo : ProductInfo
        ProductInfo object representing the product to get prices of.
    trade_date : Union[str, date]
        Date of the trade.
    price : Union(int, float)
        Price. Must be a number.
    price_format : str, optional
        Format of the price. Can be "spread", "upfront" or "cash price", by default "spread".
    size : Union[str, int, float]
        Size of the trade. Can be a number or a string representing a compact number as "1K", "1M", "1B"..., by default "1M"
    direction : str, optional
        Direction of the trade, can be "buy" or "sell" by default "buy"

    Returns
    -------
    Dict
        Response from the OTCStreaming's ISDA Calculator :
        {"isdaInterestCurve" : str,
         "prices": {
            "Upfront" : float,
            "Spread" : float,
            "RiskyBp" : float,
            "'FullUpfront" : float,
            "CS01" : float,
            "DirtyUpfront" : float },
         "cashAmount" : float }
    """
    product_info = {}

    if isinstance(productInfo, ProductInfo):
        product_info["maturity"] = productInfo.maturity
        product_info["coupon"] = productInfo.coupon
        product_info["currency"] = productInfo.currency
        product_info["recovery"] = productInfo.recovery
        product_info["factor"] = productInfo.factor

    else:
        raise TypeError("productInfo must be a ProductInfo object.")

    if not isinstance(price, (int, float)):
        raise TypeError("trade_date must be a number.")

    if isinstance(trade_date, date):
        trade_date = trade_date.isoformat()
    elif not isinstance(trade_date, str):
        raise TypeError("trade_date must be a date object or a string.")

    if isinstance(price_format, str):
        if not price_format in ["spread", "upfront", "cash price"]:
            raise ValueError(
                "price_format must be in ['spread', 'upfront', 'cash price']."
            )
    else:
        raise TypeError(
            "price_format must be a string in ['spread', 'upfront', 'cash price']."
        )

    if isinstance(size, (int, float)):
        size = str(size)
    elif not isinstance(size, str):
        raise TypeError("size must be a number or a string.")

    if isinstance(direction, str):
        if not direction in ["buy", "sell"]:
            raise ValueError("direction must be either 'buy' or 'sell'.")
    else:
        raise TypeError("direction must be a string in ['buy', 'sell'].")

    product_info["price"] = price
    product_info["direction"] = direction

    price_format_matches = {"spread": 0, "upfront": 2, "cash price": 3}
    product_info["priceFormat"] = price_format_matches[price_format]

    product_info["size"] = size
    product_info["valueDate"] = trade_date

    request_calculator = requests.post(url=BASE_URL, json=product_info)

    if request_calculator.status_code == 200:
        return request_calculator.json()
    else:
        raise RequestFailedException(
            request_calculator.status_code, request_calculator.json()
        )
