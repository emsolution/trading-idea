import MetaTrader5 as mt5
from datetime import datetime,timedelta
import pandas as pd
import pytz
import schedule
import time
import pandas_ta as ta

global count, rates_frame, watch_list, watch_list_pair, price, points, get_time, last_index, trade_index, trade_on, trade_order, order_type, sl, tp, sl_distance, open_price

mt5.initialize()

watch_list = watch_list_pair = []

def open_position(pair,order_type,size,sl,tp):
	symbol_info=mt5.symbol_info(pair)
	if symbol_info is None:
		print(pair,'not found')
		return
	if not symbol_info.visible:
		print(pair,'is not visible, trying to switch on')
		if not mt5.symbol_select(pair,True):
			print('symbol_select ({}) failed, exit',format(pair))
			return
	print(pair,'found!')
	
	if (order_type=='buy'):
		order=mt5.ORDER_TYPE_BUY
		price=mt5.symbol_info_tick(pair).ask
	elif (order_type=='sell'):
		order=mt5.ORDER_TYPE_SELL
		price=mt5.symbol_info_tick(pair).bid
	else:
		pass
		
	request={'action':mt5.TRADE_ACTION_DEAL,'symbol':pair,'volume':float(size),'type':order,'price':price,'sl':sl,'tp':tp,'magic':234000,'comment':'open a trade','type_time':mt5.ORDER_TIME_GTC,'type_filling':mt5.ORDER_FILLING_IOC,}
	result=mt5.order_send(request)
	if result.retcode != mt5.TRADE_RETCODE_DONE:
		print('failed to send order:')
		open_position(pair,order_type,size,sl,tp)
	else:
		print('order successfully placed')
		last_index=rates_frame.tail(1).index.item()
		trade_index=last_index
		trade_order=order_type
		trade_on=True
		volume=size
		open_price=mt5.positions_get(symbol=pair).price_open
		sl_distance=abs(open_price-sl)
		check_list=[pair,sl,open_price,volume,trade_order,tp,sl_distance,trade_index]
		watch_list.append(check_list)
		check_list.clear()
		watch_list_pair.append(pair)
		
def positions_get(symbol=None):
	if (symbol is None):
		resp=mt5.positions_get()
	else:
		resp=mt5.positions_get(symbol=symbol)
	if(resp is not None and resp != ()):
		df=pd.DataFrame(list(resp),columns=resp[0]._asdict().keys())
		df['time']=pd.to_datetime(df['time'],unit='s')
		return df
	return pd.DataFrame()
	
def close_position(deal_id):
		open_positions=positions_get()
		open_positions=open_positions[open_positions['ticket']==deal_id]
		order_type=open_positions['type'][0]
		symbol=open_positions['symbol'][0]
		volume=open_positions['volume'][0]
		if (order_type==mt5.ORDER_TYPE_BUY):
			order_type=mt5.ORDER_TYPE_SELL
			price=mt5.symbol_info_tick(symbol).bid
		else:
			order_type=mt5.ORDER_TYPE_BUY
			price=mt5.symbol_info_tick(symbol).ask
		close_request={'action':mt5.TRADE_ACTION_DEAL,'symbol':symbol,'volume':float(volume),'type':order_type,'position':deal_id,'price':price,'magic':234000,'comment':'close a trade','type_time':mt5.ORDER_TIME_GTC,'type_filling':mt5.ORDER_FILLING_IOC,}
		result=mt5.order_send(close_request)
		if result.retcode != mt5.TRADE_RETCODE_DONE:
			print('failed to close order:')
			close_position(deal_id)
		else:
			print('order successfully closed')
			watch_list.pop(count)
			watch_list_pair.pop(count)
	
def close_positions_by_symbol(symbol):
	open_positions=positions_get(symbol)
	open_positions['ticket'].apply(lambda x: close_position(x))
	
