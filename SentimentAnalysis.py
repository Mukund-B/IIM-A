# -*- coding: utf-8 -*-
"""
Created on Wed Mar 01 14:37:22 2017

@author: Mukundbj
"""


import os
import slate
import pandas as pd
from nltk.tokenize import RegexpTokenizer
from collections import Counter
from nltk import tokenize
from nltk.tokenize import word_tokenize
import re

#os.chdir('C:\Users\Mukundbj\Desktop')

def genDict():
    
    wordList = pd.read_csv('MasterDictionary.csv')
    LM_negative = wordList['Word'][wordList['Negative']>2000]
    LM_positive = wordList['Word'][wordList['Positive']>2000]
    LM_negative.to_csv('LM_negative.csv',index=False)
    LM_positive.to_csv('LM_positive.csv',index=False)

def loadDict(path):
        def load(name):
            with open(path+name, "r") as f:
                words = f.readlines()
            words = [pos.strip().lower() for pos in words]
            return words
        pos = load('LM_positive.csv')
        neg = load('LM_negative.csv')
        stop = load('StopWords_Generic.txt')
        return pos,neg,stop

def calcScore(words,List):
        count = 0
        for word in words.keys():
            if word in List:
                count += words[word]
        return count
    
def sentiment(doc,path):
    
    positive,negative,stop = loadDict(path)
    words = getWords(getText(doc),stop)
    fdist = dict(Counter(words))
    negScore = calcScore(fdist,negative)
    posScore = calcScore(fdist,positive)
    return posScore - negScore

def sentimentVader(sentences):
    from nltk.sentiment.vader import SentimentIntensityAnalyzer
    sid = SentimentIntensityAnalyzer()
    score = 0.0
    for sentence in sentences:
        ss = sid.polarity_scores(sentence)
        if ss['pos'] > ss['neg']:
            score += 1
        elif ss['pos'] < ss['neg']:
            score -= 1
    return score

def loadDoc(name):
    
    with open(name,'rb') as f:
        doc = slate.PDF(f)
    return doc
def getText(doc):
    text = ' '.join(doc)
    #remove numbers, hex values, some special characters
    text = text.strip().decode('utf8').encode('ascii', errors='ignore')
    text = ' '.join(text.split())
    return text

def getWords(text,stop):   
    word_tokenizer = RegexpTokenizer(r'\w+')
    words = word_tokenizer.tokenize(text)
    #remove stop words
    clean = [word.strip() for word in words if word not in stop]
    return clean

def getSentences(text):
    sent = tokenize.sent_tokenize(text)
    return sent

def getForwardLookingSentences(sentences):
    forward_looking_terms=['future','plan to','future plan','look forward','forward','looking','ahead','looking ahead','planning to','anticipate','anticipating','expecting','expect']
    forward_looking_sentences = []
    for i in sentences: 
        word_tokens = word_tokenize(i)
        count1 = 0
        for j in word_tokens:
            word_tokens[count1] = j.lower()
            count1 = count1 + 1
        if any(x in forward_looking_terms for x in word_tokens): 
            forward_looking_sentences.append(i) 
    answer = [] 
    for i in forward_looking_sentences:  
        if '.....' in i:
            continue
        answer.append(i)
    return answer  
   


def isPresent(text,page,start=None,stop=None):
    return any(re.search(w,getText(page.split('\n')[start:stop])) for w in text)

def isPresent_all(text,page,start=None,stop=None):
    return all(re.search(w,getText(page.split('\n')[start:stop])) for w in text)

def searchTitle(title,doc,stop=None):
    for i,page in enumerate(doc):
        if isPresent([title],page,stop=stop):
            yield i,page

def list_files(dir):
    r = []
    for root, dirs, files in os.walk(dir):
        for name in files:
            r.append(os.path.join(root, name))
    return r

def genFLS():
    files = list_files('M:/Documents/IIM-A Hackathon/DATA/')
    data = list()
    for file in files:
        if file[-4:]!=".pdf":
            continue
        ID = file[:6]
        year = '20'+file[-6:-4]
        doc = loadDoc(file)
        text1 = getText(doc)
        sentences1 = getSentences(text1)
        sentences1 = getForwardLookingSentences(sentences1)
        fls = ','.join(sentences1)
        data.append([ID,fls,year])
    pd.DataFrame(data,columns = ['ID','Forward Looking Sentences','Year']).to_csv('Forward Looking Sentences.csv')