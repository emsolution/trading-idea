import requests, pandas as pd

api_key = '72c8dd8051cc00e79df49a009c7ea1b3-7fdedcd86704e9d011a0567862b570b7'
account = '101-001-22952778-001'

base_url =   "https://api-fxpractice.oanda.com/v3"
SECURE_HEADER ={"Authorization": f"Bearer {api_key}"}



#granularity = 'M5'


#base_url =   "https://api-fxpractice.oanda.com/v3"
#SECURE_HEADER ={"Authorization": f"Bearer {api_key}"}

session = requests.Session()
count = 1000

def get_candles(y, granularity):
	instruments = y
	use_url = base_url+f"/instruments/{instruments}/candles"
	params = dict(count = count, granularity = granularity, price= 'MBA')
	#for j in instruments:
	response = session. get(use_url, params= params, headers = SECURE_HEADER)
	data = response.json()
		
	our_data = []
	for candle in data['candles']:
			#if candle['complete'] == False:
#				continue
			new_dict= dict(time = candle['time'], Open = candle['bid']['o'], High = candle['ask']['h'], Low = candle['bid']['l'], Close = candle['ask']['c'])
			our_data.append(new_dict)
	
	candles_df = pd.DataFrame.from_dict(our_data)
	candles_df['time'] = pd.to_datetime(candles_df['time'])
	candles_df['High']= pd.to_numeric(candles_df['High'])
	candles_df['Close'] = pd.to_numeric(candles_df['Close'])
	candles_df[ 'Open'] = pd.to_numeric(candles_df[ 'Open'])
	candles_df['Low'] = pd.to_numeric(candles_df['Low'])
	return candles_df


#check_list = ['EUR_USD','USD_CAD','AUD_USD','GBP_USD','USD_JPY','USD_CHF','NZD_USD','EUR_GBP', 'NZD_CAD']
#print(get_candles('NZD_USD', 'M5').info())

#print(candles_df.to_string())