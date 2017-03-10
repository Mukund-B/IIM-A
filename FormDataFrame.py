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
    co_names = pd.DataFrame(dt.items(),columns=["Company","ID"])
    co_names['ID'] = co_names['ID'].astype(int)
    
    #Adding Sector Details
    sectors = pd.read_csv('Sector.csv',index_col = 0)
    del sectors['Company']
    sectors['Sector'] = sectors['Sector 1']
    del sectors['Sector 1']
    sectors = sectors.dropna()
    sectors['Sector'] = map(lambda x: x.strip(),sectors['Sector'])
    sectors['ID'] = sectors['ID'].astype(int)
    
    #Adding Sentiment Scores
    sentiment = pd.read_csv('Sentiment Scores.csv',index_col=0)
    sentiment['ID'] = sentiment['ID'].astype(int)
    result = ( 
            co_names.merge(result,how = "right",on="ID")
            .merge(stocks,how = "left",on="ID")
            .merge(sectors,how = "left",on="ID")
            .merge(sentiment,how="left",on="ID")
            )
    return result
        
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
def genFrame():
    ID = getID('DATA/')
    columns = labelsPL.keys() + labelsBS.keys() + ['X1', 'X2', 'X3', 'X4', 'X5', 'z-score', 'ROA', 'ROE']
    path = "Annual Data"
    res = formDataFrame(path, columns, ID, 2011, 2015)
    res.to_csv("final_df.csv", index = False)
genFrame()