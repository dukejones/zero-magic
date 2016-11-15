#!/usr/bin/env python3
# -*- coding: iso-8859-1 -*-
# file controlling the graphic interface of the software
import tkinter as tk
import tkinter.messagebox as messagebox
import tkinter.scrolledtext as tkst
import sqlite3 as lite
from subprocess import Popen
import formula as formule
import shutil
import httplib2
class General:
    def __init__(self, master):
        # main window of the graphic interface
        self.master = master
        self.master.geometry("{}x{}".format(550,650))
        # content of the main window
        self.welcome = tk.Label(self.master, text = 'Welcome to Zero Magic!\nFollow these 5 steps to enjoy the magic of short selling*\n\nPLEASE NOTE THAT THIS SOFTWARE IS STILL IN EARLY TESTING')        
        self.ins = tk.Button(self.master, text = '1. Manage Data', width = 250, command = self.add_button)
        self.insl = tk.Label(self.master, wraplength=250, padx=0, justify = "left", text = "1. To increase the accuracy of its trading advice, Zero Magic requires that you input certain data. Under 'Manage Data' you can provide links to known stock promoters and short-sellers. You can also provide the names of stocks that were previously successful shorts.", width=250)        
        self.form = tk.Button(self.master, text = '2. Modify Formula', width = 250, command = self.formula_button)
        self.forml = tk.Label(self.master, wraplength=255, padx=0, justify = "left", text = '2. Zero Magic provides a default formula for determining which stocks are most vulnerable to perception changes. However, as you gain trading experience you might want to modify the weighting of the coefficients in this formula to provide more accurate results.', width=250)        
        self.upd = tk.Button(self.master, text = '3. Update Ranking', width = 250, command = self.update_button)
        self.updl = tk.Label(self.master, wraplength=261, padx=0, justify = "left", text = '3. Once you have inserted the required data and checked the formula, Zero Magic will update its target company rating. Please be patient, this may take a few minutes.', width=250)        
        self.disp = tk.Button(self.master, text = '4. Display Results', width = 250, command = self.display_button)
        self.displ = tk.Label(self.master, wraplength=256, padx=0, justify = "left", text = '4. Once the ranking is updated you can display the results. Zero Magic will present a list of 5 stocks most vulnerable to perception change, and therefore suitable as short selling targets.', width=250)        
        self.act = tk.Button(self.master, text = '5. Perform Zero Magic', width = 250, command = self.perform_button)
        self.actl = tk.Label(self.master, wraplength=260, justify = "left", text = '5. Time to go short. For the first top short selling target, Zero Magic will provide you with key data and references that can help undermine the current valuation of this target company. Making targeted stocks fall, will make your short profitable and your magic trick successful.', width=250)        
        self.reset = tk.Button(self.master, text = 'Reset Data', width = 250, command = self.reset_button)
        self.resetl = tk.Label(self.master, wraplength=260, justify = "left", text = '[X] Something went wrong? The ranking update does not work? Reset the database.', width=250)        
        self.welcome.grid(row=0,column=0,columnspan=2, pady=20)
        self.discl = tk.Label(self.master, wraplength=500, justify = "center", font="Arial 8", text='\n*Individuals must not rely on the information provided by Zero Magic software to make a financial or investment decision. Before making any decision, we recommend you consult a financial planner to take into account your particular investment objectives, financial situation and individual needs.',width=500)
        # grids and table of the main window        
        self.ins.grid(row=1,column=1)
        self.insl.grid(row=1,column=0, padx=0)
        self.form.grid(row=2,column=1)
        self.forml.grid(row=2,column=0, padx=0)
        self.upd.grid(row=3,column=1)
        self.updl.grid(row=3,column=0, padx=0)
        self.disp.grid(row=4,column=1)
        self.displ.grid(row=4,column=0, padx=0)
        self.act.grid(row=5,column=1)
        self.actl.grid(row=5,column=0, padx=0)
        self.reset.grid(row=6,column=1)
        self.resetl.grid(row=6,column=0, padx=0)
        self.discl.grid(row=7,column=0, padx=0,columnspan=2)
        self.master.grid_columnconfigure(index=1, weight=1)
        self.master.grid_columnconfigure(index=0, weight=1)
    def display_button(self):
        self.newWindow = tk.Toplevel(self.master)
        self.app = Display(self.newWindow)
    def perform_button(self):
        self.newWindow = tk.Toplevel(self.master)
        self.app = Perform(self.newWindow)
    def reset_button(self):
        self.newWindow = tk.Toplevel(self.master)
        self.app = Reset(self.newWindow)
    def add_button(self):
        self.newWindow = tk.Toplevel(self.master)
        self.app = Add(self.newWindow)
    def formula_button(self):
        self.newWindow = tk.Toplevel(self.master)
        self.app = Formula(self.newWindow)
    def update_button(self):
        self.newWindow = tk.Toplevel(self.master)
        self.app = Update(self.newWindow)

