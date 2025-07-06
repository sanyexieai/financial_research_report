import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import random
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    retry_if_result,
)


def is_rate_limited(response):
    """Check if the response indicates rate limiting (status code 429)"""
    return response.status_code == 429


@retry(
    retry=(retry_if_result(is_rate_limited)),
    wait=wait_exponential(multiplier=1, min=4, max=60),
    stop=stop_after_attempt(5),
)
def make_request(url, headers):
    """Make a request with retry logic for rate limiting"""
    # Random delay before each request to avoid detection
    time.sleep(random.uniform(2, 6))
    response = requests.get(url, headers=headers, timeout=10)
    return response


def getNewsData(query, start_date, end_date):
    """
    Scrape Google News search results for a given query and date range.
    query: str - search query
    start_date: str - start date in the format yyyy-mm-dd or mm/dd/yyyy
    end_date: str - end date in the format yyyy-mm-dd or mm/dd/yyyy
    """
    if "-" in start_date:
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        start_date = start_date.strftime("%m/%d/%Y")
    if "-" in end_date:
        end_date = datetime.strptime(end_date, "%Y-%m-%d")
        end_date = end_date.strftime("%m/%d/%Y")

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/101.0.4951.54 Safari/537.36"
        )
    }
    news_results = []
    page = 0
    max_pages = 3  # 最多翻3页，防止死循环
    while page < max_pages:
        print(f"Scraping page {page}")
        offset = page * 10
        url = (
            f"https://www.google.com/search?q={query}"
            f"&tbs=cdr:1,cd_min:{start_date},cd_max:{end_date}"
            f"&tbm=nws&start={offset}"
        )
        try:
            response = make_request(url, headers)
        except Exception as e:
            break
        soup = BeautifulSoup(response.content, "html.parser")
        
        results_on_page = soup.select('div.SoaBEf')
        if not results_on_page:
            print(f"No results on page {page}")
            break
        for el in results_on_page:
            # url
            a_tag = el.select_one('a.WlydOe')
            news_url = a_tag['href'] if a_tag and a_tag.has_attr('href') else ''
            # title
            title_tag = el.select_one('.n0jPhd')
            title = title_tag.get_text(strip=True) if title_tag else ''
            # description
            desc_tag = el.select_one('.GI74Re')
            description = desc_tag.get_text(strip=True) if desc_tag else ''
            # source
            source_tag = el.select_one('.MgUUmf span')
            source = source_tag.get_text(strip=True) if source_tag else ''
            # date
            date_tag = el.select_one('.LfVVr span')
            if not date_tag:
                date_tag = el.select_one('.OSrXXb span')
            date = date_tag.get_text(strip=True) if date_tag else ''
            news_results.append({
                'title': title,
                'url': news_url,
                'description': description,
                'source': source,
                'date': date
            })
        page += 1
    return news_results


class GoogleNewsSearch:
    @staticmethod
    def search(keywords, max_results=10, start_date=None, end_date=None):
        """
        统一 Google News 搜索接口，返回标准化结果
        Args:
            keywords: 搜索关键词
            max_results: 最大结果数
            start_date, end_date: 日期范围，格式 yyyy-mm-dd 或 mm/dd/yyyy
        Returns:
            标准化结果列表，每个结果包含 title, url, description, date, source
        """
        if not start_date:
            start_date = datetime.now().strftime("%Y-%m-%d")
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
        news = getNewsData(keywords, start_date, end_date)
        results = []
        for r in news[:max_results]:
            results.append({
                'title': r.get('title', '无标题'),
                'url': r.get('url', '无链接'),
                'description': r.get('description', '无摘要'),
                'date': r.get('date', ''),
                'source': r.get('source', '')
            })
        return results
