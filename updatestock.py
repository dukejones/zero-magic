# -*- coding: utf-8 -*-
"""
Created on Sun Jan 17 14:29:11 2016

@author: théo
"""

import requests
import sqlite3 as lite
import csv
from lxml import html
import formula as formule

# updates the financial values of stocks in the DB with latest Yahoo Finance data
def ListStocks():
    stocks=csv.reader(open("stocklist.csv","r"), delimiter=";")
    stocklist=[]
    for row in stocks:
        stocklist.extend([row[0]])
    print('Stock list retrieved.')
    return stocklist

#print(ListStocks())

def GetStock(symbol):
    formula=formule.Formula()
    header={'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:32.0) Gecko/20100101 Firefox/32.0',}
    page=requests.get('https://finance.yahoo.com/q/ks?s='+symbol, headers=header)
    page = html.fromstring(page.content)
    data = page.xpath('//*[@class="yfnc_tabledata1"]//text()')
    if not data:
        print('Stock '+symbol+' unfonctional.')
    else:
        price = page.xpath('//*[@class="time_rtq_ticker"]//text()')[0]
        tmp=[data[0],data[29],price,data[34],data[45], formula.NumberTreatment(data[29]),formula.NumberTreatment(data[0]),symbol]   
        con = lite.connect('stock.db')
        cur=con.cursor()     
        cur.execute('UPDATE Stocks_Data SET MarketCap=?, OCF=?, DayMA=?, FiftyWeekHigh=?, ShortRatio=?, OCFN=?, MarketCapN=? WHERE Symbol=?', tmp)
        con.commit()
        con.close()
        con = lite.connect('stock_backup.db')
        cur=con.cursor()     
        cur.execute('UPDATE Stocks_Data SET MarketCap=?, OCF=?, DayMA=?, FiftyWeekHigh=?, ShortRatio=?, OCFN=?, MarketCapN=? WHERE Symbol=?', tmp)
        con.commit()
        con.close()
        print('Stock '+symbol+' updated.')

liste=ListStocks()
for symbol in liste:
    GetStock(symbol)

print('Update finished.\nYou can quit this process.')