class Display:
    def __init__(self, master):
        # Display Results window
        self.master = master
        self.frame = tk.Frame(self.master)
        self.txt = tkst.ScrolledText(self.frame, undo=True, wrap=tk.WORD)
        self.txt['font'] = ('consolas', '12')
        self.txt.pack(expand=True, fill='both')
        # select the 5 first results ordered by overall score
        con = lite.connect('stock.db')
        cur=con.cursor()        
        cur.execute('SELECT Symbol,Score FROM Stocks_Data WHERE Proximity!=0 AND Score IS NOT NULL ORDER BY Score DESC LIMIT 0, 5')
        best=cur.fetchall()
        cur.execute('SELECT Name,Coefficient FROM Formula')
        formula=cur.fetchall()
        con.close()
        # variable content is filled with the result to display to the user
        content="Zero Magic Results\n\nFormula\nScore = \n"
        for coefficients in formula:
            content+="("+str(coefficients[1])+") * "+str(coefficients[0])+" + \n"
        content=content[:-4]+" +\n1000 (constant)"
        content+="\n\n\nFive Best Stocks To Short (Symbol | Score):\n"
        for stock in best:
            content+=stock[0]+" | "+str(round(stock[1],1)+1000)+"\n"
        # put variable content in the scrolledtext frame
        self.txt.insert(tk.INSERT,content)
        self.quitButton = tk.Button(self.frame, text = 'Quit', width = 25, command = self.close_windows)
        self.quitButton.pack()
        self.frame.pack()
    def close_windows(self):
        self.master.destroy()

