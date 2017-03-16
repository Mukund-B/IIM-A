# -*- coding: utf-8 -*-
"""
Created on Thu Mar 09 22:28:37 2017

@author: Mukund Bharadwaj
"""

import FormDataFrame as FD
import StocksGraph as SG
import DataMining as DM
import SentimentAnalysis as SA
import os

def main():
    home_dir = "M:/Documents/IIM-A Hackathon/"
    os.chdir(home_dir)
    files = os.listdir(os.curdir)
    folders = ['DATA','StockData']
    for folder in folders:
        if folder not in files:
            print "You do not have the required files! Please ensure all the files are present"
            return
    try:
        os.mkdir('Annual Data')
    except:
        pass
    print '\nGenerating Mean Stock Prices and identify trends'
    SG.genStock()
    print '\nGetting Financial Data from www.moneycontrol.com'
    ID = DM.getID('DATA/')
    DM.mine(ID)
    print '\nGetting Sentiment Scores'
    SA.genFLS()
    print '\nGetting Sector data and Company Name'
    DM.getInfo(ID)
    print '\nGenerate Final Data Frame for Prediction'
    FD.genFrame(ID)
    print '\nDone! Open up Processing.R to predict stock prices'
main()