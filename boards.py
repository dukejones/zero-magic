# -*- coding: utf-8 -*-
from lxml import html
import requests
import yahoo_finance
import sqlite3 as lite
import pandas
from lxml import html
import requests
stocks=pandas.read_csv('C:\PythonScripts\stocklist.csv',sep=";")
con = lite.connect('stock.db')
cur=con.cursor()
#cur.execute('CREATE TABLE Board(Symbol TEXT, Name TEXT, Age TEXT)')
for index,row in stocks.iterrows():
    symbol=row['SYMBOL']
    print('Traitement',symbol)
    header = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:32.0) Gecko/20100101 Firefox/32.0',}
    stockPage=requests.get('http://www.reuters.com/finance/stocks/companyOfficers?symbol='+symbol+'.PH', headers=header)
    print('Page recuperee',symbol)
    stockPage = html.fromstring(stockPage.content)
    name = stockPage.xpath('//div[@id="companyNews"][1]/div/div[2]/table[@class="dataTable"][1]/tbody/tr/td[1]/h2/a/text()')
    age = stockPage.xpath('//div[@id="companyNews"][1]/div/div[2]/table[@class="dataTable"][1]/tbody/tr/td[not(@class="data")][2]//text()')
    name=name[:int(len(name)/2)]
    contenu=list(zip([symbol]*len(name),name,age))
    cur.executemany('INSERT INTO Board VALUES(?,?,?)',contenu)
    print('Requete executee',symbol)
con.commit()
con.close()

"""
cur.execute("CREATE TABLE Proximity (Symbols TEXT, Name TEXT, IndexP INT)")
cur.execute("INSERT INTO Proximity (Name, Symbols) SELECT Name, group_concat(Symbol) AS Symbols FROM Board GROUP BY Name, Age")
"""