class Perform:
    def __init__(self, master):
        # Perform the Short window
        self.master = master
        self.frame = tk.Frame(self.master)
        self.txt = tkst.ScrolledText(self.frame, undo=False, wrap=tk.WORD)
        self.txt['font'] = ('consolas', '12')
        self.txt.pack(expand=True, fill='both')
        # select all relevant information regarding the best short
        con = lite.connect('stock.db')
        cur=con.cursor()        
        cur.execute('SELECT Symbol,Score,MarketCap,OCF,ShortRatio,Proximity,ShortPublic,PromotersPublic,FiftyWeekHigh,DayMA FROM Stocks_Data WHERE Proximity!=0 AND Score IS NOT NULL ORDER BY Score DESC LIMIT 0, 1')
        best=cur.fetchall()
        con.close()
        # try to outline the most powerful arguments against the best short
        # by using simple conditions
        formula = formule.Formula()
        best=best[0]
        distance=100*float(formula.NumberTreatment(best[8])-formula.NumberTreatment(best[9]))/float(formula.NumberTreatment(best[8]))       
        content="Now: Perform Zero Magic!\n\n\n"
        content+=best[0]+" stock is currently the best short according to Zero Magic with a score of "+str(round(best[1],1)+1000)+".\n"
        content+="\nIn short selling, it is not enough to have an accurate analysis of a stock. It requires transforming the perceived value of your target company. To change the market perception of "+best[0]+", follow the steps below:\n\n\n"
        content+="1. First of all, let's look at the fundamentals of the stock:\n\n"
        content+="\n\n- Market Cap: "+str(best[2])
        # condition on market cap
        if formula.NumberTreatment(best[2])<2500000000:
            content+="\n--> nice: it's a quite small company for Nasdaq, no one really cares about it so it's vulnerable to volatility."
        else:
            content+="\n--> well, it's a rather big company: let's find other arguments..."
        content+="\n\n- Operating Cash-Flow: "+str(best[3])
        # condition on operating cash flows
        if formula.NumberTreatment(best[3])<0:
            content+="\n--> fantastic: the company burns cash, let's save this information for later."
        else:
            content+="\n--> oops, the company generates cash; let's find other weaknesses."
        #content+="- Short-ratio: "+str(best[4])+"\n"
        # condition on distance to 1yr high
        content+="\n\n- Distance to 1-Year High: "+str(round(distance,1))+"% below"       
        if distance<25:
            content+="\n--> perfect: we're near to a 1-Year-High, we will argue that the stock is the object of a dangerous bubble."
        else:
            content+="\n--> well, the stock has already fallen this year"           
        content+="\n\n2. Secondly, let’s see if the company is involved in networks of corruption.\n"
        # condition on the network indicator        
        if best[5]<10:
            content+="\n-> It has "+str(best[5])+" degree(s) of separation from previously successful short targets.\n"
            content+="\n-> Have a closer look to the links between "+best[0]+"'s board and the following boards:\n"
            # display the companies linked to the best short            
            con = lite.connect('stock.db')
            cur=con.cursor()        
            cur.execute('SELECT Linked FROM Board_Network WHERE Symbol=?',[best[0]])
            board=cur.fetchall()
            con.close()
            for rows in board:
                content+="\n  - "+rows[0].replace(',',',\n  - ')+".\n"
        else:
            content+="\n-> It has no link with previously successful short targets: no worries, we'll find something else.\n"
        
        # to do : outline the promoters through SEC filings and promotional articles
        #content+="\n\n3. Thirdly, let’s see who is promoting this stock.\n"
        #content+="See URLs:\n"
        #content+=+"\n"
        content+="\n\n4. Now look at how the stock price is currently being discussed. "
        content+="There are/is "+str(best[6])+" short article(s) related to "+best[0]+":\n\n"   
        # description of short arguments        
        if best[6]>0:
            con = lite.connect('stock.db')
            cur=con.cursor()        
            cur.execute('SELECT Title,Url FROM Articles WHERE Stocks=?',[best[0]])
            articles=cur.fetchall()
            con.close()
            for rows in articles:
                content+="-> "+rows[0]+" (http://seekingalpha.com"+rows[1]+")\n"
        content+="\n5. Finally, evaluate if the information provided above is sufficient to tell a newsworthy story of how and why this company is over-valued?\nIf yes, frame your story of how the value of this company was manipulated. Add incriminating details on management and board members which seem especially newsworthy.\n\n-> Send your story anonymously to the following writers/journalists:"
        content+="\n\n  - Adam Feuerstein,"
        content+="\n  - Richard Pearson,"
        content+="\n  - Bleecker Street Research,"
        content+="\n  - Logical Thought."
        content+="\n\nPlease add whatever further writers, journalists or analysts you think could be relevant.\n\nSit back and enjoy the magic."
        # insert everything in the scrolledtext frame        
        self.txt.insert(tk.INSERT,content)
        self.quitButton = tk.Button(self.frame, text = 'Quit', width = 25, command = self.close_windows)
        self.quitButton.pack()
        self.frame.pack()
    def close_windows(self):
        self.master.destroy()
        
