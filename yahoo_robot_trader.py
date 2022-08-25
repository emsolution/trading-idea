import csv
import pandas_ta as ta
import pandas as pd
import numpy as np
import time
import datetime

#period2 = int(time.time())
#period1 =period2 - 43200000
#interval = '1d'
global qo
qo = ['EURUSD','CAD','AUDUSD','GBPUSD','JPY','CHF','NZDUSD','AUDCAD','CADJPY' ,'AUDNZD','AUDJPY', 'AUDNZD', 'CADJPY','EURGBP','EURJPY','NZDCHF' , 'NZDCAD','MXN','ZAR']
for j in range(19):
    query_string = f'https://query1.finance.yahoo.com/v7/finance/download/{qo[j]}=X?period1=1595030400&period2=1658102400&interval=1d&events=history&includeAdjustedClose=true'
    try:
        f= pd.read_csv(query_string)
    except:
        pass
    else:
            #if len(f) == 0:
               # continue
            info = pd.Series(f['Close'].astype('float64'))
            inf= pd.Series(f['Open'].astype('float64'))
            infa = pd.Series(f['High'].astype('float64'))
            infb = pd.Series(f['Low'].astype('float64'))
            
            f['hlo3']=(1/3)*(infa +infb + inf)
            f['hlcc4']=(1/4)*(infa+infb + info +info)
            f['height'] = infa - infb
            
            f.loc[(info > inf), 'maxi']= f['Close']
            f.loc[(f['Close'] < f['Open']), 'maxi']= f['Open']
            f.loc[(f['Close'] == f['Open']), 'maxi']= f['Close']
            f.loc[(f['Close'] < f['Open']), 'mini']= f['Close']
            f.loc[(f['Close'] > f['Open']), 'mini']= f['Open']
            f.loc[(f['Close'] == f['Open']), 'mini']= f['Close']
            f['maxi']= pd.Series(f['maxi'].astype('float64'))
            f['mini'] = pd.Series(f['mini'].astype('float64'))
            
            maxi_arr = np.array(f['maxi'])
            mini_arr = np.array(f['mini'])
            High_arr = np.array(f['High'])
            Low_arr = np.array(f['Low'])
            ave_arr = (1/2)*(f['maxi'] + f['mini'])
            ave_maxi = (1/4)*(f['maxi'] + f['maxi'] +infa+infb)
            ave_mini = (1/4)*(f['mini'] + f['mini'] +infa+infb)
            
            #print(type(mini_arr[0]))
            num_index = f.tail(1).index.item()
            b1_arr = []
            b2_arr = []
            score_alert =[]
            def diff(arr,i_1, i_2):
                if i_2 >=0:
                    
                    if arr[i_1] > arr[i_2]:
                        return True
                    elif arr[i_1] < arr[i_2]:
                        return False
                    else:
                        return None
                else:
                        None
                        
            for i in range(num_index + 1):
                if (diff(High_arr, i, i-1) == diff(Low_arr, i, i-1) == diff(mini_arr, i, i-1) == diff(maxi_arr, i, i-1) == True):
                    b1_arr.append(2)
                    #print(i, len(b1_arr), b1_arr[-1])
                elif (diff(High_arr, i, i-1) == diff(mini_arr, i, i-1) == diff(maxi_arr, i, i-1) == True) and (diff(Low_arr, i, i-1) != True):
                    b1_arr.append(1.2)
                    #print(i, len(b1_arr), b1_arr[-1])
                elif (diff(Low_arr, i, i-1) == diff(mini_arr, i, i-1) == diff(maxi_arr, i, i-1) == True) and (diff(High_arr, i, i-1) != True):
                    b1_arr.append(1.2)
                    #print(i, len(b1_arr), b1_arr[-1])
                elif (diff(High_arr, i, i-1) == diff(Low_arr, i, i-1) ==  True) and (diff(mini_arr, i, i-1) == diff(maxi_arr, i, i-1) == None):
                    b1_arr.append(1)
                    
                elif ((diff(High_arr, i, i-1) == diff(Low_arr, i, i-1) == True) and (diff(mini_arr, i, i-1) == diff(maxi_arr, i, i-1) != False)):
                    b1_arr.append(1)
                    
                elif (diff(High_arr, i, i-1) == diff(Low_arr, i, i-1) == diff(mini_arr, i, i-1) == diff(maxi_arr, i, i-1) == False):
                    b1_arr.append(-2)
                    #print(i, len(b1_arr), b1_arr[-1])
                elif (diff(High_arr, i, i-1) == diff(mini_arr, i, i-1) == diff(maxi_arr, i, i-1) == False) and (diff(Low_arr, i, i-1) != False):
                    b1_arr.append(-1.2)
                    #print(i, len(b1_arr), b1_arr[-1])
                elif (diff(Low_arr, i, i-1) == diff(mini_arr, i, i-1) == diff(maxi_arr, i, i-1) == False) and (diff(High_arr, i, i-1) != False):
                    b1_arr.append(-1.2)
                    #print(i, len(b1_arr), b1_arr[-1])
                elif (diff(High_arr, i, i-1) == diff(Low_arr, i, i-1) ==  False) and (diff(mini_arr, i, i-1) == diff(maxi_arr, i, i-1) == None):
                    b1_arr.append(-1)
                    
                elif (diff(High_arr, i, i-1) == diff(Low_arr, i, i-1) == False) and (diff(mini_arr, i, i-1) == diff(maxi_arr, i, i-1) != False):
                    b1_arr.append(-1)
                    
                else:
                    b1_arr.append(0)
                    #print(i, len(b1_arr), b1_arr[-1])
                if (diff(High_arr, i, i-2) == diff(Low_arr, i, i-2) == diff(mini_arr, i, i-2) == diff(maxi_arr, i, i-2) == True):
                    b2_arr.append(2)
                    #print(i, len(b1_arr))
                elif (diff(High_arr, i, i-2) == diff(mini_arr, i, i-2) == diff(maxi_arr, i, i-2) == True) and (diff(Low_arr, i, i-2) == None):
                    b2_arr.append(1.2)
                    #print(i, len(b1_arr))
                elif (diff(High_arr, i, i-2) == diff(mini_arr, i, i-2) == diff(maxi_arr, i, i-2) == True) and (diff(Low_arr, i, i-2) == False):
                    b2_arr.append(1)
                
                elif (diff(Low_arr, i, i-2) == diff(mini_arr, i, i-2) == diff(maxi_arr, i, i-2) == True) and (diff(High_arr, i, i-2) == None):
                    b2_arr.append(1.2)
                    #print(i, len(b1_arr))
                
                elif (diff(Low_arr, i, i-2) == diff(mini_arr, i, i-2) == diff(maxi_arr, i, i-2) == True) and (diff(High_arr, i, i-2) == False):
                    b2_arr.append(1)
                
                elif (diff(High_arr, i, i-2) == diff(Low_arr, i, i-2) ==  True) and (diff(mini_arr, i, i-2) == diff(maxi_arr, i, i-2) == None):
                    b2_arr.append(0.7)
                    #print(i, len(b1_arr))
                    #print('i dey oooh 2')
                elif (diff(High_arr, i, i-2) == diff(Low_arr, i, i-2) == True) and (diff(mini_arr, i, i-2) == diff(maxi_arr, i, i-2) != False):
                    b2_arr.append(1)
                    
                elif (diff(High_arr, i, i-2) == diff(Low_arr, i, i-2) == diff(mini_arr, i, i-2) == diff(maxi_arr, i, i-2) == False):
                    b2_arr.append(-2)
                    #print(i, len(b1_arr))
                elif (diff(High_arr, i, i-2) == diff(mini_arr, i, i-2) == diff(maxi_arr, i, i-2) == False) and (diff(Low_arr, i, i-2) == None):
                    b2_arr.append(-1.2)
                    #print(i, len(b1_arr))
                
                elif (diff(High_arr, i, i-2) == diff(mini_arr, i, i-2) == diff(maxi_arr, i, i-2) == False) and (diff(Low_arr, i, i-2) == True):
                    b2_arr.append(-1)
                
                elif (diff(Low_arr, i, i-2) == diff(mini_arr, i, i-2) == diff(maxi_arr, i, i-2) == False) and (diff(High_arr, i, i-2) == None):
                    b2_arr.append(-1.2)
                    #print(i, len(b1_arr))
                
                elif (diff(Low_arr, i, i-2) == diff(mini_arr, i, i-2) == diff(maxi_arr, i, i-2) == False) and (diff(High_arr, i, i-2) == True):
                    b2_arr.append(-1)
                
                elif (diff(High_arr, i, i-2) == diff(Low_arr, i, i-2) ==  False) and (diff(mini_arr, i, i-2) == diff(maxi_arr, i, i-2) == None):
                    b2_arr.append(-0.7)
                    
                elif (diff(High_arr, i, i-2) == diff(Low_arr, i, i-2) == False) and (diff(mini_arr, i, i-2) == diff(maxi_arr, i, i-2) != False):
                    b2_arr.append(-1)
                    
                else:
                    b2_arr.append(0)
                   
            score = (0.63 * (np.array(b1_arr)) + (0.37 * (np.array(b2_arr))))
        
            #f['score'] = score
            
            for i in range(num_index + 1):
                if (score[i] > 0.67) and (score[i-1] >0) and (infa[i] >= f['maxi'][i-2]) and (f['maxi'][i] >= ave_arr[i-2]) :
                    score_alert.append('buy')
                
                elif (score[i] >-0.67) and (1.5 > score[i-1] >0.67):
                    score_alert.append('')
                elif (score[i]< -0.67) and (score[i-1] < 0) and (infb[i] <= f['mini'][i-2]) and (f['mini'][i] <= ave_arr[i-2]):
                    score_alert.append('sell')
                
                elif (score[i] < 0.67) and (-1.5 < score[i-1] < -0.67):
                    score_alert.append('')
                else:
                    score_alert.append(None)
        
            score_alert = np.array(score_alert)
            f['score_alert'] = score_alert
            
            
            
            Mac = ta.macd(info, 5,34,5)
        
            f['ema']=ta.dema(ave_maxi, 10)
            f['dema']=ta.dema(ave_maxi, 8)# I am using tema for dema because it has shown to be smoother and a better filter for noise in the market.
            
            f['tema']=ta.tema(ave_maxi,11)
            
            f['h'] = ta.sma(f['height'], 7)
            height = f['h'].iloc[-1]
            
            
            
            f.loc[f['dema'] > ave_mini,'DEMA_alert']='sell'
            f.loc[(f['dema'] < ave_maxi),'DEMA_alert']='buy'
        
        
            a=f['tema'].tolist()
            a.pop()
            a1=a.copy()
            a.pop()
            a2=a.copy()
            a1.insert(0,np.nan)
            a2.insert(0,np.nan)
            a2.insert(0,np.nan)
            f=f.assign(tema1=a1)
            f=f.assign(tema2=a2)
            	
            f.loc[((f['tema1']>=f['tema2'])& (f['tema1']<f['tema'])) | ((f['tema1']>f['tema2'])& (f['tema1']==f['tema'])),'TEMA_alert']='buy'
            f.loc[((f['tema1']<=f['tema2'])& (f['tema1']>f['tema'])) | ((f['tema1']<f['tema2'])& (f['tema1']==f['tema'])),'TEMA_alert']='sell'
            
            
            
            f.loc[((f['score_alert'] == 'buy') & (f['DEMA_alert'] == 'buy')) & (f['TEMA_alert'] == 'buy')  |((f['score_alert'] != 'sell') & (f['DEMA_alert'] == 'buy')) & (f['TEMA_alert'] == 'buy'),'final_alert'] = 'buy'
            f.loc[((f['score_alert'] == 'sell') & (f['DEMA_alert'] == 'sell')) & (f['TEMA_alert'] == 'sell') |((f['score_alert'] != 'buy') & (f['DEMA_alert'] == 'sell')) & (f['TEMA_alert'] == 'sell'),'final_alert'] = 'sell'
            
            #x_list = list(str(f['Open'].iloc[-1]))
