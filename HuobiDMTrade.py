#-*- coding:utf-8 -*-
from REST-Python3.5-demo.HuobiDMService import HuobiDM
import time
import numpy as np
import os,json
from talib import RSI
import requests
from utils import send_mail

#保存配置信息
config = {}

#日志文件
log_file = 'log/log.txt'

#配置文件
config_file = 'conf.json'

#日志函数
def log(msg):
    global log_file
    cur_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(time.time())))
    if not os.path.isfile(log_file):
        open(log_file,'w')
    open(log_file,'a').write('%s: %s\n'%(cur_time,msg))

#获取我的帐户
def get_my_balance(currency):
    data = list(filter(lambda x: x['currency'] == currency and x['type'] == 'trade',get_balance()['data']['list']))[0]['balance']
    return float(data[:data.find('.')+7])

#获取当前的usdt/btc价格
def get_current_price():
    url = 'https://www.huobi.co/-/x/pro/market/overview5?r=ny2seo'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        price_usdt= data['data'][2]['close']
        return price_usdt
    else:
        return 0
            


#根据k线计算rsi，周期为14
def get_rsi(data):
    #调用talib库计算rsi指标
    close = np.array([x['close'] for x in data])
    real = RSI(close,14)
    return real

#买操作
def buy(cur_price):
    global config
    #获取当前我帐户中的usdt
    my_usdt = get_my_balance('usdt')
    #取小数点后6位
    my_usdt = float('%0.6f' % my_usdt) 
    #若my_usdt不为0的话
    if  int(my_usdt) > 0:
        #下单，以cur_price价钱全部买btc
        #ret = send_order(amount=my_usdt,source='api',symbol='btcusdt',_type='buy-market')
        #config['BUY_PRICE']记下当前买的价格
        config['BUY_PRICE'] = cur_price
        #log(str(ret))
        #在日志文件中记下这个买操作
        log('buy at %f usdt/btc,current balance: %f btc,%f usdt' % (
            cur_price,
            get_my_balance('btc')
            ,get_my_balance('usdt')
            ))
#卖操作
def sell(cur_price):
    global config
    #获取我的帐户中的btc数量
    my_btc = get_my_balance('btc')
    #取小数点后6位
    my_btc = float('%0.6f' % my_btc)
    #若大于0.0001，因为btc是最小交易单位为万分之一比特币
    if  my_btc > 0.0001:
        #下单卖
        #ret = send_order(amount=my_btc,source='api',symbol='btcusdt',_type='sell-market')
        #config['SELL_PRICE']记下当前的卖的价格
        config['SELL_PRICE'] = cur_price
        #log(str(ret))
        #将这次卖操作写入日志文件
        log('sell at %f usdt/btc,current balance: %f btc,%f usdt' % (
            cur_price,
            get_my_balance('btc'),
            get_my_balance('usdt')
            ))

#买时机监控开关
buy_monitor_switch = False
#卖时机监控开关
sell_monitor_switch = False

#量化主函数
def trade():
    #声明全局变量
    global config
    global buy_monitor_switch,sell_monitor_switch

    #获取k线数据，获取从当前向前200个k线数据，每个k线时长为config['period']
    data = get_kline('btcusdt',"%dmin" % config['period'],200)['data']
    #数据反转
    data.reverse()
    #计算rsi,取最后三个rsi值
    rsi1,rsi2,rsi3  = get_rsi(data)[-3:]
    #根据时间戳获取最后一个k线的时间
    cur_time_ = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(data[-1]['id']))
    
    #获取当前的btc/usdt的价格
    cur_price = get_current_price()
    log('%s rsi:%f, price:%f usdt/btc' % (cur_time_,rsi3,cur_price))

    
    #如果rsi3小于30，开启买监控
    if rsi3 < 30:
        buy_monitor_switch =  True
    #如果rsi大于70，开启卖监控
    if rsi3 > 70:
        sell_monitor_switch =  True

    if buy_monitor_switch:      
        #若rsi曲线出线 触底反弹 或者 直接向上突破30 时，发出买的信息 
        if (rsi2 < rsi1 and rsi2 < rsi3) or (rsi3 > 30):
            log('It is time to buy')
            
            try:
                #向用户发出买的信息
                send_mail(title='Buy Signal rsi=%f price= %f' % (rsi3,cur_price),msg='%s rsi:%f, price:%f usdt/btc' % (cur_time_,rsi3,cur_price))
            except:
                pass
        #若rsi向上已经突破30，关闭买操作监控
        if rsi3 > 30 :
            buy_monitor_switch = False
        
    if sell_monitor_switch:
        #若rsi出现 触顶下降 时 或者 向下突破70，发出卖的信息
        if (rsi2 > rsi1 and rsi2 > rsi3) or (rsi3 < 70):
            log('It is time to sell')
            try:
                #向用户发出卖的信号
                send_mail(title='Sell Signal rsi=%f price= %f' % (rsi3,cur_price),msg='%s rsi:%f, price:%f usdt/btc' % (cur_time_,rsi3,cur_price))
            except:
                pass
        #若rsi向下突破70，关闭卖操作监控
        if rsi3 < 70:
            sell_monitor_switch = False
   

#主函数  
def main():
    #声明全局变量
    global config
    #k线的时间区间为15min
    config['period'] = 15
    while True:
        #获取当前的分和秒
        cur_miniute,cur_second = time.strftime("%M:%S", time.localtime(int(time.time()))).split(':')
        cur_miniute = int(cur_miniute)
        cur_second = int(cur_second)
        #如果当前时间为整刻钟
        if cur_miniute % config['period'] == 0 and cur_second == 0:
            try:
                #加载配置文件
                config = json.load(open(config_file,'r'))
                #监控操作
                trade()
            except:
                #出错的话继续
                continue
            finally:
                #配置信息写入文本文件
                json.dump(config,open(config_file,'w'))
            time.sleep(1)

main()