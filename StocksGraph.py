# -*- coding: utf-8 -*-
"""
Created on Sat Feb 25 23:51:10 2017

@author: Simran
"""

import pandas as pd
import numpy as np
import os
from sklearn import linear_model

directory = "StockData"
trends = []

    
def getMonthlyRollingMean(stock_data):
    stock_data = stock_data.sort_index(ascending=False).reset_index(drop=True)
    roll_mean = np.array(stock_data['Close Price'].rolling(window=30).mean())
    return stock_data,roll_mean

def getPrice(data):
    data['Date'] = pd.to_datetime(data['Date'],format = "%d-%B-%Y")
    data['Year'] = pd.DatetimeIndex(data['Date']).year
    lt = list()
    for y in range(2010,2016):
        df = data[data['Year']==y]
        t,roll = getMonthlyRollingMean(df)
        lt.append(roll[np.isfinite(roll)].mean())
    return lt

def getTrend(data):
    data['Date'] = pd.to_datetime(data['Date'],format = "%d-%B-%Y")
    data['Year'] = pd.DatetimeIndex(data['Date']).year
    lt = list()
    for y in range(2010,2016):
        df = data[data['Year']==y]
        if len(df)==0:
            lt.append(None)
            continue
        regr = linear_model.LinearRegression()
        regr.fit(df['Close Price'].values.reshape(-1, 1),range(len(df['Close Price'])))
        lt.append('UP' if regr.coef_[0]>0 else 'DOWN')
    return lt
    

def genStock():
    os.chdir('StockData')
    
    print("Analysing...")
    stock_data = pd.read_csv('500002.csv')
    getTrend(stock_data)
    prices = dict()
    for file in os.listdir(os.curdir):
        stock_data = pd.read_csv(file)
        prices[file[:-4]] = getPrice(stock_data) + getTrend(stock_data)
    years = ['Stock_2015','Stock_2014','Stock_2013','Stock_2012','Stock_2011','Stock_2010',
             'Trend_2015','Trend_2014','Trend_2013','Trend_2012','Trend_2011','Trend_2010']
    data = pd.DataFrame.from_dict(prices,orient = 'index')
    data.columns = years
    data['ID'] = data.index
    data.index = range(len(data['ID']))
    data.to_csv('../StockPrices.csv')
    
    print("Done!")
    
    os.chdir('..')