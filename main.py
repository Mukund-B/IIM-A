# -*- coding: utf-8 -*-
"""
Created on Thu Mar 09 22:28:37 2017

@author: Mukund Bharadwaj
"""

import FormDataFrame as FD
import StocksGraph as SG
import DataMining as DM
import NewsDiscovery as ND
import SentimentAnalysis as SA
import os

def main(FLS=False):
    home_dir = "M:/Documents/IIM-A Hackathon/"
    os.chdir(home_dir)
    files = os.listdir(os.curdir)
    folders = ['DATA','StockData']
    for folder in folders:
        if folder not in files:
            print "You do not have the required files! Please ensure all the files are present"
            return
    os.mkdir('Annual Data')
    print '\nGenerating Mean Stock Prices and identify trends'
    SG.genStock()
    print '\nGetting Financial Data from www.moneycontrol.com'
    ID = DM.getID('DATA/')
    DM.mine(ID)
    print '\nGetting Sentiment Scores using IBM Watson - Discovery API'
    ND.genSentiment(ID)
    print '\nGenerate Final Data Frame for Prediction'
    FD.genFrame()
    if FLS:
        print '\nGenerating Forward Looking Sentences. This will take a while...'
        SA.genFLS()
    print '\nDone! Open up Processing.R to predict stock prices'
main()