# -*- coding: utf-8 -*-
"""
Created on Fri Mar 10 16:59:06 2017

@author: Mukund Bharadwaj
"""

from watson_developer_cloud import DiscoveryV1
import pandas as pd
import DataMining as DM
import time
import calendar

def getSentiment(company,tBegin,tEnd,username,password,version):
    
    discovery = DiscoveryV1(
      username = username,
      password = password,
      version = version
    )
    
    environments = discovery.get_environments()
    
    news_environments = [x for x in environments['environments'] if x['name'] == 'Watson News Environment']
    news_environment_id = news_environments[0]['environment_id']
    
    collections = discovery.list_collections(news_environment_id)
    news_collections = [x for x in collections['collections']]
    news_collection_id = news_collections[0]['collection_id']
    qopts={
      "count": 5,
      "return": "aggregations.enriched_text.concepts.text",
      "query": "\"{}\",language:english".format(company),
      "aggregation": [
        "term(blekko.basedomain).term(docSentiment.type)",
        "term(docSentiment.type)",
        "min(docSentiment.score)",
        "max(docSentiment.score)",
        "filter(enrichedTitle.entities.type::Company).term(enrichedTitle.entities.text).timeslice(blekko.chrondate,1day).term(docSentiment.type)"
      ],
      "filter": "blekko.hostrank>20,blekko.chrondate>{},blekko.chrondate<{}".format(tBegin,tEnd)
    }
    
    my_query = discovery.query(news_environment_id,news_collection_id, qopts)
    results = my_query['aggregations'][0]['results']
    scorePos = 0
    scoreNeg = 0
    scoreOther = 0
    for result in results:
        result = result['aggregations'][0]['results']
        for dt in result:
            if dt['key'] == 'positive':
                scorePos += dt['matching_results']
            elif dt['key'] == 'negative':
                scoreNeg += dt['matching_results']
            else:
                scoreOther += dt['matching_results']
    try:
        return float(scorePos)/(scorePos+scoreNeg+scoreOther)
    except:
        return None

def genSentiment(ID,username="434eb326-be2c-4326-acd1-edc979bb8716",
                 password="f8BEJllUl3Xb",version="2016-12-01"):
    keys = ID.keys()
    lt = []
    for key in keys:
        print key
        
        if len(key)<3:
           continue
        url = DM.getBaseURL(key)
        title = DM.getTitle(url)
        if title==None:
            continue
        tBegin = calendar.timegm(time.strptime('1-Jan-2017',"%d-%b-%Y"))
        tEnd = calendar.timegm(time.gmtime())
        lt.append([ID[key],getSentiment(title,tBegin,tEnd,username,password,version)])
    pd.DataFrame(lt,columns = ['ID','Sentiment']).to_csv('Sentiment Scores.csv')
ID = DM.getID('DATA/')
genSentiment(ID)