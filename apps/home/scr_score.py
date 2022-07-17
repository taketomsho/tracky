# - スクレイピング処理関数
# - beautifulsoupを使用

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

from rq import get_current_job


logger = getLogger(__name__)

class KeywordZeroError(Exception):
    """キーワードがない時に発生する例外"""
    def __init__(self):
        # jobのメタ情報にKeywordZeroErrorを入れる
        job = get_current_job()
        job.meta['my_error'] = "KeywordZeroError"
        job.save_meta()


class FewArticlesError(Exception):
    """取得できる記事が少なすぎる時に発生する例外"""
    def __init__(self):
        # jobのメタ情報にFewArticlesErrorを入れる
        job = get_current_job()
        job.meta['my_error'] = "FewArticlesError"
        job.save_meta()

class Scraper(object):

    def __init__(self, keyword, url) -> None:
        # ログ出力の初期設定
        self.logger = getLogger(__name__)
        self.keyword = keyword
        self.url = url

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
    def search_top(self, num):
        bs4 = self.google_search(num)
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
            return url_list

        except Exception as e:
            self.logger.error("SERPSのURLの取得に失敗しました")
    
    def rank_tracker(self):
        url_list = self.search_top(30)
        rank = 0
        for index, url in enumerate(url_list):
            if self.url in url:
                rank = index + 1
                break
        
        # rankが0のままの場合は圏外を返す
        if rank == 0:
            return "圏外"
        else:
            return rank

    def get_result(self):
        # 比較したい自分の記事のurlの情報を抽出
        my_article = Article(self.url)
        # 自分の記事の本文にキーワードが含まれているかをチェック
        my_article.scr_keywords_check(self.keyword)

        # キーワードに基づくURLを算出
        url_list = self.search_top(10)
        
        # キーワードに基づく各記事の情報を抽出
        top_articles = []
        for url in url_list:
            try:
                article = Article(url)
                top_articles.append(article)
            except:
                self.logger.warning(url + "：URLの記事を取得できません")
                # 次のURLへ遷移

        if len(top_articles) < 3:
            raise(FewArticlesError)

        analytics = Analytics(top_articles, my_article, self.keyword)

        summary = analytics.summarize()
        
        # 順位をresultにわたす情報として入れる
        summary["rank"] = self.rank_tracker()

        return summary


