# -*- coding: utf-8 -*-
"""
Created on Thu Dec 24 19:15:47 2015

@author: théo
"""
from lxml import html
from requests import get
import sqlite3 as lite
import time
import formula as formule
import re
from math import log
class Articles:
    def __init__(self):
        self.wtime=0
        print("Initialisation...")
        self.header={'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:32.0) Gecko/20100101 Firefox/32.0',}
    
    def RetrieveArticles(self,url_aut,atype,short):
        # retrieve articles on seekingalpha for short-seller and promoters
        # short variable equals 1 if it is a short-seller article, 0 if a promoter
        # to do : extend it to thestreet.com and other wall street websites
        # first : retrieves the page of the author which includes all the articles written by the author
        author=get(url_aut, headers=self.header)
        print("\nRetrieved webpage: "+url_aut)
        author = html.fromstring(author.content)
        # identifies the number of articles of the author        
        number = author.xpath('//*[@id="profile_tabs"]/li[1]/a/div[2]/text()')[0]
        number=int(number[1:-1].replace(",",""))
        number = 1 + (number // 32)
        # find the number of pages to parse (max : 5 last pages) given that SA displays 32 articles per page
        if number>5:
            number=5
        print("\nNumber of article pages:"+str(number))
        links = author.xpath('//*[@class="author-article-title"]/a/@href')
        # finds all the links of the first page
        for i in range(2,number+1):
            #time.sleep(self.wtime)
            url=url_aut+"/"+str(i)
            author=get(url, headers=self.header)
            print("\nRetrieved webpage: "+url)
            author = html.fromstring(author.content)
            links_tmp=author.xpath('//*[@id="main_container"]/div[2]/div/div[2]/div[1]/div[1]/div/div[1]/a/@href')
            links.extend(links_tmp)
            # finds all the links of the following pages and adds it to links variable
        con = lite.connect('stock.db')
        cur=con.cursor()
        print(links)
        # retrieves each link and gets the information from it : title, stocks talked in the article
        for i in links:
            # time sleep to avoid being IP banned by seekingalpha
            time.sleep(2)
            print("\nRequest executed: "+i)
            url="http://seekingalpha.com"+i
            article=get(url,headers=self.header)
            print("\nRetrieved webpage: "+url)
            article=html.fromstring(article.content)
            stocks=article.xpath('//*[@id="about_primary_stocks"]/a/text()')
            if len(stocks)!=0:
                stocks=stocks[0]
                match = re.search(r"\(([A-Z]+)\)", stocks)
                title=article.xpath('//*[@id="a-hd"]/h1/text()')[0]
                if match is not None:
                    tmp=[url_aut,i,title,match.group(1),short]
                    cur.execute('INSERT INTO Articles VALUES(?,?,?,?,?)',tmp)
                    print("Content stocks: "+str(tmp))
                    print("\nRequest executed: "+title)
            else:
                print("\nUnfunctional article: "+url)                    
        con.commit()
        cur=con.cursor()
        # updates the Promoters and Shortsellers database and indicates that the particular promoter has been "done"
        # in order not to reparse it next time you execute the update
        if short==1:
            table="Shortsellers"
        else:
            table="Promoters"
        cur.execute('UPDATE '+table+' SET Done = 1 WHERE Url=?',[url_aut])
        # tables shortsellers and promoters are quite useless at the moment, we could directly go to Stocks_Data
        # but may be useful in the future
        # now summarise the information: see how many short and promoting article for each stock
        cur.execute('SELECT Symbol FROM Stocks_Data')
        rows=cur.fetchall()
        for row in rows:
            # for each stock, find the number of short & promoting articles
            # (not an optimal loop at all)
            cur.execute('SELECT Author FROM Articles WHERE Stocks = ? AND Short=1',[row[0]])
            articles=cur.fetchall()
            ShortPublic=len(articles)
            cur.execute('SELECT Author FROM Articles WHERE Stocks = ? AND Short=0',[row[0]])
            articles=cur.fetchall()
            PromotersPublic=len(articles)
            cur.execute('UPDATE Stocks_Data SET ShortPublic = ?, PromotersPublic = ? WHERE Symbol = ?',[ShortPublic,PromotersPublic, row[0]])
        con.commit()
        con.close()

def BoardProcessing():
    # updating targeted stocks in board_network database
    con = lite.connect('stock.db')
    cur=con.cursor()
    # first, reset the proximity index, set everyone to 10 except those who have been defined
    # by the user as targeted in table Targeted
    cur.execute('UPDATE Board_Network SET IndexP = 0 WHERE Board_Network.Symbol=(Select Targeted.Code FROM Targeted)')
    cur.execute('UPDATE Board_Network SET IndexP = 10 WHERE IndexP!=0')
    # now, implement the algorithm
    for index in range(0,9):
        print("Index: "+str(index))
        cur.execute('SELECT Linked FROM Board_Network WHERE IndexP = ?',[index])
        symbols=cur.fetchall()
        for symbol in symbols:
            print("Processing stocks: "+symbol[0])
            symbol=symbol[0].split(",")
            tmp=[]
            for i in symbol:
                tmp.append([i])
            cur.executemany('UPDATE Board_Network SET IndexP = '+str(index+1)+' WHERE IndexP = 10 AND Symbol=?',tmp)
    # now, transforms the proximity index of each board member to the proximity index of each company in
    # Stocks_Data table
    print('Launching the big update request on Proximity Index...\n Estimated time: 45 sec')
    cur.execute("UPDATE Stocks_Data SET Proximity = (SELECT Board_Network.IndexP FROM Board_Network WHERE Board_Network.Symbol=Stocks_Data.Symbol) WHERE EXISTS (SELECT * FROM Board_Network WHERE Board_Network.Symbol=Stocks_Data.Symbol)")   
    con.commit()
    con.close()

def ScoreUpdate():
    # updates the score with the formula
    con = lite.connect('stock.db')
    cur=con.cursor()
    # retrieves formula coefficients and stock information
    cur.execute('SELECT Coefficient FROM Formula')
    coeff=cur.fetchall()
    #cur.execute('UPDATE Stocks_Data SET Proximity = 0, ShortPublic = 0, PromotersPublic = 0')
    cur.execute('SELECT Symbol,MarketCapN,ShortRatio,OCFN,Proximity,ShortPublic,PromotersPublic,FiftyWeekHigh,DayMA FROM Stocks_Data WHERE ShortPublic>0 AND Proximity<10 AND OCFN<0 AND MarketCapN<10000000000')
    # AND MarketCapN<10000000000 & OCFN<0
    stocks=cur.fetchall()
    formula=formule.Formula()
    # reset the scores
    cur.execute('UPDATE Stocks_DATA SET Score = NULL')   
    # calculate the score for each of these
    for stock in stocks:
        if formula.NumberTreatment(stock[7])>0:
            distance=100*float(formula.NumberTreatment(stock[7])-formula.NumberTreatment(stock[8]))/float(formula.NumberTreatment(stock[7]))        
        else:
            distance=100
        if stock[1]<0:
            # market cap has to be "logged" to make it more flat
            marketcap=log(abs(stock[1]))
            marketcap=-marketcap
        elif stock[1]==0:
            marketcap=0
        else:
            marketcap=log(abs(stock[1]))
        if stock[3]<0:
            # idem for operating cash flows
            ocf=log(abs(stock[3]))
            ocf=-ocf
        elif stock[3]==0:
            ocf=0
        else:
            ocf=log(abs(stock[3]))
        ranking=marketcap*float(coeff[0][0])+formula.NumberTreatment(stock[2])*coeff[1][0]+distance*coeff[2][0]+ocf*coeff[3][0]+stock[4]*coeff[4][0]+stock[5]*coeff[4][0]+stock[6]*coeff[5][0]    
        cur.execute('UPDATE Stocks_Data SET Score = ? WHERE Symbol=?',[ranking,stock[0]])
        #print(stock[0]+": "+str(ranking))
    con.commit()
    con.close()
    
# now all classes have been defined, just executes the update
con = lite.connect('stock.db')
# first, retrieves articles for short-sellers and promoters
# only for those who have not been done yet in a previous update
cur=con.cursor()
cur.execute('SELECT Url,Type FROM Shortsellers WHERE Done IS NULL')
rows=cur.fetchall()
cur.execute('SELECT Url,Type FROM Promoters WHERE Done IS NULL')
rows2=cur.fetchall()
con.commit()
con.close()
#rows : short-sellers
for row in rows:
    print(row[0])
    articles=Articles()
    articles.RetrieveArticles(row[0],row[1],1)
#rows2 : promoters
for row in rows2:
    print(row[0])
    articles=Articles()
    articles.RetrieveArticles(row[0],row[1],0)
# now update the proximity index
con = lite.connect('stock.db')
cur=con.cursor()
# status variable is changed only when someone adds a new previously targeted company
# in order to win some time at the update, update of proximity index occurs only when status variable has been changed
cur.execute('SELECT Status FROM Updates WHERE Type="Board"')
result=cur.fetchall()
if result[0][0]==1:
    BoardProcessing()
    print('Articles Updated.\nNow processing Board_Network database.\n\n')    
    cur.execute('UPDATE Updates SET Status=0 WHERE Type="Board"')
con.commit()
con.close()
print('Score result processing.')
# now update the score
ScoreUpdate()
print('Magic update done.')