# -*- coding: utf-8 -*-
"""
Created on Wed Mar 08 21:09:51 2017

@author: Mukund Bharadwaj
"""
from bs4 import BeautifulSoup
import requests
import os
import pandas as pd

def getBaseURL(company):
    base="http://www.moneycontrol.com/stocks/cptmarket/compsearchnew.php?search_data=&cid=&mbsearch_str=&topsearch_type=1&search_str="
    try:
        r = requests.get(base+company.replace('&','%26'))
        r.raise_for_status()
    except:
        print "Cannot find link"
        return
    soup = BeautifulSoup(r.text, 'html.parser')
    table = soup.find('table',attrs={'class':'srch_tbl'})
    try:
        rows = table.find_all('tr')
    except:
        if 'compsearchnew.php' in r.url:
            return None
        return r.url
    for row in rows:
        details = row.find_all('td')
        span = details[1].find_all('span')
        for s in span:
            if s.find('strong').text=="NSE Id":
                if s.text.split(':')[1].replace(';','')==company:
                    link = details[0].find('a').get('href')
                    return link
    return None
def getBS(URL):
    
    try:
        r = requests.get(URL)
        r.raise_for_status()
    except:
        print "Cannot find link"
        return
    soup = BeautifulSoup(r.text, 'html.parser')
    tab = soup.find_all('dt')
    for row in tab:
        if row.text=='FINANCIALS':
            link = row.find('a').get('href')
            return "http://www.moneycontrol.com"+link
def getPL(URL):
    bs=getBS(URL)
    if bs == None:
        return None
    return bs.replace('balance-sheet','profit-loss')

def getTitle(URL):
    try:
        r = requests.get(URL)
        r.raise_for_status()
    except:
        print "Cannot find link"
        return
    soup = BeautifulSoup(r.text, 'html.parser')
    title = soup.find('h1',attrs={'class':'b_42'})
    return title.text

def getID(dir):
    r = dict()
    for f in os.listdir(dir):
        try:
            r[f]=os.listdir(dir+f)[0][:6]
        except:
            continue
    return r

def getTable(html,labels):
    
    def getDenom(tb):
        for line in tb.findAll('tr'):
            d = line.getText().lower()
            if "crore" in d or "cr" in d:
                return 1E7
            if "lakh" in d:
                return 1E5
            
    soup = BeautifulSoup(html,'html.parser')
    table = soup.findAll("table", attrs={"class":"table4"})
    denom = getDenom(table[-2])
    table = table[-1]
    for line in table.findAll('tr'):
        lt = []
        t = line.find('td').getText()
        if t in labels.keys():
            for l in line.findAll('td')[1:]:
                lt.append(float(l.getText().replace(',',''))*denom)
            labels[t] = lt
    for key in labels.keys():
        if labels[key]==None:
            labels[key] = [0.0]*5
        else:
            while len(labels[key])<5:
                labels[key].append(None)
    
    return labels

def calcRatios(data):
    """
    Arguments:
        data - Pandas Data Frame
    
    Returns:
        A Pandas Data Frame where:
        X1 = (Current Assets − Current Liabilities) / Total Assets
    
        X2 = Retained Earnings / Total Assets
        
        X3 = Earnings Before Interest and Taxes / Total Assets
        
        X4 = Book Value of Equity / Total Liabilities
        
        X5 = Sales / Total Assets
    """
    data['X1'] = (data['Total Current Assets']-data['Total Current Liabilities'])/data['Total Assets']
    data['X2'] = (data['Profit/Loss For The Period']-data['Equity Share Dividend']-data['Tax On Dividend'])/data['Total Assets']    
    data['X3'] = data['Profit/Loss Before Tax']/data['Total Assets']
    data['X4'] = data['Equity Share Capital']/(data['Total Current Liabilities']+data['Total Non-Current Liabilities'])
    data['X5'] = data['Total Revenue']/data['Total Assets']
    data['z-score'] = 0.717*data['X1'] + 0.847*data['X2'] + 3.107*data['X3'] + 0.420*data['X4'] + 0.998*data['X5']
    data['ROA'] = data['Profit/Loss For The Period']/data['Total Assets']
    data['ROE'] = data['Profit/Loss For The Period']/data['Equity Share Capital']
    return data


labelsPL = {'Total Revenue':None,
            'Profit/Loss Before Tax':None,
            'Profit/Loss For The Period':None,
            'Equity Share Dividend':None,
            'Tax On Dividend':None}
labelsBS = {'Equity Share Capital':None,
            'Total Current Assets':None,
            'Total Current Liabilities':None,
            'Total Non-Current Liabilities':None,
            'Total Assets':None}

def getNews(ID):
    keys = ID.keys()
    years = range(2010,2016)
    data = []
    for key in keys:
        print key
        lt = []
        if len(key)<3:
           continue
        url = getBaseURL(key)
        title = getTitle(url)
        print title
        if title==None:
            continue
        for year in years:
            tBegin = '1%2F1%2F'+str(year)
            tEnd = '12%2F31%2F'+str(year)
            url = """https://www.google.co.in/search?
            q={}&hl=en&gl=in&authuser=0&biw=1366&bih=633&source=lnt&
            tbs=cdr%3A1%2Ccd_min%3A{}%2Ccd_max%3A{}&
            tbm=nws""".format(title.replace(' ','+'),tBegin,tEnd)
            page = requests.get(url)
            
            lt.append()


def mine(ID):
    keys = ID.keys()
    print "Starting Financial Data Mining"
    os.chdir('Annual Data')
    print "Companies:"
    for key in keys:
        print key
        if len(key)<3:
            continue
        b = getBaseURL(key)
        final = getPL(b)
        if final==None:
            continue
        PL = getTable(requests.get(final).text,labelsPL)
        final = getBS(b)
        BS = getTable(requests.get(final).text,labelsBS)
        years = range(2015,2010,-1)
        PL.update(BS)    
        data = pd.DataFrame(PL,index = years)
        data = calcRatios(data)
        data.to_csv(ID[key]+'.csv')
    print "Done"
    os.chdir('..')