# from api.variables import Variables
import logging
from collections import OrderedDict
from datetime import datetime
from typing import Union

import services as service
from services import exceptions_manager

from .ws import Bybit


@exceptions_manager
class Agent(Bybit):
    logger = logging.getLogger(__name__)

    def get_active_instruments(self) -> OrderedDict:
        for category in self.category_list:
            instrument_info = self.session.get_instruments_info(category=category)
            for instrument in instrument_info["result"]["list"]:
                Agent.fill_instrument(self, instrument=instrument, category=category)
        for symbol in self.symbol_list:
            if symbol not in self.instruments:
                Agent.logger.error(
                    "Unknown symbol: "
                    + str(symbol)
                    + ". Check the SYMBOLS in the .env.Bitmex file. Perhaps "
                    + "such symbol does not exist"
                )
                Bybit.exit()
                exit(1)
            """if category is not "option":
                tickers = self.session.get_tickers(category=category)
                for ticker in tickers["result"]["list"]:
                    symbol = (ticker["symbol"], category)
                    self.instruments[symbol].update(ticker)
                    self.instruments[symbol]["bidPrice"] = ticker["bid1Price"]
                    self.instruments[symbol]["askPrice"] = ticker["ask1Price"]   """

        return self.instruments

    def get_user(self) -> Union[dict, None]:
        print("___get_user")
        result = self.session.get_uid_wallet_type()
        self.user = result
        id = find_value_by_key(data=result, key="uid")
        if id:
            self.user_id = id
        else:
            self.logNumFatal = 10001
            message = (
                "A user ID was requested from the exchange but was not " + "received."
            )
            Agent.logger.error(message)

    def get_instrument(self, symbol: tuple) -> None:
        print("___get_instrument_data")
        instrument_info = self.session.get_instruments_info(
            symbol=symbol[0], category=symbol[1]
        )
        Agent.fill_instrument(
            self, instrument=instrument_info["result"]["list"][0], category=symbol[1]
        )

    def get_position(self):
        print("___get_position")

    def trade_bucketed(self):
        print("___trade_bucketed")

    def trading_history(self, histCount: int, time: datetime) -> list:
        print("___trading_history")
        time = service.time_converter(time)
        histCount = min(100, histCount)
        trade_history = []
        for category in self.category_list:
            result = self.session.get_executions(category=category, limit=histCount)
            result = result["result"]["list"]
            for row in result:
                row["symbol"] = (row["symbol"], category)
                row["execID"] = row["execId"]
                row["orderID"] = row["orderId"]
                row["category"] = category
                row["lastPx"] = float(row["execPrice"])
                row["leavesQty"] = float(row["leavesQty"])
                row["transactTime"] = service.time_converter(time=int(row["execTime"]) / 1000, usec=True)
                row["commission"] = float(row["execFee"])
                row["clOrdID"] = row["orderLinkId"]
                row["price"] = float(row["orderPrice"])
                row["lastQty"] = float(row["execQty"])
                row["settlCurrency"] = self.instruments[row["symbol"]]["settlCurrency"]
                row["market"] = self.name
                row["foreignNotional"] = 0
                trade_history += result
        trade_history.sort(key=lambda x: x["transactTime"])

        return trade_history

    def open_orders(self) -> list:
        print("___open_orders")
        myOrders = list()
        for category in self.category_list:
            for settleCoin in self.settleCoin_list:
                cursor = "no"
                while cursor:
                    result = self.session.get_open_orders(
                        category=category,
                        settleCoin=settleCoin,
                        openOnly=0,
                        limit=50,
                        cursor=cursor,
                    )
                    cursor = result["result"]["nextPageCursor"]
                    for order in result["result"]["list"]:
                        order["symbol"] = (order["symbol"], category)
                        order["orderID"] = order["orderId"]
                        if "orderLinkId" in order and order["orderLinkId"]:
                            order["clOrdID"] = order["orderLinkId"]
                        order["account"] = self.user_id
                        order["orderQty"] = float(order["qty"])
                        order["price"] = float(order["price"])
                        order["settlCurrency"] = settleCoin
                        order["ordType"] = order["orderType"]
                        order["ordStatus"] = order["orderStatus"]
                        order["leavesQty"] = float(order["leavesQty"])
                        order["transactTime"] = service.time_converter(time=int(order["updatedTime"]) / 1000, usec=True)

                    myOrders += result["result"]["list"]

        return myOrders

    def get_ticker(self) -> OrderedDict:
        print("___get_ticker")

        return service.fill_ticker(self, depth=self.depth, data=self.data)

        # return service.fill_ticker(self, depth=self.depth, data=self.data)

    # del
    """def exit(self):
        print("___exit")"""

    def urgent_announcement(self):
        print("___urgent_announcement")

    def place_limit(self):
        print("___place_limit")

    def replace_limit(self):
        print("___replace_limit")

    def remove_order(self):
        print("___remove_order")

    def get_wallet_balance(self) -> dict:
        print("___wallet_balance")
        result = self.session.get_wallet_balance(accountType="UNIFIED")
        for account in result["result"]["list"]:
            if account["accountType"] == "UNIFIED":
                for coin in account["coin"]:
                    currency = coin["coin"]
                    self.data["margin"][currency] = dict()
                    self.data["margin"][currency] = coin
                    self.data["margin"][currency]["currency"] = currency
                    self.data["margin"][currency]["walletBalance"] = float(
                        coin["walletBalance"]
                    )
                    self.data["margin"][currency]["unrealisedPnl"] = float(
                        coin["unrealisedPnl"]
                    )
                    self.data["margin"][currency]["marginBalance"] = float(
                        coin["equity"]
                    )
                    self.data["margin"][currency]["availableMargin"] = float(
                        coin["availableToWithdraw"]
                    )
                    self.data["margin"][currency]["withdrawableMargin"] = float(
                        coin["availableToWithdraw"]
                    )
                break
        else:
            print("UNIFIED account not found")
        for currency in self.currencies:
            if currency not in self.data["margin"]:
                self.data["margin"][currency] = dict()
                self.data["margin"][currency]["currency"] = currency
                self.data["margin"][currency]["walletBalance"] = None
                self.data["margin"][currency]["unrealisedPnl"] = None
                self.data["margin"][currency]["marginBalance"] = None
                self.data["margin"][currency]["availableMargin"] = None
                self.data["margin"][currency]["withdrawableMargin"] = None

    def get_position_info(self):
        for category in self.category_list:
            for settleCurrency in self.settlCurrency_list[category]:
                if settleCurrency in self.currencies:
                    cursor = "no"
                    while cursor:
                        result = self.session.get_positions(
                            category=category,
                            settleCoin=settleCurrency,
                            limit=200,
                            cursor=cursor,
                        )
                        cursor = result["result"]["nextPageCursor"]
                        for position in result["result"]["list"]:
                            symbol = (position["symbol"], category)
                            if symbol in self.positions:
                                self.positions[symbol] = position
                                self.positions[symbol]["POS"] = float(position["positionValue"])
                                self.positions[symbol]["ENTRY"] = float(position["avgPrice"])
                                self.positions[symbol]["PNL"] = float(position["unrealisedPnl"])
                                self.positions[symbol]["MCALL"] = position["liqPrice"]
                                self.positions[symbol]["STATE"] = position["positionStatus"]


                            # all_positions[symbol][]

    def fill_instrument(self, instrument: dict, category: str):
        symbol = (instrument["symbol"], category)
        self.instruments[symbol] = instrument
        if "settleCoin" in instrument:
            self.instruments[symbol]["settlCurrency"] = instrument["settleCoin"]
        if "deliveryTime" in instrument:
            self.instruments[symbol]["expiry"] = instrument["deliveryTime"]
        else:
            self.instruments[symbol]["expiry"] = None
        self.instruments[symbol]["tickSize"] = instrument["priceFilter"]["tickSize"]
        self.instruments[symbol]["lotSize"] = float(
            instrument["lotSizeFilter"]["minOrderQty"]
        )
        self.instruments[symbol]["state"] = instrument["status"]
        self.instruments[symbol]["multiplier"] = 1
        self.instruments[symbol]["myMultiplier"] = 1
        self.instruments[symbol]["fundingRate"] = 0
        if category == "inverse":
            self.instruments[symbol]["isInverse"] = True
        else:
            self.instruments[symbol]["isInverse"] = False
        if instrument["settlCurrency"] not in self.settlCurrency_list[category]:
            self.settlCurrency_list[category].append(instrument["settlCurrency"])
        if instrument["settleCoin"] not in self.settleCoin_list:
            self.settleCoin_list.append(instrument["settleCoin"])        
        self.instruments[symbol]["volume24h"] = 0


def find_value_by_key(data: dict, key: str) -> Union[str, None]:
    for k, val in data.items():
        if k == key:
            return val
        elif isinstance(val, dict):
            res = find_value_by_key(val, key)
            if res:
                return res
        elif isinstance(val, list):
            for item in val:
                if isinstance(item, dict):
                    res = find_value_by_key(item, key)
                    if res:
                        return res
