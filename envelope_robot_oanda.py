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
			qwe = qw.copy()
			qwe['Low'] = data['Low']
			qw['High'] = data['High'] 
			data. loc[:, 'HA_High'] = qw.max(axis =1)
			data. loc[:, 'HA_Low'] = qwe.min(axis =1)
			data. loc[:, 'HA_ohhlc'] = (data['HA_High'] + data['HA_High'] + data['HA_Open']+ data['HA_Close']+ data['HA_Low'])/5
			data. loc[:, 'HA_ohllc'] = (data['HA_High'] + data['HA_Open'] + data['HA_Low'] + data['HA_Close'] + data['HA_Low'])/5
			data. loc[:, 'HA_hlc'] = (data['HA_High'] + data['HA_Close']+ data['HA_Low'])/3
					
			data['DEMA'] = ta.hma(data['HA_hlc'], 9)
			#data['TEMA'] = ta.hma(data['HA_hlc'], 7)
			data['macdhist'] = ta.macd(data['HA_hlc'], 7, 37, 5)['MACDh_7_37_5']
			data['ao'] = ta.ao(data['HA_High'], data['HA_Low'])
			points = 0.001 if 'JPY' in pair else 0.00001
			
			x = data['macdhist'].tolist()
			x.pop()
			x.insert(0,None)
			data=data.assign(macdhist_alert = x)
			data['macdhist_alert']=round((data['macdhist']-data['macdhist_alert']),int(str(points)[-1]))
			
			
			y = data['ao'].tolist()
			y.pop()
			y.insert(0,None)
			data=data.assign(ao_alert = y)
			data['ao_alert']=round((data['ao']-data['ao_alert']),int(str(points)[-1]))
			
			data.loc[((data['DEMA'] > data['HA_ohhlc'])),'DEMA_alert']='sell'
			data.loc[(data['DEMA'] < data['HA_ohllc']),'DEMA_alert']='buy'
			#a=data['TEMA'].tolist()
#			a.pop()
#			a1=a.copy()
#			a.pop()
#			a2=a.copy()
#			a1.insert(0,None)
#			a2.insert(0,None)
#			a2.insert(0,None)
#			data=data.assign(tema1=a1)
#			data=data.assign(tema2=a2)
			
			#data.loc[((data['tema1']>=data['tema2'])& (data['tema1']<data['TEMA'])) | ((data['tema1']>data['tema2'])& (data['tema1']==data['TEMA'])),'TEMA_alert']='buy'
			#data.loc[((data['tema1']<=data['tema2'])& (data['tema1']>data['TEMA'])) | ((data['tema1']<data['tema2'])& (data['tema1']==data['TEMA'])),'TEMA_alert']='sell'
			data.loc[((((data['macdhist_alert'] > 0) & (data['ao_alert'] > 0)) & (data['DEMA_alert'] == 'buy'))) ,'final_alert'] = 'buy'
			data.loc[((((data['macdhist_alert'] < 0) & (data['ao_alert'] < 0)) & (data['DEMA_alert'] == 'sell'))),'final_alert'] = 'sell'
			#print(data['final_alert'].to_string())
			return data
		
	
def check_data(pair, t):
		
		data = get(pair, t)
		#g = len(data.index)
		if data is not None :
			ert = data['final_alert'][999-1]
			ert3 = data['final_alert'][999-3]
			ert5 = data['final_alert'][999-5]
			if ert == 'buy' or ert == 'sell':
				n = int(str(points)[-1])
				#print('are')
				if  ert == 'buy':
					a1 = data['Low'][999-1]
					a2 = data['Low'][999-2]
					answer = data['Close'][999-1]
					OK_list = round(answer - (2*points), n)
					
					
				elif ert == 'sell':
					a1 = data['High'][999-1]
					a2 = data['High'][999-2]
					answer = data['Close'][999-1]
					OK_list = round(answer + (20*points), n)
					
					
					
				print(OK_list, answer)
				print('last', a1, 'last second', a2)
				return ert, OK_list, ert3, ert5
		return None


def final_get(pair,p,t):
	a = check_data(pair, p)
	b = check_data(pair, t2)
	c = check_data(pair, t)
	try:
		if a is not None and b is not None and c is not None and a[0] == b[0] == c[0] and c[0] != c[2] and b[0] != b[2]:
			return c
	except:
			return None
			
			
#print(final_get('GBP_USD', 'M5', 'M15'))
#print((int((get('EURGBP', '5m')['Close'][-1])/points))*points)
