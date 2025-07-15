from tools.mcp import mcp
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import logging

@mcp.tool()
async def search_news(query: str, max_results: int = 5, start_date: str = None, end_date: str = None):
    logger = logging.getLogger("google_news_search")
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(handler)
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
        logger.info(f"搜索第 {page + 1} 页: {url}")
        try:
            response = requests.get(url, headers=headers, timeout=15)
            logger.info(f"实际返回URL: {response.url}")
            logger.debug(f"部分HTML: {response.text[:1000]}")
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")
        except Exception as e:
            logger.error(f"Google News搜索请求或解析失败: {e}")
            break
        try:
            results_on_page = soup.select('div.SoaBEf')
            logger.debug(f"使用选择器 'div.SoaBEf' 查找新闻结果，数量: {len(results_on_page)}")
            if not results_on_page:
                logger.warning(f"页面 {page + 1} 没有找到新闻结果，选择器未命中")
                break
            logger.info(f"页面 {page + 1} 找到 {len(results_on_page)} 个新闻结果")
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
                    logger.debug(f"添加新闻结果: {title[:50]}...")
        except Exception as e:
            logger.error(f"Google News结果解析失败: {e}")
            break
        page += 1
    logger.info(f"Google News搜索完成，共找到 {len(news_results)} 个结果")
    return {
        "query": query,
        "results": news_results[:max_results],
        "total_results": len(news_results)
    } 