#            x= x_list.index(x_list[-1]) - x_list.index('.')
#            points = 10**(-1*x)

            
            points = 0.00001 if ('JPY' not in qo[j]) else 0.001
            
            f = pd.merge(f, Mac, left_index = True, right_index = True)
            
            f['macdhist']=f['MACDh_5_34_5']
            x = f['macdhist'].tolist()
            x.pop()
            x.insert(0,None)
            f=f.assign(macdhist_alert = x)
            f['macdhist_alert']=round((f['macdhist']-f['macdhist_alert']),5)
            
            if (f['final_alert'].iloc[-1] == 'buy') & (f['final_alert'].iloc[-1] == f['score_alert'].iloc[-1]) & (f['macdhist_alert'].iloc[-1] > 0.00008) :
                comment = f'today\'s market for {qo[j]} will be very bullish and for long'
                order = 'buy limit'
                entry_price = f["Open"].iloc[-1] -  (150*points)
                stop_loss = f['ema'].iloc[-1]
                
            
            elif (f['final_alert'].iloc[-1] == 'buy') & (f['final_alert'].iloc[-1] == f['score_alert'].iloc[-1]):
                comment = f'today\'s market for {qo[j]} will be very bullish but may not be for long'
                order = 'buy limit'
                entry_price = f["Open"].iloc[-1] -  (225*points)
                stop_loss = f['ema'].iloc[-1]
            
            elif ((f['final_alert'].iloc[-1] == 'buy') & (f['final_alert'].iloc[-1] != f['score_alert'].iloc[-1]) & (f['macdhist_alert'].iloc[-1] > 0.00008)):
                comment = f'today\'s market for {qo[j]} will not be very bullish of order 2'
                order = 'buy limit'
                entry_price = f["Open"].iloc[-1] -  (300*points)
                stop_loss = f['ema'].iloc[-1]
            
            elif ((f['score_alert'].iloc[-1] == 'buy') & (f['macdhist_alert'].iloc[-1] > 0.00008)):
                comment = f'today\'s market for {qo[j]} will not be very bullish of order 1'
                order = 'buy limit'
                entry_price = f["Open"].iloc[-1] -  (300*points)
                stop_loss = f['ema'].iloc[-1]
            
            elif (f['final_alert'].iloc[-1] == 'sell') & (f['final_alert'].iloc[-1] == f['score_alert'].iloc[-1]) & (f['macdhist_alert'].iloc[-1] < -0.00008) :
                comment = f'today\'s market for {qo[j]} will be very bearish and for long'
                order = 'sell limit'
                entry_price = f["Open"].iloc[-1] + (150*points)
                stop_loss = f['ema'].iloc[-1]
        
            elif (f['final_alert'].iloc[-1] == 'sell') & (f['macdhist_alert'].iloc[-1] < -0.00008):
                comment = f'today\'s market for {qo[j]} will  not be very bearish of order 2'
                order = 'sell limit'
                entry_price = f["Open"].iloc[-1] + (300*points)
                stop_loss = f['ema'].iloc[-1]
        
            elif (f['score_alert'].iloc[-1] == 'sell') & (f['macdhist_alert'].iloc[-1] < -0.00008):
                comment = f'today\'s market for {qo[j]} will  not be very bearish of order 1'
                order = 'sell limit'
                entry_price = f["Open"].iloc[-1] + (300*points)
                stop_loss = f['ema'].iloc[-1]
        
            elif (f['final_alert'].iloc[-1] == 'sell') & (f['final_alert'].iloc[-1] == f['score_alert'].iloc[-1]):
                comment = f'today\'s market for {qo[j]} will be very bearish but may not be for long'
                order = 'sell limit'
                entry_price = f["Open"].iloc[-1] + (225*points)
                stop_loss = f['ema'].iloc[-1]
            
            
            if (f['final_alert'].iloc[-1] == 'sell') | (f['final_alert'].iloc[-1] == 'buy'):
                try:
                    print(f'comment ={comment} \norder = {order}, \nentry_price = {entry_price}\nstop-loss = {stop_loss}\n distance from low to high = {height}\n\n')
                except:
                    pass
                else:
                    pass
        
        #q = f.loc[:, [ 'Close', 'Open','High', 'Low', 'final_alert', 'score_alert']]
        #print(q.to_string())
        #print(f['score_alert'].to_string() )
         
        