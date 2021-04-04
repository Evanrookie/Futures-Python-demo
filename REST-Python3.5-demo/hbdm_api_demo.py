#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 17 15:48:13 2018

@author: zhaobo
"""

from HuobiDMService import HuobiDM
from pprint import pprint

#### input huobi dm url
URL = 'api.btcgateway.pro'

####  input your access_key and secret_key below:
ACCESS_KEY = '10f8d42d-49959935-bg2hyw2dfg-faaad'
SECRET_KEY = '770611ca-19b79818-737bc1fe-1abe3'


dm = HuobiDM(URL, ACCESS_KEY, SECRET_KEY)

#### another account:
#dm2 = HuobiDM(URL, "ANOTHER ACCOUNT's ACCESS_KEY", "ANOTHER ACCOUNT's SECRET_KEY")
print(dm)



#%%  market data api ===============


#%% trade / account api  ===============

print (u' 获取用户账户信息 ')
pprint (dm.get_contract_account_info())
pprint (dm.get_contract_account_info("BTC"))

print (u' 获取用户持仓信息 ')
pprint (dm.get_contract_position_info())
pprint (dm.get_contract_position_info("BTC"))

print (u' 合约下单 ')
pprint(dm.send_contract_order(symbol='', contract_type='', contract_code='BTC181228', 
                        client_order_id='', price=10000, volume=1, direction='sell',
                        offset='open', lever_rate=5, order_price_type='limit'))


print (u' 合约批量下单 ')
orders_data = {'orders_data': [
               {'symbol': 'BTC', 'contract_type': 'quarter',  
                'contract_code':'BTC181228',  'client_order_id':'', 
                'price':10000, 'volume':1, 'direction':'sell', 'offset':'open', 
                'leverRate':5, 'orderPriceType':'limit'},
               {'symbol': 'BTC','contract_type': 'quarter', 
                'contract_code':'BTC181228', 'client_order_id':'', 
                'price':20000, 'volume':2, 'direction':'sell', 'offset':'open', 
                'leverRate':5, 'orderPriceType':'limit'}]}
pprint(dm.send_contract_batchorder(orders_data))


print (u' 撤销订单 ')
pprint(dm.cancel_contract_order(symbol='BTC', order_id='42652161'))

print (u' 全部撤单 ')
pprint(dm.cancel_all_contract_order(symbol='BTC'))

print (u' 获取合约订单信息 ')
pprint(dm.get_contract_order_info(symbol='BTC', order_id='42652161'))

print (u' 获取合约订单明细信息 ')
pprint(dm.get_contract_order_detail(symbol='BTC', order_id='42652161', order_type=1, created_at=1542097630215))

print (u' 获取合约当前未成交委托 ')
pprint(dm.get_contract_open_orders(symbol='BTC'))

print (u' 获取合约历史委托 ')
pprint (dm.get_contract_history_orders(symbol='BTC', trade_type=0, type=1, status=0, create_date=7))



