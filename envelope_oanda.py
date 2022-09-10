import yfinance as yf
import pandas_ta as ta
import numpy as np
import pandas as pd
#import smtplib
#from email.mime.text import MIMEText
#import schedule
import time
import oanda_newfile as on

check_list = ['EURUSD','CAD','AUDUSD','GBPUSD','JPY','CHF','NZDUSD','EURGBP', 'NZDCAD']
t1 = '2m'
t2 = '5m'
t3 = '15m'


def get(pair, t):
		try:
			global points
			data = on.get_candles(pair, t)
			#data = stocks.history(interval = t)
			data.loc[:, 'HA_Close'] = (data['Open'] + data['Low'] + data['Close'] + data['High'])/4
			
			data.loc[:, '_Close'] = np.insert(np.delete(data['Close'].to_numpy(),  -1, None), 0, np.nan)
			data.loc[:, '_Open'] = np.insert(np.delete(data['Open'].to_numpy(), -1, None), 0, np.nan)
			
		except:
			pass
		else:
			
			
			data. loc[:, 'HA_Open'] = (data['_Open'] + data['_Close'])/2
			qw =  pd.merge( data['HA_Open'], data['HA_Close'], right_index = True, left_index = True)
			data['max'] = qw.max(axis=1)
			data['min'] = qw.min(axis=1)
			qwe = qw.copy()
			qwe['Low'] = data['Low']
			qw['High'] = data['High'] 
			data. loc[:, 'HA_High'] = qw.max(axis =1)
			data. loc[:, 'HA_Low'] = qwe.min(axis =1)
			data. loc[:, 'HA_ohhlc'] = (data['HA_High'] + data['HA_High'] + data['HA_Open']+ data['HA_Close']+ data['HA_Low'])/5
			data. loc[:, 'HA_ohllc'] = (data['HA_High'] + data['HA_Open'] + data['HA_Low'] + data['HA_Close'] + data['HA_Low'])/5
			data. loc[:, 'HA_hlc'] = (data['HA_High'] + data['HA_Close']+ data['HA_Low'])/3
					
			data['DEMA'] = ta.ema(data['HA_hlc'], 9)
			data['env_upper'] = data['DEMA']*1.1275
			data['env_lower'] = data['DEMA']*0.8725
			#data['TEMA'] = ta.hma(data['HA_hlc'], 7)
			
			return data
		
buy_wait_dict_1, sell_wait_dict_1={}, {}	
def check_data(pair, t):
		
		data = get(pair, t)
		#g = len(data.index)
		if data is not None :
			art1 = data['min'][on.count-3]
			art2 = data['env_lower'][on.count-3]
			art3 = data['env_upper'][on.count-3]
			art4 = data['max'][on.count-3]
			
			art1b = data['min'][on.count-3]
			art2b = data['env_lower'][on.count-3]
			art3b = data['env_upper'][on.count-3]
			art4b = data['max'][on.count-3]
			
			art1c= data['min'][on.count-3]
			art2c = data['env_lower'][on.count-3]
			art3c = data['env_upper'][on.count-3]
			art4c = data['max'][on.count-3]
			
			art1d = data['min'][on.count-3]
			art2d = data['env_lower'][on.count-3]
			art3d = data['env_upper'][on.count-3]
			art4d = data['max'][on.count-3]
			
			art1e = data['min'][on.count-3]
			art2e = data['env_lower'][on.count-3]
			art3e = data['env_upper'][on.count-3]
			art4e = data['max'][on.count-3]
			
			art1f = data['min'][on.count-3]
			art2f = data['env_lower'][on.count-3]
			art3f = data['env_upper'][on.count-3]
			art4f = data['max'][on.count-3]
			
			ert = data['min'][on.count-3]
			ert3 = data['env_lower'][on.count-3]
			ert3a = data['env_upper'][on.count-3]
			ert5 = data['max'][on.count-3]
			ert1 = data['min'][on.count-2]
			ert2 = data['env_lower'][on.count-2]
			ert2a = data['env_upper'][on.count-2]
			ert4 = data['max'][on.count-2]
			ert9 = data['DEMA'][on.count-3]
			ert6 = data['DEMA'][on.count-2]
			ert8 = data['HA_ohllc'][on.count-1]
			ert8a = data['HA_ohhlc'][on.count-1]
			ert7 = data['DEMA'][on.count-1]
			if ((ert <= ert3 and ert5 >= ert3) or (art1 <= art2 and art4 >= art2) or (art1b <= art2b and art4b >= art2b) or (art1c <= art2c and art4c >= art2c) or (art1d <= art2d and art4d >= art2d) or (art1e <= art2e and art4e >= art2e) or (art1f <= art2f and art4f >= art2f)) and (ert1 > ert2) and (ert6>ert9 and ert7 <= ert8):
				#buy_wait_dict_1[pair] = time.ctime()
				return 'buy'
			elif ((ert5 >= ert3a and ert3a >= ert)  or (art4 >= art3 and art3 >= art1) or (art4 >= art3 and art3 >= art1) or (art4b >= art3b and art3b >= art1b) or (art4c >= art3c and art3c >= art1c) or (art4d >= art3d and art3d >= art1d) or (art4e >= art3e and art3e >= art1e) or (art4f >= art3f and art3f >= art1f)) and (ert4 < ert2a) and (ert6<ert9 and ert7 >= ert8a):
				#sell_wait_dict_1[pair] = time.ctime()
				return 'sell'
					
		return None


def final_get(pair,p):
	final = check_data(pair, p)
	return final
			
			
#print(final_get('GBP_USD', 'M5', 'M15'))
#print((int((get('EURGBP', '5m')['Close'][-1])/points))*points)
