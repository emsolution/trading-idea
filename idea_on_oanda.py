import json, requests, numpy as np, pandas as pd
import yfinance as yf, time, schedule
import robot_with_yfinance_v2 as ryf
global open_pair, SECURE_HEADER , base_url, api_key, account, t2, t3, open_position

api_key = '72c8dd8051cc00e79df49a009c7ea1b3-7fdedcd86704e9d011a0567862b570b7'
account = '101-001-22952778-001'
session = requests.Session()
base_url =   "https://api-fxpractice.oanda.com/v3"
SECURE_HEADER ={"Authorization": f"Bearer {api_key}"}

PRICING_PATH = f'/accounts/{account}/pricing'
ORDER_PATH = f'/accounts/{account}/orders'
TRADE_PATH = f'/accounts/{account}/openTrades'
#query_key = ('instruments0', 'instruments1', 'instruments2', 'instruments3', 'instruments4')
query_value = ['EUR_USD', 'EUR_GBP', 'GBP_USD', 'NZD_USD', 'AUD_USD', 'NZD_CAD', 'AUD_CAD', 'EUR_JPY', 'AUD_JPY','USD_JPY', 'USD_CAD',  'CAD_JPY', 'NZD_JPY']
#body={"order": {"units": "100","instrument": f"{j}","timeInForce": "FOK","type": "MARKET","positionFill": "DEFAULT"}}
open_pair, open_position ={}, {}

t1 = 'M2'
t2 = 'M5'
t3 = 'M15'
def place_order(lots=100):
	trade_check = session.get(f'{base_url}{TRADE_PATH}', headers = SECURE_HEADER)
	try:
		for l, k in enumerate(trade_check.json()["trades"]):
			open_position[f'{k["instrument"]}'] = [k['id'], k["currentUnits"]]
	except:
		pass
	for j in query_value:
		print(f'which{j}')
#		w = ''.join(j.split('_'))
#		w = w if w[:3] =='USD' else w[3:]
		result = ryf.final_get(j,t1, t2)
		if result is not None:
			oan_res = '-' if result[0] == 'sell' else ''
			units_factor = 1 if result[0] == 'buy' else -1
			units = units_factor * lots
			entry = result[1]
			if result[0] == 'buy':
				tp = entry + 0.0013
			else:
				tp = entry - 0.0013
			
			body={"order": {"price": f"{entry}","trailingStopLossOnFill": {"timeInForce": "GTC","distance": "0.0005"},"takeProfitOnFill": {"price": f"{tp}"},"timeInForce": "GTC","instrument": f"{j}","units": f"{units}","type": "LIMIT","positionFill": "DEFAULT"}}
			if j not in open_pair  and j not in open_position:
				print('open new order')
				#query = {'instruments': f'{j}'}
				#resp = session.get(f'{base_url}{PRICING_PATH}', headers = SECURE_HEADER, params = query)
				q = session.post(f'{base_url}{ORDER_PATH}', headers = SECURE_HEADER, json =body)
				if q.status_code == 201:
					open_pair[j] = [q.json()["orderCreateTransaction"]["id"], q.json()["orderCreateTransaction"]["units"]]
				print(q.status_code, q.json())
			#print(resp.json()['prices'][0]['bids'][0]['price'])
			
			elif (j in open_pair and j not in open_position and oan_res == open_pair[j][1][0]):
				
				print('replaced former order')
				CANCEL_PATH = f'/accounts/{account}/orders/{open_pair[j][0]}/cancel'
				q = session.put(f'{base_url}{CANCEL_PATH}', headers = SECURE_HEADER)
				q = session.post(f'{base_url}{ORDER_PATH}', headers = SECURE_HEADER, json =body)
				if q.status_code == 201:
					open_pair[j] = [q.json()["orderCreateTransaction"]["id"], q.json()["orderCreateTransaction"]["units"]]
				print(q.status_code, q.json())
			
			
			elif (j in open_pair and j not in open_position and oan_res != open_pair[j][1][0]):
				print('cancelled former order')
				CANCEL_PATH = f'/accounts/{account}/orders/{open_pair[j][0]}/cancel'
				q = session.put(f'{base_url}{CANCEL_PATH}', headers = SECURE_HEADER)
				q = session.post(f'{base_url}{ORDER_PATH}', headers = SECURE_HEADER, json =body)
				if q.status_code == 201:
					open_pair[j] = [q.json()["orderCreateTransaction"]["id"], q.json()["orderCreateTransaction"]["units"]]
				print(q.status_code, q.json())
			
			
			elif  (j in open_position and oan_res != open_position[j][1][0]):
				print('cancelled former position')
				body1 = {"units" : "ALL"}
				CLOSE_POSITION_PATH = f'/accounts/{account}/trades/{open_position[j][0]}/close'
				q = session.put(f'{base_url}{CLOSE_POSITION_PATH }', headers = SECURE_HEADER, json =body1)
				del open_position[j]
				q = session.post(f'{base_url}{ORDER_PATH}', headers = SECURE_HEADER, json =body)
				if q.status_code == 201:
					open_pair[j] = [q.json()["orderCreateTransaction"]["id"], q.json()["orderCreateTransaction"]["units"]]
				print(q.status_code, q.json())
	print(trade_check.json())



def trading():
	schedule.every(105).seconds.do(place_order,15000)
	while True:
		schedule.run_pending()
		time.sleep(27)


if __name__=='__main__':
	trading()