def get_data(pair,time_frame):
	#utc_from=datetime(2020,1,1,tzinfo=pytz.timezone('   '))
	date_to=datetime.now().astimezone(pytz.timezone('Europe/London'))
	date_to=datetime(date_to.year,date_to.month,date_to.day,hour=date_to.hour,minute=date_to.minute)
	utc_from = date_to - timedelta(hours = 600)
	rates=mt5.copy_rates_range(pair,time_frame,utc_from,date_to)
	rates_frame=pd.DataFrame(rates)
	rates_frame.drop(rates_frame.tail(1).index,inplace=True)
	rates_frame['hlo3']=(1/3)*(rates_frame['high']+rates_frame['low']+rates_frame['open'])
	rates_frame['hlcc4']=(1/4)*(rates_frame['high']+rates_frame['low']+rates_frame['close']+rates_frame['close'])
	rates_frame['DEMA']=round(ta.dema(rates_frame['hlcc4'],13),int(str(points)[-1]))
	rates_frame['TEMA']=round(ta.tema(rates_frame['hlcc4'],9),int(str(points)[-1]))
	macd,macdsignal,macdhist=ta.MACDEXT(rates_frame['hlcc4'],5,3,34,0,5,4)
	rates_frame['macdhist']=round(macdhist,int(str(points)[-1]))
	x = rates_frame['macdhist'].tolist()
	x.pop()
	x.insert(0,None)
	rates_frame=rates_frame.assign(macdhist_alert = x)
	rates_frame['macdhist_alert']=round((rates_frame['macdhist']-rates_frame['macdhist_alert']),int(str(points)[-1]))
	rates_frame.loc[((rates_frame['DEMA']>rates_frame['hlo3']) & (rates_frame['DEMA'] > rates_frame['close'])),'DEMA_alert']='sell'
	rates_frame.loc[(rates_frame['DEMA'] < rates_frame['hlo3'] & (rates_frame['DEMA'] < rates_frame['close'])),'DEMA_alert']='buy'
	a=rates_frame['TEMA'].tolist()
	a.pop()
	a1=a.copy()
	a.pop()
	a2=a.copy()
	a1.insert(0,None)
	a2.insert(0,None)
	a2.insert(0,None)
	rates_frame=rates_frame.assign(tema1=a1)
	rates_frame=rates_frame.assign(tema2=a2)
	
	rates_frame.loc[((rates_frame['tema1']>=rates_frame['tema2'])& (rates_frame['tema1']<rates_frame['TEMA'])) | ((rates_frame['tema1']>rates_frame['tema2'])& (rates_frame['tema1']==rates_frame['TEMA'])),'TEMA_alert']='buy'
	rates_frame.loc[((rates_frame['tema1']<=rates_frame['tema2'])& (rates_frame['tema1']>rates_frame['TEMA'])) | ((rates_frame['tema1']<rates_frame['tema2'])& (rates_frame['tema1']==rates_frame['TEMA'])),'TEMA_alert']='sell'
	rates_frame.loc[((((rates_frame['macdhist_alert'] > 0) & (abs(rates_frame['macdhist']) > 0.0001)) & (rates_frame['DEMA_alert'] == 'buy')) & (rates_frame['TEMA_alert'] == 'buy')),'final_alert'] = 'buy'
	rates_frame.loc[((((rates_frame['macdhist_alert'] < 0) & (abs(rates_frame['macdhist']) > 0.0001)) & (rates_frame['DEMA_alert'] == 'sell')) & (rates_frame['TEMA_alert'] == 'sell')),'final_alert'] = 'sell'
	return rates_frame
	
	
