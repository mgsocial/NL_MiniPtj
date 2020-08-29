from django.shortcuts import render
from django.http import HttpResponse


def home(request) :

    return render(request, 'index.html')

def recommend(request) :
    import pandas as pd
    import numpy as np
    import re
    import csv
    from sklearn.feature_extraction.text import TfidfVectorizer
    
    
    stock = pd.read_csv('./NLptj/ContentStock.csv', encoding='utf-8')

    tfidf_vec = TfidfVectorizer(ngram_range=(1, 2))
    tfidf_matrix = tfidf_vec.fit_transform(stock['words'])

    from sklearn.metrics.pairwise import cosine_similarity
    genres_similarity = cosine_similarity(tfidf_matrix, tfidf_matrix)
    similar_index = np.argsort(-genres_similarity)

    from sklearn.feature_extraction.text import CountVectorizer
    count_vec = CountVectorizer(ngram_range=(1, 2))
    count_matrix = count_vec.fit_transform(stock['words'])

    from sklearn.metrics.pairwise import cosine_similarity
    genres_similarity = cosine_similarity(count_matrix, count_matrix)
    similar_index = np.argsort(-genres_similarity)


    input_stock = request.POST['name'].upper()

    stock_index = stock[stock['name'] ==input_stock].index.values
    similar_stock = similar_index[stock_index, :5]
    similar_stock_index = similar_stock.reshape(-1)

    import requests
    from bs4 import BeautifulSoup
    from urllib import parse
    import json


    query = list(stock.iloc[similar_stock_index]['name'])
    price = int(request.POST['price'])
    stockList = {}



    print(input_stock, '와(과) 관련된 종목')
    print('종목코드', '종목명', '현재가', '전일대비', '등락률')
    idx = 0
    for c in query : 
        params = (
            ('keyword', c),
            ('pageSize', '20'),
            ('page', '1'),
        )
        response = requests.get('https://m.stock.naver.com/api/json/search/searchListJson.nhn', params=params)
        result = json.loads(response.text)

        result = result['result']['d'][0]


        if float(result['nv']) <= price:
            print(result['cd'], result['nm'], result['nv'], result['cv'], result['cr'])
            stockList[str(idx)]={'code' : result['cd'], 'name' : result['nm'], 'price' : result['nv'], 'cprice':result['cv'], 'cper' : result['cr']}
        print('----------------------------------------')
        idx +=1
    return render(request, 'index.html', {'stockList' : stockList})
