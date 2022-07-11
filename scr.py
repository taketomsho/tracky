import requests
from urllib import request
import tldextract
from bs4 import BeautifulSoup
import re
from logging import getLogger
import statistics
import json
import datetime
import pandas as pd
from PIL import Image
import io
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import django

from rq import get_current_job

import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')  # 自分のsettings.py
django.setup()

from apps.home.models import Rank, Keyword

logger = getLogger(__name__)


class Scraper(object):

    def __init__(self, keyword, domain) -> None:
        # ログ出力の初期設定
        self.logger = getLogger(__name__)
        self.keyword = keyword
        self.domain = str(domain)

    def google_search(self, num):
        googleSearch = 'https://www.google.co.jp/search'

        # ユーザーエージェントを使って回避できる可能性あり
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36"}

        response = requests.get(googleSearch, params={
                                'q': self.keyword, 'num': num}, headers=headers)
        html = response.text.encode()
        bs4 = BeautifulSoup(html, 'html.parser')
        return bs4

    # インプットしたキーワードに対してSERPSのURLをリストで返してくれる関数
    def search_rank(self):
        
        bs4 = self.google_search(30)
        # Google検索のSERPSの情報を取得
        try:
            searchResults = bs4.select('div.yuRUbf> a')
        except Exception as e:
            self.logger.error("SERPSが取得できません")

        # 各SERPSのURLだけ抜き取ってリストに格納
        url_list = []
        try:
            for searchResult in searchResults:
                url_temp = re.sub("\/url\?q=", "", searchResult.get('href'))
                url = re.sub("&sa.*", "", url_temp)
                url_list.append(url)

        except Exception as e:
            self.logger.error("SERPSのURLの取得に失敗しました")
        
        # ランクを取得する
        rank = 0
        for index, url in enumerate(url_list):
            if self.domain in url:
                rank = index + 1
                break
        
        # rankが0のままの場合は圏外を返す
        if rank == 0:
            return 0, None
        else:
            return rank, url

def main():
    today = datetime.date.today()
    Rank.objects.filter(date=today).delete()

    keyword_list = Keyword.objects.all()

    for keyword in keyword_list:
        scr = Scraper(keyword.name, keyword.domain)
        rank_score, url = scr.search_rank()
        Rank.objects.create(keyword=keyword, domain=keyword.domain, rank = rank_score, url=url, date=today)
    
    Rank.objects.filter(date__isnull=True).delete()

if __name__ == "__main__": 
    main()