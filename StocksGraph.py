# -*- coding: utf-8 -*-
"""
Created on Sat Feb 25 23:51:10 2017

@author: Simran
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import argrelextrema
import csv
import os
from sklearn import linear_model

directory = "StockData"
trends = []

def getPeakTroughIndices(roll_mean):
    peaks = np.array(argrelextrema(roll_mean,np.greater,order=30))
    troughs = np.array(argrelextrema(roll_mean,np.less,order=30))
    return peaks[0],troughs[0]
    
def getMonthlyRollingMean(stock_data):
    stock_data = stock_data.sort_index(ascending=False).reset_index(drop=True)
    roll_mean = np.array(stock_data['Close Price'].rolling(window=30).mean())
    return stock_data,roll_mean

def plotStockGraph(date,roll_mean,peaks,troughs):
    plt.xticks(peaks,date[peaks],rotation=90)
    plt.scatter(peaks,roll_mean[peaks],color='blue')
    plt.scatter(troughs,roll_mean[troughs],color='red')
    plt.plot(range(0,len(roll_mean)),roll_mean)
    plt.xlabel("2010-2015")
    plt.ylabel("Moving month average")
    plt.title("Stock Close Price")
    plt.show()
    plt.close()
    
def upTrendAnalysis(date,roll_mean,peaks,troughs,trends):
    p_high = t_high = 0
    p = t = 0
    period = False
    start = end = 0
    for i,j in zip(peaks,troughs):
        p_high = p
        t_high = t
        p = roll_mean[i]
        t = roll_mean[j]
        if(p>p_high and t>t_high):
            if(not period):
                start = min(i,j)
                period = True
            end = max(i,j)
        else:
            if(period):
                trends.append([date[start],date[end],"UP"])
            period = False
    return trends

def downTrendAnalysis(date,roll_mean,peaks,troughs,trends):
    p_low = t_low = 0
    p = t = 0
    period = False
    start = end = 0
    for i,j in zip(peaks,troughs):
        p_low = p
        t_low = t
        p = roll_mean[i]
        t = roll_mean[j]
        if(p<p_low and t<t_low):
            if(not period):
                start = min(i,j)
                period = True
            end = max(i,j)
        else:
            if(period):
                trends.append([date[start],date[end],"DOWN"])
            period = False
    return trends

def saveTrends(file,trends):
    with open("Trends/"+file, 'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(["FROM","TO","TREND"])
        csvwriter.writerows(trends)
        csvfile.close()


def doForAllFiles(directory,trends):
    os.chdir(directory)
    for file in os.listdir():
        if file.endswith(".csv"): 
            data,roll_mean = getMonthlyRollingMean(file)
            date = data['Date']
            peaks,troughs = getPeakTroughIndices(roll_mean)
#            plotStockGraph(date,roll_mean,peaks,troughs)
            trends = upTrendAnalysis(date,roll_mean,peaks,troughs,trends)
            trends = downTrendAnalysis(date,roll_mean,peaks,troughs,trends)
            saveTrends(file,trends)

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
#    df = data[data['Year']==2010]
#    regr = linear_model.LinearRegression()
#    regr.fit(df['Close Price'].values.reshape(-1, 1),range(len(df['Close Price'])))
#    print regr.coef_
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
genStock()