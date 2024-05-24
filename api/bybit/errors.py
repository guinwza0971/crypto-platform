import logging
import traceback
from datetime import datetime, timezone

from api.variables import Variables
from common.variables import Variables as var

logger = logging.getLogger(__name__)


def exception(method):
    """
    Handling HTTP request and websocket errors
    """

    def decorator(*args, **kwargs):
        self: Variables = args[0]
        try:
            result = method(*args, **kwargs)
            if self.logNumFatal < 0:
                self.logNumFatal = 0
            return result
        except Exception as exception:
            name = exception.__class__.__name__
            message = name + " - " + str(exception)
            if name == "ConnectionError":  # requests module
                self.logNumFatal = 1001
            elif name == "SSLError":  # requests module
                self.logNumFatal = 1001
            elif name == "ReadTimeout":  # requests module
                self.logNumFatal = 1001
            elif name == "FailedRequestError":  # pybit http
                self.logNumFatal = 1001
            elif name == "InvalidRequestError":  # pybit http
                if exception.status_code in [
                    10000,
                    10002,
                    10016,
                ]:  # Server Timeout or error
                    self.logNumFatal = 1001
                elif exception.status_code == 10001:  # Request parameter error
                    pass
                elif exception.status_code in [
                    10003,
                    10004,
                    10005,
                    10006,
                    10007,
                    10008,
                    10009,
                    10010,
                    10028,
                    10029,
                    100028,
                    110018,
                ]:  # error sign or the requested symbol is invalid
                    self.logNumFatal = 2001
                elif exception.status_code in [
                    110004,
                    110006,
                    110007,
                    110012,
                    110014,
                    110015,
                    110045,
                    110047,
                    110052,
                    170033,
                    170131,
                    175003,
                    175006,
                    176015,
                    110013,
                    110021,
                ]:  # Insufficient available balance or margin
                    self.logNumFatal = 2
                elif (
                    exception.status_code == 181001
                ):  # category only support linear or option
                    self.logNumFatal = 3
                elif exception.status_code in [
                    170135,
                    170136,
                    170140,
                ]:  # Order quantity exceeded upper limit or lower than the minimum
                    pass
                elif exception.status_code in [
                    170124,
                    170135,
                    170197,
                    170198,
                    170199,
                    170200,
                ]:  # Order amount too large
                    pass
                elif exception.status_code in [
                    170203,
                    170204,
                ]:  # Trigger price cannot be higher or lower...
                    pass
                elif (
                    exception.status_code == 170206
                ):  # Stop_limit Order is not supported within the first 5 minutes of newly launched pairs
                    pass
                elif (
                    exception.status_code == 170133
                ):  # Order price lower than the minimum
                    pass
                elif exception.status_code in [
                    170134,
                    170137,
                    170148,
                ]:  # Order decimal too long
                    pass
                elif (
                    exception.status_code == 10001
                ):  # The number of contracts exceeds maximum limit allowed # Can't query order earlier than 2 years
                    pass
                elif exception.status_code in [
                    170132,
                    170192,
                    170193,
                ]:  # Buy order price cannot be higher
                    pass
                elif exception.status_code == 170194:  # order price cannot be lower
                    pass
                elif exception.status_code in [
                    170195,
                    170196,
                ]:  # Your order may not be filled. Risk control
                    pass
                elif (
                    exception.status_code == 110094
                ):  # Order does not meet minimum order value
                    pass
                elif exception.status_code == 110003:  # Price is out of range
                    pass
                elif exception.status_code in [
                    110001,
                    110008,
                    110010,
                    170139,
                    170142,
                    170213,
                ]:  # Order does not exist
                    pass
                elif exception.status_code in [
                    110009,
                    170341,
                ]:  # The number of stop orders exceeds the maximum allowable limit
                    pass
                elif (
                    exception.status_code == 110020
                ):  # Not allowed to have more than 500 active orders
                    pass
                elif (
                    exception.status_code == 110022
                ):  # Quantity has been restricted and orders cannot be modified to increase the quantity
                    pass
                elif (
                    exception.status_code == 110023
                ):  # Currently you can only reduce your position on this contract. please check our announcement or contact customer service for details.
                    pass
                elif exception.status_code in [110023, 110024]:  # Position mode error
                    pass
                elif exception.status_code in [
                    110072,
                    170141,
                ]:  # OrderLinkedID or clientOrderId is duplicate
                    pass
                elif exception.status_code == 170143:  # Cannot be found on order book
                    pass
                elif exception.status_code == 170210:  # New order rejected
                    pass
                elif (
                    exception.status_code in 40004
                ):  # the order is modified during the process of replacing
                    pass
                else:
                    self.logNumFatal = 1001
            elif name == "InvalidChannelTypeError":  # pybit ws
                self.logNumFatal = 2002
            elif name == "UnauthorizedExceptionError":  # pybit ws
                self.logNumFatal = 1001
            elif name == "TopicMismatchError":  # pybit ws
                self.logNumFatal = 1001
            elif name == "WebSocketTimeoutException":  # pybit ws
                self.logNumFatal = 1001
            else:
                print("_____________error", name)
                traceback.print_exception(
                    type(exception), exception, exception.__traceback__
                )
                # os.abort()
            if message:
                message = message.replace("\n", " ")
                logger.error(message)
                var.queue_info.put(
                    {
                        "market": self.name,
                        "message": message,
                        "time": datetime.now(tz=timezone.utc),
                        "warning": True,
                    }
                )

    return decorator
