"""
搜索引擎封装模块
支持 DuckDuckGo 和 Sogou 两种搜索方式
"""

import time
from typing import List, Dict, Any
from duckduckgo_search import DDGS
from googlenews_utils import GoogleNewsSearch
from datetime import datetime

# 尝试导入搜狗搜索，如果失败则只支持DDG
try:
    from sogou_search import sogou_search
    SOGOU_AVAILABLE = True
except ImportError:
    SOGOU_AVAILABLE = False

class SearchEngine:
    """搜索引擎封装类，支持多引擎合并去重"""

    def __init__(self, engine: str = "ddg"):
        """
        初始化搜索引擎

        Args:
            engine: 搜索引擎类型，支持 "ddg" (DuckDuckGo)、"sogou" (搜狗)、"google" (Google News) 或它们的列表
        """
        if isinstance(engine, str):
            self.engines = [engine.lower()]
        else:
            self.engines = [e.lower() for e in engine]
        self.delay = 1.0  # 默认搜索延迟

        # 检查支持性
        valid_engines = []
        for e in self.engines:
            if e not in ["ddg", "sogou", "google"]:
                print(f"警告: 不支持的搜索引擎: {e}. 跳过。")
                continue
            if e == "sogou" and not SOGOU_AVAILABLE:
                print("警告: 搜狗搜索 (k_sogou_search) 未安装, 跳过搜狗。")
                continue
            valid_engines.append(e)
        if not valid_engines:
            raise ValueError("没有可用的搜索引擎。支持: 'ddg', 'sogou', 'google'")
        self.engines = valid_engines

    def search(self, keywords: str, max_results: int = 10, start_date=None, end_date=None) -> List[Dict[str, Any]]:
        """
        统一搜索接口，支持多引擎合并去重

        Args:
            keywords: 搜索关键词
            max_results: 每个引擎最大结果数
            start_date, end_date: 仅对 google 有效，格式 yyyy-mm-dd

        Returns:
            搜索结果列表，每个结果包含 title, url, description, engine 字段
        """
        print(f"使用 {','.join([e.upper() for e in self.engines])} 搜索引擎搜索: '{keywords}'")
        all_results = {}
        for engine in self.engines:
            try:
                if engine == "ddg":
                    results = self._search_ddg(keywords, max_results)
                elif engine == "sogou":
                    results = self._search_sogou(keywords, max_results)
                elif engine == "google":
                    results = self._search_google(keywords, max_results, start_date, end_date)
                else:
                    results = []
                for r in results:
                    url = r.get('url')
                    if not url:
                        continue
                    if url in all_results:
                        # 已有，合并 engine 字段
                        if engine not in all_results[url]['engine']:
                            all_results[url]['engine'].append(engine)
                    else:
                        # 新结果
                        r['engine'] = [engine]
                        all_results[url] = r
                time.sleep(self.delay)
            except Exception as e:
                print(f"搜索失败 ({engine}): {e}")
        # 返回合并后的结果
        return list(all_results.values())

    def _search_ddg(self, keywords: str, max_results: int) -> List[Dict[str, Any]]:
        """DuckDuckGo 搜索"""
        results = DDGS().text(
            keywords=keywords,
            region="cn-zh",
            max_results=max_results
        )
        # 标准化结果格式
        return [
            {
                'title': r.get('title', '无标题'),
                'url': r.get('href', '无链接'),
                'description': r.get('body', '无摘要')
            }
            for r in results
        ]

    def _search_sogou(self, keywords: str, max_results: int) -> List[Dict[str, Any]]:
        """搜狗搜索"""
        if not SOGOU_AVAILABLE:
            return []
        # 假设 sogou_search 返回的结果已包含 title, url, description 字段
        return sogou_search(keywords, num_results=max_results)

    def _search_google(self, keywords: str, max_results: int, start_date=None, end_date=None) -> List[Dict[str, Any]]:
        """Google News 搜索"""
        # start_date, end_date 格式: yyyy-mm-dd
        # getNewsData 返回: link, title, snippet, date, source
        if not start_date:
            start_date = datetime.now().strftime("%Y-%m-%d")
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
        news =  GoogleNewsSearch.search(keywords, max_results, start_date, end_date)
        # 标准化格式
        results = []
        for r in news[:max_results]:
            print(r)
            results.append({
                'title': r.get('title', '无标题'),
                'url': r.get('url', '无链接'),
                'description': r.get('description', '无摘要'),
                'date': r.get('date', r.get('date', '')),
                'source': r.get('source', r.get('source', ''))
            })
        return results

if __name__ == "__main__":
    # 测试代码
    print("测试搜索引擎封装...")

    # 测试多引擎合并
    print("\n=== 测试多引擎合并 ===")
    # engines = ["ddg", "google"]
    # if SOGOU_AVAILABLE:
    #     engines.append("sogou")
    engines = ["google"]
    multi_engine = SearchEngine(engine=engines)
    multi_results = multi_engine.search("商汤科技", max_results=2, start_date="2024-01-01", end_date="2024-06-01")
    for i, result in enumerate(multi_results, 1):
        print(f"{i}. {result['title']}")
        print(f"   URL: {result['url']}")
        print(f"   描述: {result['description'][:100]}...")
        print(f"   来源引擎: {result['engine']}")
        if 'date' in result:
            print(f"   日期: {result.get('date', '')}")
        if 'source' in result:
            print(f"   来源: {result.get('source', '')}")
