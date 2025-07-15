from .base import MCPTool
from datetime import datetime
from typing import Dict, Any
import requests
from bs4 import BeautifulSoup
import logging

class GoogleNewsSearchTool(MCPTool):
    def __init__(self):
        super().__init__(
            name="google_news_search",
            description="Google新闻搜索多方法MCP工具，支持关键词、时间范围等参数。"
        )
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
            self.logger.addHandler(handler)
        self._methods = {
            "search_news": {
                "description": "Google新闻搜索",
                "parameters": {
                    "query": {"type": "string", "description": "搜索关键词"},
                    "max_results": {"type": "integer", "default": 5},
                    "start_date": {"type": "string", "description": "开始日期(YYYY-MM-DD)", "required": False},
                    "end_date": {"type": "string", "description": "结束日期(YYYY-MM-DD)", "required": False}
                }
            }
        }

    def get_methods(self) -> Dict[str, Any]:
        return self._methods

    def get_schema(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "methods": self.get_methods()
        }

    def get_parameters(self) -> Dict[str, Any]:
        return self.get_methods()

    def execute(self, method: str, **kwargs):
        if not method or method not in self._methods:
            return f"不支持的方法: {method}"
        try:
            if method == "search_news":
                return self.search_news(kwargs)
            else:
                return f"未知方法: {method}"
        except Exception as e:
            return f"Google News搜索失败: {e}"

    def search_news(self, kwargs):
        query = kwargs.get("query")
        max_results = kwargs.get("max_results", 5)
        start_date = kwargs.get("start_date")
        end_date = kwargs.get("end_date")
        # --- 以下为原有逻辑 ---
        tbs = ""
        if start_date and end_date:
            if "-" in start_date:
                start_date_fmt = datetime.strptime(start_date, "%Y-%m-%d").strftime("%m/%d/%Y")
            else:
                start_date_fmt = start_date
            if "-" in end_date:
                end_date_fmt = datetime.strptime(end_date, "%Y-%m-%d").strftime("%m/%d/%Y")
            else:
                end_date_fmt = end_date
            tbs = f"&tbs=cdr:1,cd_min:{start_date_fmt},cd_max:{end_date_fmt}"
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }
        news_results = []
        page = 0
        max_pages = 3
        while page < max_pages and len(news_results) < max_results:
            offset = page * 10
            url = (
                f"https://www.google.com/search?q={query}"
                f"{tbs}"
                f"&tbm=nws&start={offset}"
            )
            self.logger.info(f"搜索第 {page + 1} 页: {url}")
            try:
                response = requests.get(url, headers=headers, timeout=15)
                self.logger.info(f"实际返回URL: {response.url}")
                self.logger.debug(f"部分HTML: {response.text[:1000]}")
                response.raise_for_status()
                soup = BeautifulSoup(response.content, "html.parser")
            except Exception as e:
                self.logger.error(f"Google News搜索请求或解析失败: {e}")
                break
            try:
                results_on_page = soup.select('div.SoaBEf')
                self.logger.debug(f"使用选择器 'div.SoaBEf' 查找新闻结果，数量: {len(results_on_page)}")
                if not results_on_page:
                    self.logger.warning(f"页面 {page + 1} 没有找到新闻结果，选择器未命中")
                    break
                self.logger.info(f"页面 {page + 1} 找到 {len(results_on_page)} 个新闻结果")
                for el in results_on_page:
                    if len(news_results) >= max_results:
                        break
                    a_tag = el.select_one('a.WlydOe')
                    news_url = a_tag['href'] if a_tag and a_tag.has_attr('href') else ''
                    title_tag = el.select_one('div.n0jPhd')
                    title = title_tag.get_text(strip=True) if title_tag else ''
                    desc_tag = el.select_one('div.GI74Re')
                    description = desc_tag.get_text(strip=True) if desc_tag else ''
                    source_tag = el.select_one('div.MgUUmf span')
                    source = source_tag.get_text(strip=True) if source_tag else ''
                    date_tag = el.select_one('div.LfVVr span')
                    if not date_tag:
                        date_tag = el.select_one('div.OSrXXb span')
                    date = date_tag.get_text(strip=True) if date_tag else ''
                    if title and news_url:
                        news_results.append({
                            'title': title,
                            'url': news_url,
                            'snippet': description,
                            'source': source,
                            'date': date
                        })
                        self.logger.debug(f"添加新闻结果: {title[:50]}...")
            except Exception as e:
                self.logger.error(f"Google News结果解析失败: {e}")
                break
            page += 1
        self.logger.info(f"Google News搜索完成，共找到 {len(news_results)} 个结果")
        return {
            "query": query,
            "results": news_results[:max_results],
            "total_results": len(news_results)
        } 