class Analytics():
    def __init__(self, top_articles, my_article, keyword) -> None:
        self.top_articles = top_articles
        self.my_article = my_article
        self.keyword = keyword

    def make_summary(self,data_contains_none,selfdata):
        # TODO: make_summary関連のfuncが冗長なので整理
        
        data = [item for item in data_contains_none if item is not None]
        try:
            return dict(
                max=max(data),
                min=min(data),
                mean=round(sum(data)/len(data), 1),
                self=selfdata,
                deviation=round(selfdata - sum(data)/len(data),1),
                data=data
            )
        except:
            return dict(
                max="解析不能",
                min="解析不能",
                mean="解析不能",
                self=selfdata,
                deviation="解析不能",
                score = 80,
                data=data
            )

    def make_summary_freshness(self,data_contains_none,selfdata):

        # Noneでないデータをカウントする。
        data = [item for item in data_contains_none if item is not None]
        not_none_ratio = len(data)/len(data_contains_none)

        summary = {}
        # そもそもArticle構造化データに意味がない場合、解析不能として値を返却する。
        if not_none_ratio < 0.3:
            summary["max"] = "解析不能"
            summary["min"] = "解析不能"
            summary["mean"] = "解析不能"
            summary["score"] = "解析不能"

            if selfdata is None:
                # Article構造化データに意味がない場合は、自分の記事に構造化データが設定されていなくてもそれほど問題ではないため、score=80
                summary["self"] = "なし"
                return summary

            summary["self"] = selfdata
            return summary

        summary["max"] = max(data)
        summary["min"] = min(data)
        mean_value = sum(data)/len(data)
        summary["mean"] = round(mean_value, 1)
        summary["data"] = data

        if selfdata is not None:
            summary["self"] = selfdata
            deviation = selfdata - mean_value
            summary["deviation"] = abs(round(deviation,1))
            if deviation <= 0:
                score = 100
            else:
                score = round(100 - abs(deviation) / statistics.stdev(data) * 20,1) # 絶対偏差を標準偏差で割って10をかけて100から引く(偏差値と似た算出方法)
            if score <= 0:
                score = 0
            summary["score"] = score
        # selfdataがない場合、score=60で返却
        else:
            summary["score"] = 60
            summary["self"] = "なし"

        return summary

    def make_summary_keyword(self, data, selfdata):
        keyword_list = self.keyword.split()
        data = pd.DataFrame(data)
        selfdata = pd.Series(selfdata)

        try:
            # 絶対偏差を標準偏差で割って10をかけて100から引く(偏差値と似た算出方法)
            temp_score = round(
                100 - abs(selfdata - data.sum(axis=0)/len(data)) / data.std()*20, 1)
            score = temp_score.mean()
            if score <= 0:
                score = 0

        except ZeroDivisionError:
            score = 0
        
        return dict(
            max=data.max(),
            min=data.min(),
            mean=round(data.sum()/len(data), 1),
            keyword_list=keyword_list,
            score=score,
            deviation=round(selfdata - pd.Series(data.sum()/len(data)), 1),
            self=selfdata
        )

    def summarize(self):
        title_data = [article.count_title() for article in self.top_articles]
        meta_data = [article.count_meta() for article in self.top_articles]
        body_data = [article.count_body() for article in self.top_articles]
        img_data = [article.count_img() for article in self.top_articles]
        h2_tag_data = [article.count_tags()["h2"]
                       for article in self.top_articles]
        h3_tag_data = [article.count_tags()["h3"]
                       for article in self.top_articles]
        h4_tag_data = [article.count_tags()["h4"]
                       for article in self.top_articles]
        inner_link_data = [article.count_link()["inner"]
                           for article in self.top_articles]
        outer_link_data = [article.count_link()["outer"]
                           for article in self.top_articles]
        freshness_data = [article.get_freshness() for article in self.top_articles]
        body_keyword_data = [article.scr_keywords(
            self.keyword)["body_keyword"] for article in self.top_articles]
            

        summary = dict(
            keyword=self.keyword,
            url=self.my_article.url,
            title=self.make_summary(title_data, self.my_article.count_title()),
            meta=self.make_summary(meta_data, self.my_article.count_meta()),
            body=self.make_summary(body_data, self.my_article.count_body()),
            img=self.make_summary(img_data, self.my_article.count_img()),
            h2=self.make_summary(
                h2_tag_data, self.my_article.count_tags()["h2"]),
            h3=self.make_summary(
                h3_tag_data, self.my_article.count_tags()["h3"]),
            h4=self.make_summary(
                h4_tag_data, self.my_article.count_tags()["h4"]),
            inner_link=self.make_summary(
                inner_link_data, self.my_article.count_link()["inner"]),
            outer_link=self.make_summary(
                outer_link_data, self.my_article.count_link()["outer"]),
            freshness=self.make_summary_freshness(freshness_data,self.my_article.get_freshness()),
            body_keyword=self.make_summary_keyword(
                body_keyword_data, self.my_article.scr_keywords(self.keyword)["body_keyword"]),
        )
        summary["score"] = self.calc_total_score(summary)
        return summary

    def calc_score(self,data,selfdata):
    # 通常の情報のスコアを算出する関数
        try:
            # 絶対偏差を標準偏差で割って10をかけて100から引く(偏差値と似た算出方法)
            score = round(100 - abs(selfdata - sum(data)/len(data)
                                    ) / statistics.stdev(data) * 20, 1)
            if score <= 0:
                score = 0

        except ZeroDivisionError:
            score = 0
        return score
    
    def calc_score_img(self,data,selfdata):
    # img情報のスコアを算出する関数
        try:
            dev = selfdata - sum(data)/len(data)
            if dev >= 0:
                score = 100
            else:
                # 絶対偏差を標準偏差で割って10をかけて100から引く(偏差値と似た算出方法)
                score = round(100 - abs(selfdata - sum(data) /
                            len(data)) / statistics.stdev(data) * 20, 1)
            if score <= 0:
                score = 0

        except ZeroDivisionError:
            score = 0
        return score

    def calc_total_score(self,summary):
        tag_score = (self.calc_score(summary["h2"]["data"], summary["h2"]["self"]) * 4 + self.calc_score(summary["h3"]["data"], summary["h3"]["self"]) * 2 + self.calc_score(summary["h4"]["data"], summary["h4"]["self"]) * 1)/7
        text_score = (self.calc_score(summary["title"]["data"], summary["title"]["self"]) * 2 + self.calc_score(summary["meta"]["data"], summary["meta"]["self"]) * 4 + self.calc_score(summary["body"]["data"], summary["body"]["self"]) * 1)/7
        link_score = (self.calc_score(summary["inner_link"]["data"], summary["inner_link"]["self"]) + self.calc_score(summary["outer_link"]["data"], summary["outer_link"]["self"]))/2
        
        scores = [ text_score, tag_score, link_score, self.calc_score(summary["img"]["data"], summary["img"]["self"]), summary["body_keyword"]["score"] ]

        if summary["freshness"]["score"] == "解析不能":
            return dict(
                label=["文字数", "見出し数", "画像数", "リンク数", "キーワード数"],
                data=scores,
                total = round((sum(scores))/5,1)
                )
        scores.append(summary["freshness"]["score"])    
        return dict(
            label=["文字数", "見出し数", "画像数", "リンク数", "キーワード数","更新性"],
            data=scores,
            total=round(sum(scores)/6,1)
            )

