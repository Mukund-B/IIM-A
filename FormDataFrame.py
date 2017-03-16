# -*- coding: utf-8 -*-
"""
Created on Thu Mar 09 16:07:52 2017

@author: HP
"""

import os
import pandas as pd
import numpy as np

def formColumnList(col_list, start, end):
    res = []
    col_list = [col.replace(" ", "_").replace("/", "_") for col in col_list]
        
    for i in range(end, start - 1, -1):
        for col in col_list:    
            res.append(col + "_" + str(i))
    
    return res

def formDataFrame(path, columns, dt, start, end):
    os.chdir(path)
    
    col_list = formColumnList(columns, start, end)
    col_list = ['ID'] + col_list
    temp = list()
    
    for file in os.listdir(os.curdir):
        
        df = pd.read_csv(file)
        df['z-score'] = map(lambda x: 0 if x<1.23 else 1 if x<2.9 else 2,df['z-score'])
        d = df[df.columns[1:]].values.flatten()
#        for i in d:
#            i = remove_comma(i)
        d = np.append(file[:-4], d)
        temp.append(d)
        print "\nFinished file: " + file
    
    os.chdir('..')
    
    result = pd.DataFrame(data = temp, columns = col_list,dtype=object)
    result['ID'] = result['ID'].astype(int)
    
    #Adding Stock Data
    stocks = pd.read_csv('StockPrices.csv',index_col=0)
    
    #Adding Company Names
    co_names = pd.DataFrame(dt.items(),columns=["NSE ID","ID"])
    co_names['ID'] = co_names['ID'].astype(int)
    
    #Adding Sector Details
    sectors = pd.read_csv('Sector.csv',index_col = 0)
    sectors = sectors.dropna()
    sectors['ID'] = sectors['ID'].astype(int)
    
    #Adding Sentiment Scores
    sentiment = pd.read_csv('Sentiment.csv',index_col=0)
    sentiment['ID'] = sentiment['ID'].astype(int)
    sentiment['Basic'] = ''
    sentiment.loc[sentiment['Basic Sentiment'] > 0,'Basic'] = 'Positive'
    sentiment.loc[sentiment['Basic Sentiment'] < 0,'Basic'] = 'Negative'
    sentiment.loc[sentiment['Basic Sentiment'] == 0,'Basic'] = 'Neutral'

    sentiment['Vader'] = ''
    sentiment.loc[sentiment['Vader Sentiment'] > 0,'Vader'] = 'Positive'
    sentiment.loc[sentiment['Vader Sentiment'] < 0,'Vader'] = 'Negative'
    sentiment.loc[sentiment['Vader Sentiment'] == 0.0,'Vader'] = 'Neutral'
    
    uniq = set(sentiment['ID'])
    columns = ['ID','Sent_2010','Sent_2011','Sent_2012','Sent_2013',
               'Sent_2014','Sent_2015','Vader_2010','Vader_2011'
               ,'Vader_2012','Vader_2013','Vader_2014','Vader_2015']
    sents = pd.DataFrame(index=range(0,len(uniq)),columns=columns)
    count = 0
    for ID in uniq:
        temp = sentiment[sentiment['ID']==ID]
        numRow = len(temp.index)
        sents.iloc[count]['ID'] = ID
        for i in range(numRow):
            t = temp.iloc[i]
            if t['Year']==2010:
                sents.iloc[count]['Sent_2010'] = t['Basic']
                sents.iloc[count]['Vader_2010'] = t['Vader']
            elif t['Year']==2011:
                sents.iloc[count]['Sent_2011'] = t['Basic']
                sents.iloc[count]['Vader_2011'] = t['Vader']
            elif t['Year']==2012:
                sents.iloc[count]['Sent_2012'] = t['Basic']
                sents.iloc[count]['Vader_2012'] = t['Vader']
            elif t['Year']==2013:
                sents.iloc[count]['Sent_2013'] = t['Basic']
                sents.iloc[count]['Vader_2013'] = t['Vader']
            elif t['Year']==2014:
                sents.iloc[count]['Sent_2014'] = t['Basic']
                sents.iloc[count]['Vader_2014'] = t['Vader']
            elif t['Year']==2015:
                sents.iloc[count]['Sent_2015'] = t['Basic']
                sents.iloc[count]['Vader_2015'] = t['Vader']
            else:
                continue
        count += 1
    result = (
            co_names.merge(result,how = "right",on="ID")
            .merge(stocks,how = "left",on="ID")
            .merge(sectors,how = "left",on="ID")
            .merge(sents,how="left",on="ID")
            )
    
    sector = set(result['Sector'])
    total = result.sum()
    
    result.loc[:,'Total_Revenue_2011'] = result['Total_Revenue_2011'].astype(float)
    result.loc[:,'Total_Revenue_2012'] = result['Total_Revenue_2012'].astype(float)
    result.loc[:,'Total_Revenue_2013'] = result['Total_Revenue_2013'].astype(float)
    result.loc[:,'Total_Revenue_2014'] = result['Total_Revenue_2014'].astype(float)
    result.loc[:,'Total_Revenue_2015'] = result['Total_Revenue_2015'].astype(float)
    
    data = list()
    for sect in sector:
        temp = result[result['Sector']==sect]
        total = temp.sum()
        temp.loc[:,'Share_2011'] = temp['Total_Revenue_2011']/total['Total_Revenue_2011']
        temp.loc[:,'Share_2012'] = temp['Total_Revenue_2012']/total['Total_Revenue_2012']
        temp.loc[:,'Share_2013'] = temp['Total_Revenue_2013']/total['Total_Revenue_2013']
        temp.loc[:,'Share_2014'] = temp['Total_Revenue_2014']/total['Total_Revenue_2014']
        temp.loc[:,'Share_2015'] = temp['Total_Revenue_2015']/total['Total_Revenue_2015']
        data.append(temp)
    share = pd.concat(data)
    return share
        
def remove_comma(string):
    if type(string) != float and type(string) != np.float64:
        return float(string.replace(",", ""))
    return string

def getID(dir):
    r = dict()
    for f in os.listdir(dir):
        try:
            r[f]=os.listdir(dir+f)[0][:6]
        except:
            continue
    return r

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
def genFrame(ID):
    columns = labelsPL.keys() + labelsBS.keys() + ['X1', 'X2', 'X3', 'X4', 'X5', 'z-score', 'ROA', 'ROE']
    path = "Annual Data"
    res = formDataFrame(path, columns, ID, 2011, 2015)
    res.to_csv("final_df.csv", index = False)