class Update:
    def __init__(self, master):
        # launch the update : launch a compiled version of articles.py
        # (articles.py being the program which updates the data, in particular regarding short and promotional articles)
        # to do : replace it with subprocessing or multithreading
        Popen(["articles.exe"], creationflags=CREATE_NEW_CONSOLE, shell=True)
        self.master = master
        self.frame = tk.Frame(self.master)
        self.txt = tkst.ScrolledText(self.frame, undo=True, wrap=tk.WORD)
        # display to the user the estimated time for the update
        con = lite.connect('stock.db')
        cur=con.cursor()
        cur.execute('SELECT Count(*) FROM Shortsellers WHERE Done IS NULL')
        rows=cur.fetchall()
        cur.execute('SELECT Count(*) FROM Promoters WHERE Done IS NULL')
        rows2=cur.fetchall()
        con.commit()
        con.close()
        self.txt['font'] = ('consolas', '12')
        self.txt.pack(expand=True, fill='both')
        self.txt.insert(tk.INSERT,"Update process launched. It will run as a background process.\nTasks to process :\n - "+str(rows[0][0])+" short-seller(s) to scrape\n - "+str(rows2[0][0])+" promoter(s) to scrape\n - proximity index to update\n - ranking scores to update.\n\nEstimated time : "+str((int(rows[0][0])+int(rows2[0][0]))*3+1)+" minute(s).\nYou can quit this window without affecting the updating process.\nHowever, while the update is running the 'Manage Data’ and 'Modify Formula' features will not function correctly.")
        self.quitButton = tk.Button(self.frame, text = 'Quit', width = 25, command = self.close_windows)
        self.quitButton.pack()
        self.frame.pack()
        self.master.lift()

    def close_windows(self):
        self.master.destroy()

class Reset:
    def __init__(self, master):
        # reset the data : replace stock.db by stock_backup.db
        self.master = master
        self.frame = tk.Frame(self.master)
        self.txt = tkst.ScrolledText(self.frame, undo=True, wrap=tk.WORD)
        shutil.copy2("stock_backup.db","stock.db")
        self.txt['font'] = ('consolas', '12')
        self.txt.pack(expand=True, fill='both')
        self.txt.insert(tk.INSERT,"Reset done!")
        self.quitButton = tk.Button(self.frame, text = 'Quit', width = 25, command = self.close_windows)
        self.quitButton.pack()
        self.frame.pack()
        self.master.lift()

    def close_windows(self):
        self.master.destroy()
        