class Article():
    def __init__(self, url) -> None:
        # ログ出力の初期設定
        self.logger = getLogger(__name__)
        self.url = url
        self.bs4 = self.get_article()

    def get_article(self):
        requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += 'HIGH:!DH:!aNULL'
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36"}
        response = requests.get(self.url, headers=headers, timeout=10.0)
        html = response.text.encode()

        bs4 = BeautifulSoup(html, 'html.parser')
        return bs4

    def count_title(self):
        try:
            #    タイトルを抽出
            title = self.bs4.find("title")
            return len(title.text)

        except Exception as e:
            self.logger.warning(f"{self.url}：タイトル情報にアクセスできませんでした")
            return 0

    def count_meta(self):
        try:
            meta = self.bs4.find("meta", attrs={"name": "description"})[
                "content"]
            # メタディスクリプションの文字数をカウント
            return len(meta)
        except Exception as e:
            # メタディスクリプションがない場合はNullや0で埋めて処理継続
            self.logger.warning(f"{self.url}：メタディスクリプションがありません")
            return 0

    def count_body(self):
        try:
            count = len(self.bs4.find("body").text.replace("\n", ""))
            return count
        except Exception as e:
            self.logger.warning(f"{self.url}：本文がありません")
            return 0

    def count_img(self):
        try:
            # ドメイン解析
            ext = tldextract.extract(self.url)
            # ドメインから.comを覗いてトップレベルドメインだけ抽出
            domain_name = ext.domain
        except:
            pass

        # 全体の画像
        img_list = []
        for img in self.bs4.find_all("img"):
            # Noneオブジェクトではなくて（トップレベルドメイン）or（/から始まるscr）
            if img.get("src") is not None and (domain_name in img.get("src") or img.get("src").startswith("/")):
                img_list.append(img.get("src"))
            else:
                continue

        # 内部リンクやアフィリエイトリンクなどリンク付きの画像
        img_a_list = []
        for img in self.bs4.select('a img'):
            # Noneオブジェクトではなくて（トップレベルドメイン）or（/から始まるscr）
            if img.get("src") is not None and (domain_name in img.get("src") or img.get("src").startswith("/")):
                img_a_list.append(img.get("src"))
            else:
                continue

        # aタグが付いている画像は除外し、重複している画像も削除
        img_src_list = set(img_list) - set(img_a_list)

        return len(img_src_list)

    def count_each_tag(self, i):
        texts = []
        for tag in self.bs4.find_all("h"+str(i)):
            texts.append(tag.text)

        return len(texts)

    def count_tags(self):
        tag_dict = {}
        for i in range(2, 5):
            tag_dict["h"+str(i)] = self.count_each_tag(i)

        return tag_dict

    # 内部リンク、外部リンクを取得する

    def count_link(self):

        # 内部リンクと外部リンクの数を集計
        # ドメインを抽出
        try:
            domain = re.search('https?://[^/]+/', self.url).group()
            count_inner = 0
            count = 0
            for tag in self.bs4.find_all("a"):
                link = tag.get("href")
                # リンクがNoneの場合は除外
                if link != None:
                    # httpから始まる通常の内部リンク
                    if re.fullmatch(fr'{domain}.*', link) != None:
                        count_inner = count_inner + 1
                    # /1つから始まるドメイン省略の内部リンク
                    if re.fullmatch(fr'^/(?!(/)).*', link) != None:
                        count_inner = count_inner + 1
                    if re.fullmatch(fr'^#.*', link) == None:
                        count = count + 1
            count_outer = count - count_inner
            return dict(
                inner=count_inner,
                outer=count_outer
            )
        except Exception as e:
            self.logger.warning(f"{self.url}：リンクが見つかりませんでした")
            return dict(
                inner=0,
                outer=0
            )
    def get_freshness(self):
        try:
            ld_jsons = self.bs4.find_all('script', type='application/ld+json')
            ld_json = [json.loads(ld.text, strict=False) for ld in ld_jsons if ld.text != '' ]
            dateModified = self.search_json(ld_json,'dateModified')[0]
            date_modified = datetime.datetime.strptime(dateModified[0:10], '%Y-%m-%d').date()
        except Exception as e:
            # 取得できない場合はNoneを返す
            return None
        freshness = datetime.date.today() - date_modified 

        return freshness.days

    # 該当する値のリストを返す
    def search_json(self,arg,key):
        value_list = []
        if isinstance(arg, dict):
            if key in arg:
                value_list.append(arg[key])
        if isinstance(arg, list):
            for item in arg:
                value_list += self.search_json(item,key)
        elif isinstance(arg, dict):
            for value in arg.values():
                value_list += self.search_json(value,key)
        return value_list

