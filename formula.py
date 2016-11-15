# -*- coding: utf-8 -*-
"""
Created on Tue Jan  5 07:20:55 2016

@author: théo
"""
from lxml import html
import requests
import sqlite3 as lite
class Formula:
    def NumberTreatment(self,number):
        # transforms a Yahoo figure like "1.2Bn" into numeric 120000000
        number=number.replace(",","")
        number=str(number)
        if number == "N/A":
            return 0
        else:
            final=number[-1:]
            numb=float(number[:-1])
            if final == "K":
                n=numb*1000
            elif final == "M":
                n=numb*1000000
            elif final == "B":
                n=numb*1000000000
            elif final == "%":
                n=numb
            else:
                n=float(number)
            return n
    def Calculate(self):
        con = lite.connect('stock.db')
        cur=con.cursor()        
        cur.execute('SELECT Coefficient FROM Formula')
        coeff=cur.fetchall()