class Add:
    def __init__(self, master):
        # add stock promoters, previously successful shorts or short-sellers
        self.master = master
        self.master.geometry("{}x{}".format(550,270))
        self.promoter = tk.Button(self.master, text = 'Identify known stock promoters', width = 250, command = self.add_promoter)
        self.targeted = tk.Button(self.master, text = 'Identify previously successful shorts', width = 250, command = self.add_targeted)
        self.short = tk.Button(self.master, text = 'Identify known short-sellers', width = 250, command = self.add_shortseller)
        self.promoterl = tk.Label(self.master, wraplength=250, text = '1. Promoted stocks are stocks whose perceived value can be more easily transformed. Identifying known stock promoters helps the software find vulnerable stocks.', width = 250)
        self.shortl = tk.Label(self.master, wraplength=250, text = '2. "A wolf never hunts alone"”. Identifying known short sellers helps the software perceive changes under way.', width = 250)
        self.targetedl = tk.Label(self.master, wraplength=250, text = '3. When a stock is hit by short selling, it carries its likes in the fall. Identifying companies which were the targets of previous successful short selling campaigns allows the software to perform a network analysis.', width = 250)
        self.promoter.grid(row=0,column=1)
        self.promoterl.grid(row=0,column=0)
        self.shortl.grid(row=1,column=0)
        self.short.grid(row=1,column=1)
        self.targetedl.grid(row=2,column=0)
        self.targeted.grid(row=2,column=1)
        self.master.grid_columnconfigure(index=1, weight=1)
        self.master.grid_columnconfigure(index=0, weight=1)
    def add_shortseller(self):
        # if the user wants to add a short-seller: input
        self.newWindow = tk.Toplevel(self.master)
        self.entryVariable=tk.StringVar()
        self.entry = tk.Entry(self.newWindow, textvariable=self.entryVariable)
        self.entryVariable.set("")
        self.list=tk.IntVar()
        self.listbox = tk.Radiobutton(self.newWindow, text="SeekingAlpha", variable=self.list, value=0)
        self.listbox1 = tk.Radiobutton(self.newWindow, text="(Coming Soon)", variable=self.list, value=1)        
        self.newLabel = tk.Label(self.newWindow, text="Affiliation")
        self.newLabel2 = tk.Label(self.newWindow, text="Author's URL")
        self.formatting = tk.Label(self.newWindow, text="Author's URL Formatting: http://seekingalpha.com/author/author-id/articles")
        self.validateButton = tk.Button(self.newWindow,text=u"Add Shortseller",command=self.ShortClick)
        self.validateButton.grid(column=0,row=3)
        self.formatting.grid(column=0,row=2, columnspan=3)
        self.entry.grid(column=1,row=1)
        self.listbox.grid(column=1,row=0)
        self.listbox1.grid(column=2,row=0)
        self.newLabel.grid(column=0,row=0)
        self.newLabel2.grid(column=0,row=1)
    def add_promoter(self):
        # input for promoters
        self.newWindow = tk.Toplevel(self.master)
        self.entryVariable=tk.StringVar()
        self.entry = tk.Entry(self.newWindow, textvariable=self.entryVariable)
        self.entryVariable.set("")
        self.list=tk.IntVar()
        self.listbox = tk.Radiobutton(self.newWindow, text="SeekingAlpha", variable=self.list, value=0)
        self.listbox1 = tk.Radiobutton(self.newWindow, text="(Coming Soon)", variable=self.list, value=1)        
        self.newLabel = tk.Label(self.newWindow, text="Affiliation")
        self.newLabel2 = tk.Label(self.newWindow, text="Author's URL")
        self.formatting = tk.Label(self.newWindow, text="Author's URL Formatting: http://seekingalpha.com/author/author-id/articles")
        self.validateButton = tk.Button(self.newWindow,text=u"Add Promoter",command=self.PromoterClick)
        self.validateButton.grid(column=0,row=3)
        self.formatting.grid(column=0,row=2, columnspan=3)
        self.entry.grid(column=1,row=1)
        self.listbox.grid(column=1,row=0)
        self.listbox1.grid(column=2,row=0)
        self.newLabel.grid(column=0,row=0)
        self.newLabel2.grid(column=0,row=1)
    def add_targeted(self):
        # input for targeted companies
        self.newWindow = tk.Toplevel(self.master)
        self.entryVariable=tk.StringVar()
        self.entry = tk.Entry(self.newWindow, textvariable=self.entryVariable)
        self.newLabel = tk.Label(self.newWindow, text="4-Letters Stock Code")
        self.entryVariable.set("")
        self.validateButton = tk.Button(self.newWindow,text=u"Add Targeted Stock",command=self.TargetedClick)
        self.validateButton.grid(column=0,row=1)
        self.newLabel.grid(column=0,row=0)
        self.entry.grid(column=1,row=0)
    def TargetedClick(self):
        # insert into the DB a previously targeted company (controls the existence of the company)
        con = lite.connect('stock.db')
        cur=con.cursor()
        cur.execute('SELECT Count() FROM Stocks_Data WHERE Symbol=?',[self.entryVariable.get()])
        number=cur.fetchall()[0][0]       
        if number==1:
            cur.execute('INSERT INTO Targeted (Code) VALUES (?)',[self.entryVariable.get()])
            cur.execute('UPDATE Board_Network SET IndexP=0 WHERE Symbol=?',[self.entryVariable.get()])          
            cur.execute('UPDATE Updates SET Status=1 WHERE Type="Board"')
        else:
            messagebox.showerror("Stockname Error", "Invalid Stock Code. Please type a Nasdaq code (e.g. GALT, ALNY, KERX)")
        con.commit()
        con.close()
        self.newWindow.destroy()
    def PromoterClick(self):
        # insert into the DB a promoters' DB to be updated then with articles.exe program
        # (controls the existence of the webpage)
        page = httplib2.Http()
        try:
            resp=int(page.request(self.entryVariable.get(),'HEAD')[0]['status'])
        except:
            messagebox.showerror("URL Error","Zero Magic could not retrieve the URL. Please type a real author URL (e.g. http://seekingalpha.com/author/author-id/articles) or check your connection.")
        else:
            if resp==200:
                con = lite.connect('stock.db')
                cur=con.cursor()
                cur.execute('INSERT INTO Promoters (Url,Type) VALUES (?,?)',[self.entryVariable.get(),self.list.get()])
                con.commit()
                con.close()
                self.newWindow.destroy()
            else:
                messagebox.showerror("URL Error","Zero Magic could not retrieve the URL. Please type a real author URL (e.g. http://seekingalpha.com/author/author-id/articles) or check your connection.")
    def ShortClick(self):
        #same as PromotersClick
        page = httplib2.Http()
        try:
            resp=int(page.request(self.entryVariable.get(),'HEAD')[0]['status'])
        except:
            messagebox.showerror("URL Error","Zero Magic could not retrieve the URL. Please type a real author URL (e.g. http://seekingalpha.com/author/author-id/articles) or check your connection.")
        else:
            if resp==200:
                con = lite.connect('stock.db')
                cur=con.cursor()
                cur.execute('INSERT INTO Shortsellers (Url,Type) VALUES (?,?)',[self.entryVariable.get(),self.list.get()])
                con.commit()
                con.close()
                self.newWindow.destroy()
            else:
                messagebox.showerror("URL Error","Zero Magic could not retrieve the URL. Please type a real author URL (e.g. http://seekingalpha.com/author/author-id/articles) or check your connection.")