# キーワード系を取得する

    def scr_keywords(self, keyword):
        keyword_list = keyword.split()

# キーワード系を取得する
        try:
            #    タイトルを抽出
            title = self.bs4.find("title")

            #     タイトル内のキーワード数を抽出
            keyword_count_list = []
            for i in keyword_list:
                keyword_count_list.append(title.text.count(i))

            title_keyword_list = {f"{keyword}": count for keyword, count in zip(
                keyword_list, keyword_count_list)}
        except Exception as e:
            self.logger.warning(f"{self.url}：タイトル情報にアクセスできませんでした")
            title_keyword_list = {
                f"{keyword}": 0 for keyword in keyword_list}
            # 次のURLへ遷移

        #     メタディスクリプションを抽出
        try:
            meta = self.bs4.find("meta", attrs={"name": "description"})[
                "content"]
            #     メタディスクリプション内のキーワード数を抽出
            keyword_count_list = []
            for i in keyword_list:
                keyword_count_list.append(meta.count(i))
            meta_keyword_list = {f"{keyword}": count for keyword, count in zip(
                keyword_list, keyword_count_list)}

        except Exception as e:
            # メタディスクリプションがない場合はNullや0で埋めて処理継続
            self.logger.warning(f"{self.url}：メタディスクリプションがありません")
            meta_keyword_list = {
                f"{keyword}": 0 for keyword in keyword_list}

        # 本文を抽出
        try:
            words = self.bs4.find("body").text.replace("\n", "")

            # 本文に出現するキーワード数をカウント
            keyword_count_list = []
            for i in keyword_list:
                keyword_count_list.append(words.count(i))

            body_keyword_list = {f"{keyword}": count for keyword,
                                count in zip(keyword_list, keyword_count_list)}

        except Exception as e:
            # 本文がない場合
            self.logger.warning(f"{self.url}：本文がありません")
            body_keyword_list = {
                f"{keyword}": 0 for keyword in keyword_list}
            # TODO: 0でリターンしているが、平均値に影響するためNULLで返したい
        return dict(
            body_keyword=body_keyword_list
        )

    def scr_keywords_check(self, keyword):
        # 本文にキーワードが含まれているかをチェックする関数

        keyword_list = keyword.split()
        try:
            words = self.bs4.find("body").text.replace("\n", "")

        except:
            return

         # 本文にキーワードが含まれていない場合エラーをRaiseする
        for i in keyword_list:
            if words.count(i) == 0:
                raise(KeywordZeroError)

       