def run_trader():
	pairs=['EURUSD','USDCAD','AUDUSD','GBPUSD','USDJPY','USDCHF','NZDUSD','EURGBP','USDMXN','USDZAR','USDCNH','AUDNZD','XAUUSD','XAGUSD','AUDJPY','EURJPY']
	for pair in pairs:
		time_frame=mt5.TIME_FRAME_M30 if ('X' in pair) else mt5.TIME_FRAME_M12
		if mt5.symbol_info(pair).spread <=8:
			points=mt5.symbol_info(pair).point
			data=get_data(pair,time_frame)
			order_type=data['final_alert'].iloc[-1]
			positions=positions_get(pair)
			trade_on=False if (positions == None) else True
			alert = True if(order_type == 'buy' or order_type == 'sell') else False
			if (alert == True ) and (trade_on == False):
				if (order_type == 'buy'):
					conversion_factor = 1 if pair[:3] == 'USD' else mt5.symbol_info_tick(pair[:3] + 'USD').ask if mt5.symbol_info(pair[:3] + 'USD') is not None else (1/mt5.symbol_info_tick('USD' + pair[:3]).ask)
					sl = min(data['low'].iloc[-1],data['low'].iloc[-2])
					tp= 2 * (data['high'].iloc[-1])
					buy_price = mt5.symbol_info_tick(pair).ask
					sl_dist = (abs(buy_price - sl)) / points
					free_margin = mt5.account_info().margin_free
					free_to_loss_margin = free_margin/100
					size = round((free_to_loss_margin * sl)/((sl - buy_price)*conversion_factor * 100000),2)
					size = 25 if (size > 25) else size
					size = 0.01 if (size < 0.01) else size
					if (order_type != data['final_alert'].iloc[-2]) or ((order_type == data['final_alert'].iloc[-2]) and (order_type != data['final_alert'].iloc[-3])):
						if (mt5.account_info().margin_level > 120):
							open_position(pair,order_type,size,sl,tp)
						else:
							continue
					elif (data['TEMA'].iloc[-1] < data['hlcc4'].iloc[-1]):
						if (mt5.account_info().margin_level > 120):
							open_position(pair,order_type,size,sl,tp)
						else:
							continue
				else:
					conversion_factor = 1 if pair[:3] == 'USD' else mt5.symbol_info_tick(pair[:3] + 'USD').bid if mt5.symbol_info(pair[:3] + 'USD') is not None else (1/mt5.symbol_info_tick('USD' + pair[:3]).bid)
					sl = min(data['high'].iloc[-1],data['high'].iloc[-2])
					tp= 0.5 * (data['low'].iloc[-1])
					sell_price = mt5.symbol_info_tick(pair).bid
					sl_dist = (abs(sell_price - sl)) / points
					free_margin = mt5.account_info().margin_free
					free_to_loss_margin = free_margin/100
					size = round((free_to_loss_margin * sl)/((sell_price - sl)*conversion_factor * 100000),2)
					size = 25 if (size > 25) else size
					size = 0.01 if (size < 0.01) else size
					if (order_type != data['final_alert'].iloc[-2]) or ((order_type == data['final_alert'].iloc[-2]) and (order_type != data['final_alert'].iloc[-3])):
						if (mt5.account_info().margin_level > 120):
							open_position(pair,order_type,size,sl,tp)
						else:
							continue
					elif (data['TEMA'].iloc[-1] > data['hlo3'].iloc[-1]):
						if (mt5.account_info().margin_level > 120):
							open_position(pair,order_type,size,sl,tp)
						else:
							continue
						
			elif (trade_on == True):
				count = watch_list_pair.index(pair)
				sl = watch_list[count][1]
				open_price = watch_list[count][2]
				volume = watch_list[count][3]
				trade_order = watch_list[count][4]
				tp = watch_list[count][5]
				#deal_id = watch_list[count][6]
				sl_distance = watch_list[count][6]
				trade_index = watch_list[count][7]
				if (alert == True) and (order_type != trade_order):
					close_positions_by_symbol(pair)
				elif ((data['DEMA_alert'].iloc[-1] != data['final_alert'].iloc[trade_index]) or (data['TEMA_alert'].iloc[-1] != data['final_alert'].iloc[trade_index])):
					close_position_by_symbol(pair)
				

		
def get_order_history(date_from, date_to):
	res= mt5.history_deals_get(date_from, date_to)
	if (res is not None and res != ()):
		df= pd.DataFrame(list(res), columns = res[0]._asdict().keys())
		df['time'] = pd.to_datetime(df['time'], unit = 's')
		return df
	return pd.DataFrame()

def calc_daily_trades():
	now= datetime.now().astimezone(pytz.timezone('Europe/London'))
	now = datetime(now.year, now.month, now.day, hour = now.hour, minute = now.minute)
	midnight = now.replace(hour= 0, minute = 0, second = 0, microsecond = 0)
	res = get_order_history(midnight, now)
	
	if (res.empty):
		return 0
	else:
		lost_trade_count= loss = profit = profit_trade_count = break_even = 0
		for i, row in res.iterrows():
			outcome = float(row['profit'])
			if (outcome > 0):
				profit += outcome
				profit_trade_count += 1
			elif (outcome == 0):
				break_even += 1
			else:
				loss += outcome
				lost_trade_count += 1
				
	return loss,lost_trade_count,profit,profit_trade_count,break_even
	
	
def reports():
	a,b,c,d,e = calc_daily_trades()
	f = c + a
	mydict = {'loss': a, 'Number of lost trades': b, 'profit': c, 'Number of profittable trades': d, 'Number of break even trades': e, 'closing balance': mt5.account_info().balance, 'accumulated daily profit': f}
	print(pd.DataFrame(mydict))
	
def robot_trader():
	hour_of_day = get_time[3]
	day_of_week= get_time[6]
	if ((day_of_week in range(5)) and (hour_of_day in range(7,21)) and ((calc_daily_trades() == 0) or (calc_daily_trades()[0] < 0.035 * (mt5.account_info().margin_free))) and (mt5.account_info().margin_level > 130)):
		run_trader()
		
		
def market_trader():
	get_time = time.gmtime()
	minutes = get_time[4]
	min_6 = minutes % 6
	if (min_6 == 0):
		robot_trader()
	
		
def live_trading():
	schedule.every(2.5).seconds.do(market_trader)
	while True:
		schedule.run_pending()
		time.sleep(1)
		
if __name__ == '__main__':
	live_trading()
	
	
	schedule.every().day.at('22:00').do(reports)