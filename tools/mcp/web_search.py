# -*- coding: utf-8 -*-
"""
网络搜索工具
"""

import time
import random
import requests
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from bs4 import BeautifulSoup
from .base import MCPTool


class WebSearchTool(MCPTool):
    """网络搜索工具"""
    
    def __init__(self, api_key: str = None, default_engine: str = "google"):
        super().__init__(
            name="web_search",
            description="搜索网络信息",
            config={"api_key": api_key, "default_engine": default_engine}
        )
        self.default_engine = default_engine
        
        # 设置日志记录器
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # 如果还没有处理器，添加控制台处理器
        if not self.logger.handlers:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
    
    def execute(self, query: str, max_results: int = 5, search_engine: str = None, 
                search_type: str = "web", start_date: str = None, end_date: str = None) -> Dict[str, Any]:
        """执行网络搜索"""
        # 使用指定的搜索引擎或默认搜索引擎
        engine = search_engine or self.default_engine
        
        self.logger.info(f"开始执行搜索: 查询='{query}', 引擎={engine}, 类型={search_type}, 最大结果={max_results}")
        
        try:
            # 根据搜索类型选择不同的搜索方法
            if search_type.lower() == "news":
                if engine.lower() == "google":
                    self.logger.info("使用Google News搜索")
                    results = self._search_google_news(query, max_results, start_date, end_date)
                    return {
                        "query": query,
                        "search_engine": "google",
                        "search_type": "news",
                        "results": results,
                        "total_results": len(results)
                    }
                else:
                    self.logger.error(f"{engine} 搜索引擎暂不支持新闻搜索")
                    raise NotImplementedError(f"{engine} 搜索引擎暂不支持新闻搜索")
            
            # 普通网页搜索
            if engine.lower() == "google":
                self.logger.info("使用Google网页搜索")
                return self._search_google(query, max_results)
            elif engine.lower() == "bing":
                self.logger.info("使用Bing搜索")
                return self._search_bing(query, max_results)
            elif engine.lower() == "duckduckgo":
                self.logger.info("使用DuckDuckGo搜索")
                return self._search_duckduckgo(query, max_results)
            else:
                self.logger.error(f"不支持的搜索引擎: {engine}")
                raise ValueError(f"不支持的搜索引擎: {engine}")
        except Exception as e:
            self.logger.error(f"搜索执行失败: {e}")
            raise
    
    def _search_google(self, query: str, max_results: int) -> Dict[str, Any]:
        """Google搜索实现"""
        results = self._scrape_google_search(query, max_results)
        return {
            "query": query,
            "search_engine": "google",
            "results": results,
            "total_results": len(results)
        }
    
    def _make_request(self, url: str, headers: Dict[str, str]) -> requests.Response:
        """发送请求，包含重试逻辑和速率限制"""
        try:
            # 更长的随机延迟避免被检测
            delay = random.uniform(3, 5)
            self.logger.info(f"等待 {delay:.2f} 秒后发送请求")
            time.sleep(delay)
            
            self.logger.info(f"发送请求到: {url}")
            response = requests.get(url, headers=headers, timeout=30)
            self.logger.info(f"请求完成，状态码: {response.status_code}")
            
            # 检查是否被重定向到验证页面
            if "consent" in response.url or "sorry" in response.url:
                self.logger.warning(f"可能被Google重定向到验证页面: {response.url}")
            
            return response
        except requests.exceptions.Timeout:
            self.logger.error(f"请求超时: {url}")
            raise
        except requests.exceptions.ConnectionError as e:
            self.logger.error(f"连接错误: {url}, 错误: {e}")
            raise
        except requests.exceptions.RequestException as e:
            self.logger.error(f"请求失败: {url}, 错误: {e}")
            raise
        except Exception as e:
            self.logger.error(f"未知错误: {url}, 错误: {e}")
            raise
    
    def _scrape_google_search(self, query: str, max_results: int = 10) -> List[Dict[str, str]]:
        """抓取Google搜索结果"""
        self.logger.info(f"开始Google搜索: {query}, 最大结果数: {max_results}")
        
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
        
        search_results = []
        page = 0
        max_pages = 3  # 最多翻3页，防止死循环
        
        while page < max_pages and len(search_results) < max_results:
            offset = page * 10
            url = (
                f"https://www.google.com/search?q={query}"
                f"&udm=14&start={offset}"
            )
            self.logger.info(f"搜索第 {page + 1} 页: {url}")
            
            try:
                response = self._make_request(url, headers)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, "html.parser")
            except Exception as e:
                self.logger.error(f"Google搜索请求或解析失败: {e}")
                break

            try:
                #定义可能的搜索结果选择器
                possible_selectors = [
                    '.MjjYud',
                ]
                # 尝试使用可能的选择器
                for selector in possible_selectors:
                    results_on_page = soup.select(selector)
                    if results_on_page:
                        break
                if not results_on_page:
                    self.logger.warning(f"页面 {page + 1} 没有找到搜索结果，选择器均未命中")
                    print(soup.select('#search'))
                    break
                self.logger.info(f"页面 {page + 1} 找到 {len(results_on_page)} 个结果")
                
                for result in results_on_page:
                    if len(search_results) >= max_results:
                        break
                    # 提取标题
                    title_tag = result.select_one('h3')
                    title = title_tag.get_text(strip=True) if title_tag else ''
                    # 提取链接
                    link_tag = result.select_one('a')
                    url = link_tag.get('href', '') if link_tag else ''
                    if url.startswith('/url?q='):
                        url = url.split('/url?q=')[1].split('&')[0]
                    # 提取摘要
                    snippet_tag = result.select_one('.VwiC3b')
                    if not snippet_tag:
                        snippet_tag = result.select_one('.st')
                    snippet = snippet_tag.get_text(strip=True) if snippet_tag else ''
                    if title and url:
                        search_results.append({
                            'title': title,
                            'url': url,
                            'snippet': snippet
                        })
                        self.logger.debug(f"添加搜索结果: {title[:50]}...")
            except Exception as e:
                self.logger.error(f"Google搜索结果解析失败: {e}")
                break
            page += 1
        self.logger.info(f"Google搜索完成，共找到 {len(search_results)} 个结果")
        return search_results[:max_results]
    
    def _search_google_news(self, query: str, max_results: int = 10, 
                           start_date: Optional[str] = None, 
                           end_date: Optional[str] = None) -> List[Dict[str, str]]:
        """抓取Google News搜索结果"""
        self.logger.info(f"开始Google News搜索: {query}, 最大结果数: {max_results}")
        if start_date and end_date:
            self.logger.info(f"日期范围: {start_date} 到 {end_date}")
        # 处理日期参数
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
        max_pages = 3  # 最多翻3页，防止死循环
        while page < max_pages and len(news_results) < max_results:
            offset = page * 10
            url = (
                f"https://www.google.com/search?q={query}"
                f"{tbs}"
                f"&tbm=nws&start={offset}"
            )
            self.logger.info(f"搜索第 {page + 1} 页: {url}")
            try:
                response = self._make_request(url, headers)
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
                    # 提取URL
                    a_tag = el.select_one('a.WlydOe')
                    news_url = a_tag['href'] if a_tag and a_tag.has_attr('href') else ''
                    # 提取标题
                    title_tag = el.select_one('.n0jPhd')
                    title = title_tag.get_text(strip=True) if title_tag else ''
                    # 提取描述
                    desc_tag = el.select_one('.GI74Re')
                    description = desc_tag.get_text(strip=True) if desc_tag else ''
                    # 提取来源
                    source_tag = el.select_one('.MgUUmf span')
                    source = source_tag.get_text(strip=True) if source_tag else ''
                    # 提取日期
                    date_tag = el.select_one('.LfVVr span')
                    if not date_tag:
                        date_tag = el.select_one('.OSrXXb span')
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
        return news_results[:max_results]
    
    def _search_bing(self, query: str, max_results: int) -> Dict[str, Any]:
        """Bing搜索实现"""
        raise NotImplementedError("Bing搜索功能尚未实现")
    
    def _search_duckduckgo(self, query: str, max_results: int) -> Dict[str, Any]:
        """DuckDuckGo搜索实现"""
        raise NotImplementedError("DuckDuckGo搜索功能尚未实现")
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "搜索查询"
                },
                "max_results": {
                    "type": "integer",
                    "description": "最大结果数量",
                    "default": 5
                },
                "search_engine": {
                    "type": "string",
                    "description": "搜索引擎",
                    "enum": ["google", "bing", "duckduckgo"],
                    "default": "google"
                },
                "search_type": {
                    "type": "string",
                    "description": "搜索类型",
                    "enum": ["web", "news"],
                    "default": "web"
                },
                "start_date": {
                    "type": "string",
                    "description": "开始日期 (YYYY-MM-DD格式，仅用于新闻搜索)"
                },
                "end_date": {
                    "type": "string",
                    "description": "结束日期 (YYYY-MM-DD格式，仅用于新闻搜索)"
                }
            },
            "required": ["query"]
        } 