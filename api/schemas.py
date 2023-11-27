from typing import List

from pydantic import BaseModel


# {
#   "e": "kline",     // Event type
#   "E": 123456789,   // Event time
#   "s": "BNBBTC",    // Symbol
#   "k": {
#     "t": 123400000, // Kline start time
#     "T": 123460000, // Kline close time
#     "s": "BNBBTC",  // Symbol
#     "i": "1m",      // Interval
#     "f": 100,       // First trade ID
#     "L": 200,       // Last trade ID
#     "o": "0.0010",  // Open price
#     "c": "0.0020",  // Close price
#     "h": "0.0025",  // High price
#     "l": "0.0015",  // Low price
#     "v": "1000",    // Base asset volume
#     "n": 100,       // Number of trades
#     "x": false,     // Is this kline closed?
#     "q": "1.0000",  // Quote asset volume
#     "V": "500",     // Taker buy base asset volume
#     "Q": "0.500",   // Taker buy quote asset volume
#     "B": "123456"   // Ignore
#   }
# }


class BinanceDataK(BaseModel):
    t: int
    T: int
    s: str
    i: str
    f: float
    L: float
    o: float
    c: float
    h: float
    l: float
    v: float
    n: int
    x: bool
    q: float
    V: float
    Q: float
    B: int


class BinanceData(BaseModel):
    e: str
    E: int
    s: str
    k: BinanceDataK


class CoinGeckoCourse(BaseModel):
    rub: float
    usd: float


class CoinGeckoData(BaseModel):
    bitcoin: CoinGeckoCourse
    ethereum: CoinGeckoCourse


class CourseSchema(BaseModel):
    direction: str
    value: float


class ResponseSchema(BaseModel):
    exchanger: str
    courses: List[CourseSchema]