class Formula:
    def __init__(self, master):
        # display and modifies the formula
        self.master = master
        self.entries=[]
        self.labels=[]
        con = lite.connect('stock.db')
        cur=con.cursor()
        cur.execute('SELECT * FROM Formula')
        rows=cur.fetchall()
        a=0
        # formula is defined in the DB with a set of 2-column rows
        # 1st column: factor name; 2nd column: factor coefficient
        for row in rows:
            self.entryVariable=tk.StringVar()
            self.entry = tk.Entry(self.master, textvariable=self.entryVariable)
            self.entry.grid(row=a+1,column=1)
            self.entryVariable.set(str(float(row[2])))
            self.entries.append(self.entry)
            self.label=tk.Label(self.master,text=str(row[1]))
            self.label.grid(row=a+1,column=0)
            self.labels.append(self.label)
            a=a+1
        self.validateButton = tk.Button(self.master,text=u"Modify Formula",command=self.OnButtonClick)
        self.validateButton.grid(row=a+1, column=0)
        con.commit()
        con.close()
    def OnButtonClick(self):
        con = lite.connect('stock.db')
        cur=con.cursor()
        a=0
        for i in self.entries:
            cur.execute('UPDATE Formula SET Coefficient = ? WHERE id = ?',[i.get(),a])
            a=a+1
        con.commit()
        con.close()
        self.master.destroy()

def main(): 
    root = tk.Tk()    
    #root.iconbitmap(default='transparent.ico')
    app = General(root)
    root.title("ZERO MAGIC (v0.3)")
    root.mainloop()

if __name__ == '__main__':
    main()