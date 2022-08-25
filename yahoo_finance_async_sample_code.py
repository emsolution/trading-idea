import asyncio, pandas as pd

from yahoo_finance_async import OHLC, Interval, History
global j
j = 'AUDUSD=X'

async def main():
        result = await OHLC.fetch(symbol=j, interval=Interval.HOUR, history=History.FIVE_DAYS)
        return result['candles']
        # Do something with the result

print(pd.DataFrame(asyncio.run(main())).to_string())