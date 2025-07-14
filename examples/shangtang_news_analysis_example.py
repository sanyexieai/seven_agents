# -*- coding: utf-8 -*-
"""
商汤科技新闻分析示例
展示两个智能体通过A2A MCP和RAG技术实现从谷歌新闻搜索商汤科技新闻数据并生成财报

智能体分工：
1. 新闻收集智能体 (NewsCollectorAgent) - 负责搜索和收集新闻数据
2. 财报生成智能体 (ReportGeneratorAgent) - 负责分析数据并生成财报
"""

import os
import sys
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.base_agent import BaseAgent
from tools.mcp import WebSearchTool, FileOperationTool
from tools.rag_tools import RAGTool, Document
from tools.utility_tools import data_processor, file_utils, time_utils
from tools.mcp_tools import mcp_tool_manager


class NewsCollectorAgent(BaseAgent):
    """
    新闻收集智能体
    职责: 搜索商汤科技相关新闻，收集和预处理数据
    工具: 网络搜索、数据清理、RAG存储
    """
    
    def __init__(self, name: str = "新闻收集智能体", **kwargs):
        # 配置新闻收集智能体的特定设置
        collector_config = {
            'llm': kwargs.get('llm', {
                'model': 'gpt-3.5-turbo', 
                'temperature': 0.3,
                'max_tokens': 2000
            }),
            'memory_type': 'buffer',
            'verbose': kwargs.get('verbose', True),
            'system_prompt': """你是一个专业的新闻收集智能体。

你的职责是:
- 使用网络搜索工具搜索商汤科技相关的最新新闻
- 收集和整理新闻数据，包括标题、内容、来源、时间等
- 对新闻数据进行预处理和清理
- 将处理后的数据存储到RAG知识库中
- 与财报生成智能体协作，提供高质量的数据支持

搜索策略:
- 搜索关键词：商汤科技、SenseTime、AI技术、人工智能、计算机视觉
- 重点关注：公司动态、技术突破、市场表现、财务数据、合作伙伴
- 时间范围：最近3个月内的新闻
- 数据质量：优先选择权威媒体和官方发布的信息

请确保收集的数据准确、全面、及时。""",
            'tools': self._get_collector_tools()
        }
        
        super().__init__(name, **collector_config)
        
        # 初始化工具
        self.web_search_tool = WebSearchTool()
        self.file_tool = FileOperationTool()
        self.rag_tool = RAGTool()
        
        # 搜索配置
        self.search_keywords = [
            "商汤科技 最新消息",
            "SenseTime 新闻",
            "商汤科技 AI技术",
            "商汤科技 财报",
            "商汤科技 市场表现",
            "商汤科技 合作伙伴",
            "商汤科技 技术突破"
        ]
        
        self.logger.info(f"新闻收集智能体 '{name}' 初始化完成")
    
    def _get_collector_tools(self) -> List[Dict[str, Any]]:
        """获取收集工具配置"""
        return [
            {
                'type': 'function',
                'name': 'web_search',
                'description': '网络搜索工具'
            },
            {
                'type': 'function', 
                'name': 'file_operation',
                'description': '文件操作工具'
            },
            {
                'type': 'function',
                'name': 'rag_storage',
                'description': 'RAG存储工具'
            }
        ]
    
    def _get_agent_description(self) -> str:
        return "专业的新闻收集智能体，负责搜索和整理商汤科技相关新闻数据"
    
    async def collect_news(self, max_results_per_keyword: int = 5) -> Dict[str, Any]:
        """收集新闻数据"""
        self.logger.info("开始收集商汤科技相关新闻...")
        
        all_news = []
        collected_count = 0
        
        for keyword in self.search_keywords:
            try:
                self.logger.info(f"搜索关键词: {keyword}")
                
                # 替换原有的self.web_search_tool.execute调用为标准MCP调用
                search_result = mcp_tool_manager.execute_tool(
                    "web_search",
                    {
                        "query": keyword,
                        "max_results": max_results_per_keyword,
                        "search_engine": "google",
                        "search_type": "news",
                        "start_date": (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),
                        "end_date": datetime.now().strftime("%Y-%m-%d")
                    }
                )
                
                if search_result.get('results'):
                    for result in search_result['results']:
                        # 清理和预处理新闻数据
                        cleaned_news = self._clean_news_data(result, keyword)
                        if cleaned_news:
                            all_news.append(cleaned_news)
                            collected_count += 1
                
                # 避免请求过于频繁
                await asyncio.sleep(2)
                
            except Exception as e:
                self.logger.error(f"搜索关键词 '{keyword}' 失败: {e}")
                continue
        
        # 存储到RAG知识库
        if all_news:
            self._store_news_to_rag(all_news)
        
        result = {
            'success': True,
            'total_collected': collected_count,
            'news_data': all_news,
            'search_keywords': self.search_keywords,
            'collection_time': datetime.now().isoformat()
        }
        
        self.logger.info(f"新闻收集完成，共收集 {collected_count} 条新闻")
        return result
    
    def _clean_news_data(self, raw_news: Dict[str, Any], keyword: str) -> Optional[Dict[str, Any]]:
        """清理和预处理新闻数据"""
        try:
            # 提取基本信息（适配Google News格式）
            title = raw_news.get('title', '')
            snippet = raw_news.get('snippet', '')  # Google News返回的是snippet而不是content
            url = raw_news.get('url', '')
            source = raw_news.get('source', '')
            date = raw_news.get('date', '')
            
            # 数据验证
            if not title:
                return None
            
            # 清理文本内容
            cleaned_title = data_processor.clean_text(title)
            cleaned_snippet = data_processor.clean_text(snippet)
            
            # 生成摘要（如果没有snippet，使用标题）
            summary = cleaned_snippet if cleaned_snippet else cleaned_title
            
            # 提取关键信息
            extracted_info = {
                'emails': data_processor.extract_emails(cleaned_snippet),
                'urls': data_processor.extract_urls(cleaned_snippet),
                'word_count': data_processor.count_words(cleaned_snippet),
                'language': data_processor.detect_language(cleaned_snippet)
            }
            
            cleaned_news = {
                'title': cleaned_title,
                'content': cleaned_snippet,  # 使用snippet作为内容
                'summary': summary,
                'url': url,
                'source': source,
                'date': date,
                'keyword': keyword,
                'extracted_info': extracted_info,
                'collected_at': datetime.now().isoformat(),
                'news_id': f"news_{time_utils.get_current_timestamp()}_{len(cleaned_title)}"
            }
            
            return cleaned_news
            
        except Exception as e:
            self.logger.error(f"清理新闻数据失败: {e}")
            return None
    
    def _store_news_to_rag(self, news_list: List[Dict[str, Any]]):
        """将新闻数据存储到RAG知识库"""
        try:
            # 收集到news_list后，批量入库
            contents = [news['content'] for news in news_list]
            doc_metas = [news for news in news_list]  # 假设news本身就是元数据dict
            add_results = self.rag_tool.add_documents(contents, doc_metas)
            
            self.logger.info(f"成功将 {len(news_list)} 条新闻批量存储到RAG知识库")
            
        except Exception as e:
            self.logger.error(f"批量存储新闻到RAG知识库失败: {e}")
    
    def get_news_summary(self) -> Dict[str, Any]:
        """获取新闻收集摘要"""
        try:
            # 从RAG知识库搜索商汤科技相关新闻
            search_result = self.rag_tool.search_knowledge("商汤科技", top_k=10)
            
            summary = {
                'total_news': len(search_result.get('results', [])),
                'sources': list(set([r.get('doc_meta', {}).get('source', '') for r in search_result.get('results', [])])),
                'keywords_covered': list(set([r.get('doc_meta', {}).get('keyword', '') for r in search_result.get('results', [])])),
                'latest_news': search_result.get('results', [])[:3],
                'collection_stats': {
                    'total_documents': len(search_result.get('results', [])),
                    'avg_word_count': sum([r.get('doc_meta', {}).get('word_count', 0) for r in search_result.get('results', [])]) / max(len(search_result.get('results', [])), 1)
                }
            }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"获取新闻摘要失败: {e}")
            return {'error': str(e)}


class ReportGeneratorAgent(BaseAgent):
    """
    财报生成智能体
    职责: 分析新闻数据，生成商汤科技财报分析
    工具: RAG检索、数据分析、报告生成
    """
    
    def __init__(self, name: str = "财报生成智能体", **kwargs):
        # 配置财报生成智能体的特定设置
        generator_config = {
            'llm': kwargs.get('llm', {
                'model': 'gpt-4', 
                'temperature': 0.2,
                'max_tokens': 4000
            }),
            'memory_type': 'summary',
            'verbose': kwargs.get('verbose', True),
            'system_prompt': """你是一个专业的财报分析智能体。

你的职责是:
- 分析商汤科技的新闻数据，识别关键业务动态
- 评估公司的财务状况、市场表现和技术发展
- 生成专业的财报分析报告
- 提供投资建议和风险提示
- 确保报告的准确性和专业性

分析维度:
- 业务发展：新产品、技术突破、市场扩张
- 财务状况：收入、利润、现金流、债务
- 市场表现：股价、市值、投资者信心
- 竞争环境：行业地位、竞争对手、市场机会
- 风险因素：政策风险、技术风险、市场风险

报告结构:
1. 执行摘要
2. 公司概况
3. 业务分析
4. 财务分析
5. 市场分析
6. 风险评估
7. 投资建议
8. 附录

请基于收集的新闻数据生成专业、客观、全面的财报分析。""",
            'tools': self._get_generator_tools()
        }
        
        super().__init__(name, **generator_config)
        
        # 初始化工具
        self.rag_tool = RAGTool()
        self.file_tool = FileOperationTool()
        
        self.logger.info(f"财报生成智能体 '{name}' 初始化完成")
    
    def _get_generator_tools(self) -> List[Dict[str, Any]]:
        """获取生成工具配置"""
        return [
            {
                'type': 'function',
                'name': 'rag_search',
                'description': 'RAG知识库搜索工具'
            },
            {
                'type': 'function',
                'name': 'file_operation',
                'description': '文件操作工具'
            },
            {
                'type': 'function',
                'name': 'data_analysis',
                'description': '数据分析工具'
            }
        ]
    
    def _get_agent_description(self) -> str:
        return "专业的财报分析智能体，负责分析新闻数据并生成商汤科技财报报告"
    
    async def generate_report(self, report_type: str = "comprehensive") -> Dict[str, Any]:
        """生成财报分析报告"""
        self.logger.info(f"开始生成{report_type}财报分析报告...")
        
        try:
            # 1. 从RAG知识库检索相关新闻数据
            news_data = await self._retrieve_news_data()
            
            if not news_data:
                return {
                    'success': False,
                    'error': '未找到足够的新闻数据进行分析'
                }
            
            # 2. 分析新闻数据
            analysis_result = await self._analyze_news_data(news_data)
            
            # 3. 生成报告内容
            report_content = await self._generate_report_content(analysis_result, report_type)
            
            # 4. 保存报告到文件
            file_path = await self._save_report_to_file(report_content, report_type)
            
            result = {
                'success': True,
                'report_type': report_type,
                'file_path': file_path,
                'analysis_summary': analysis_result.get('summary', {}),
                'generated_at': datetime.now().isoformat(),
                'report_content': report_content
            }
            
            self.logger.info(f"财报分析报告生成完成: {file_path}")
            return result
            
        except Exception as e:
            self.logger.error(f"生成财报分析报告失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _retrieve_news_data(self) -> List[Dict[str, Any]]:
        """从RAG知识库检索新闻数据"""
        try:
            # 搜索商汤科技相关新闻
            search_result = self.rag_tool.search_knowledge("商汤科技", top_k=20)
            
            if not search_result.get('results'):
                return []
            
            # 按时间排序（最新的在前）
            news_list = search_result['results']
            news_list.sort(key=lambda x: x.get('doc_meta', {}).get('collected_at', ''), reverse=True)
            
            return news_list
            
        except Exception as e:
            self.logger.error(f"检索新闻数据失败: {e}")
            return []
    
    async def _analyze_news_data(self, news_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析新闻数据"""
        try:
            analysis = {
                'total_news': len(news_data),
                'time_range': self._get_time_range(news_data),
                'sources': self._analyze_sources(news_data),
                'topics': self._analyze_topics(news_data),
                'sentiment': self._analyze_sentiment(news_data),
                'key_events': self._extract_key_events(news_data),
                'summary': {}
            }
            
            # 生成分析摘要
            analysis['summary'] = {
                'business_highlights': self._extract_business_highlights(news_data),
                'financial_indicators': self._extract_financial_indicators(news_data),
                'market_performance': self._extract_market_performance(news_data),
                'risk_factors': self._extract_risk_factors(news_data)
            }
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"分析新闻数据失败: {e}")
            return {'error': str(e)}
    
    def _get_time_range(self, news_data: List[Dict[str, Any]]) -> Dict[str, str]:
        """获取新闻时间范围"""
        if not news_data:
            return {'start': '', 'end': ''}
        
        dates = [news.get('doc_meta', {}).get('collected_at', '') for news in news_data]
        dates = [d for d in dates if d]
        
        if dates:
            return {
                'start': min(dates),
                'end': max(dates)
            }
        return {'start': '', 'end': ''}
    
    def _analyze_sources(self, news_data: List[Dict[str, Any]]) -> Dict[str, int]:
        """分析新闻来源分布"""
        sources = {}
        for news in news_data:
            source = news.get('doc_meta', {}).get('source', '未知来源')
            sources[source] = sources.get(source, 0) + 1
        return sources
    
    def _analyze_topics(self, news_data: List[Dict[str, Any]]) -> Dict[str, int]:
        """分析新闻主题分布"""
        topics = {}
        for news in news_data:
            keyword = news.get('doc_meta', {}).get('keyword', '')
            topics[keyword] = topics.get(keyword, 0) + 1
        return topics
    
    def _analyze_sentiment(self, news_data: List[Dict[str, Any]]) -> Dict[str, int]:
        """分析新闻情感倾向（简化版）"""
        # 这里应该使用更复杂的情感分析模型
        positive_keywords = ['增长', '突破', '成功', '合作', '创新', '领先']
        negative_keywords = ['下跌', '亏损', '风险', '挑战', '竞争', '困难']
        
        sentiment = {'positive': 0, 'negative': 0, 'neutral': 0}
        
        for news in news_data:
            content = news.get('content', '').lower()
            positive_count = sum(1 for keyword in positive_keywords if keyword in content)
            negative_count = sum(1 for keyword in negative_keywords if keyword in content)
            
            if positive_count > negative_count:
                sentiment['positive'] += 1
            elif negative_count > positive_count:
                sentiment['negative'] += 1
            else:
                sentiment['neutral'] += 1
        
        return sentiment
    
    def _extract_key_events(self, news_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """提取关键事件"""
        key_events = []
        for news in news_data[:10]:  # 取前10条作为关键事件
            event = {
                'title': news.get('title', ''),
                'summary': news.get('summary', ''),
                'source': news.get('doc_meta', {}).get('source', ''),
                'date': news.get('doc_meta', {}).get('collected_at', ''),
                'url': news.get('url', '')
            }
            key_events.append(event)
        return key_events
    
    def _extract_business_highlights(self, news_data: List[Dict[str, Any]]) -> List[str]:
        """提取业务亮点"""
        highlights = []
        for news in news_data:
            title = news.get('title', '')
            content = news.get('content', '')
            
            # 简单的关键词匹配
            if any(keyword in title or keyword in content for keyword in ['合作', '签约', '发布', '推出', '突破']):
                highlights.append(news.get('summary', title))
        
        return highlights[:5]  # 返回前5个亮点
    
    def _extract_financial_indicators(self, news_data: List[Dict[str, Any]]) -> List[str]:
        """提取财务指标"""
        indicators = []
        for news in news_data:
            content = news.get('content', '')
            
            # 简单的财务关键词匹配
            if any(keyword in content for keyword in ['营收', '利润', '增长', '投资', '融资']):
                indicators.append(news.get('summary', news.get('title', '')))
        
        return indicators[:5]
    
    def _extract_market_performance(self, news_data: List[Dict[str, Any]]) -> List[str]:
        """提取市场表现"""
        performance = []
        for news in news_data:
            content = news.get('content', '')
            
            # 简单的市场关键词匹配
            if any(keyword in content for keyword in ['股价', '市值', '市场', '份额', '竞争']):
                performance.append(news.get('summary', news.get('title', '')))
        
        return performance[:5]
    
    def _extract_risk_factors(self, news_data: List[Dict[str, Any]]) -> List[str]:
        """提取风险因素"""
        risks = []
        for news in news_data:
            content = news.get('content', '')
            
            # 简单的风险关键词匹配
            if any(keyword in content for keyword in ['风险', '挑战', '困难', '问题', '监管']):
                risks.append(news.get('summary', news.get('title', '')))
        
        return risks[:5]
    
    async def _generate_report_content(self, analysis_result: Dict[str, Any], report_type: str) -> str:
        """生成报告内容"""
        try:
            # 构建报告模板
            report_template = f"""
# 商汤科技财报分析报告

**报告类型**: {report_type}分析报告  
**生成时间**: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}  
**数据来源**: 新闻数据挖掘与分析  
**分析周期**: {analysis_result.get('time_range', {}).get('start', '')} 至 {analysis_result.get('time_range', {}).get('end', '')}

## 执行摘要

本报告基于对商汤科技相关新闻数据的深度分析，从业务发展、财务状况、市场表现等多个维度对公司进行全面评估。

**关键发现**:
- 共分析 {analysis_result.get('total_news', 0)} 条相关新闻
- 覆盖 {len(analysis_result.get('sources', {}))} 个新闻来源
- 识别 {len(analysis_result.get('key_events', []))} 个关键事件

## 1. 公司概况

商汤科技（SenseTime）是全球领先的人工智能公司，专注于计算机视觉和深度学习技术。

## 2. 业务分析

### 2.1 业务亮点
{self._format_list(analysis_result.get('summary', {}).get('business_highlights', []))}

### 2.2 技术发展
基于新闻数据分析，商汤科技在以下技术领域表现突出：
- 计算机视觉技术
- 深度学习算法
- AI芯片研发
- 行业解决方案

## 3. 财务分析

### 3.1 财务指标
{self._format_list(analysis_result.get('summary', {}).get('financial_indicators', []))}

### 3.2 财务表现评估
基于新闻数据分析，公司财务状况总体稳健，但需要关注以下方面：
- 收入增长趋势
- 盈利能力变化
- 现金流状况
- 投资活动

## 4. 市场分析

### 4.1 市场表现
{self._format_list(analysis_result.get('summary', {}).get('market_performance', []))}

### 4.2 竞争环境
- 行业地位：AI领域领先企业
- 主要竞争对手：百度、腾讯、阿里巴巴等
- 市场机会：数字化转型、AI+行业应用

## 5. 风险评估

### 5.1 主要风险因素
{self._format_list(analysis_result.get('summary', {}).get('risk_factors', []))}

### 5.2 风险等级评估
- 技术风险：中等
- 市场风险：中等
- 政策风险：中等
- 竞争风险：高

## 6. 投资建议

### 6.1 投资评级
基于新闻数据分析，建议投资评级：**谨慎乐观**

### 6.2 投资理由
- 技术实力强，在AI领域具有领先优势
- 业务布局全面，覆盖多个行业应用
- 合作伙伴众多，生态体系完善

### 6.3 风险提示
- 行业竞争激烈，需要持续技术创新
- 政策环境变化可能影响业务发展
- 盈利能力需要进一步改善

## 7. 附录

### 7.1 关键事件时间线
{self._format_events(analysis_result.get('key_events', []))}

### 7.2 新闻来源分布
{self._format_sources(analysis_result.get('sources', {}))}

### 7.3 情感分析结果
{self._format_sentiment(analysis_result.get('sentiment', {}))}

---

**免责声明**: 本报告基于公开新闻数据生成，仅供参考，不构成投资建议。投资有风险，决策需谨慎。
"""
            
            return report_template
            
        except Exception as e:
            self.logger.error(f"生成报告内容失败: {e}")
            return f"报告生成失败: {str(e)}"
    
    def _format_list(self, items: List[str]) -> str:
        """格式化列表"""
        if not items:
            return "- 暂无相关数据"
        return "\n".join([f"- {item}" for item in items])
    
    def _format_events(self, events: List[Dict[str, Any]]) -> str:
        """格式化事件列表"""
        if not events:
            return "- 暂无关键事件"
        
        formatted = []
        for i, event in enumerate(events, 1):
            formatted.append(f"{i}. **{event.get('title', '')}**")
            formatted.append(f"   - 时间: {event.get('date', '')}")
            formatted.append(f"   - 来源: {event.get('source', '')}")
            formatted.append(f"   - 摘要: {event.get('summary', '')}")
            formatted.append("")
        
        return "\n".join(formatted)
    
    def _format_sources(self, sources: Dict[str, int]) -> str:
        """格式化来源分布"""
        if not sources:
            return "- 暂无来源数据"
        
        formatted = []
        for source, count in sorted(sources.items(), key=lambda x: x[1], reverse=True):
            formatted.append(f"- {source}: {count} 条新闻")
        
        return "\n".join(formatted)
    
    def _format_sentiment(self, sentiment: Dict[str, int]) -> str:
        """格式化情感分析"""
        total = sum(sentiment.values())
        if total == 0:
            return "- 暂无情感分析数据"
        
        formatted = []
        for key, value in sentiment.items():
            percentage = (value / total) * 100
            formatted.append(f"- {key}: {value} 条 ({percentage:.1f}%)")
        
        return "\n".join(formatted)
    
    async def _save_report_to_file(self, report_content: str, report_type: str) -> str:
        """保存报告到文件"""
        try:
            # 创建报告目录
            report_dir = "reports"
            file_utils.ensure_directory(report_dir)
            
            # 生成文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"shangtang_report_{report_type}_{timestamp}.md"
            file_path = os.path.join(report_dir, filename)
            
            # 保存文件
            success = file_utils.write_file_safe(file_path, report_content, encoding='utf-8')
            
            if success:
                self.logger.info(f"报告已保存到: {file_path}")
                return file_path
            else:
                raise Exception("文件保存失败")
                
        except Exception as e:
            self.logger.error(f"保存报告文件失败: {e}")
            raise e


class A2ACommunication:
    """
    A2A通信管理器
    负责两个智能体之间的通信和协作
    """
    
    def __init__(self):
        self.news_collector = NewsCollectorAgent()
        self.report_generator = ReportGeneratorAgent()
        self.communication_log = []
    
    async def execute_full_workflow(self) -> Dict[str, Any]:
        """执行完整的工作流程"""
        print("🚀 开始商汤科技新闻分析工作流程...")
        
        try:
            # 1. 新闻收集阶段
            print("\n📰 第一阶段：新闻数据收集")
            collection_result = await self.news_collector.collect_news(max_results_per_keyword=5)
            
            if not collection_result.get('success'):
                return {
                    'success': False,
                    'error': f"新闻收集失败: {collection_result.get('error', '未知错误')}"
                }
            
            print(f"✅ 新闻收集完成，共收集 {collection_result.get('total_collected', 0)} 条新闻")
            
            # 2. 数据传递和验证
            print("\n📊 第二阶段：数据验证和准备")
            news_summary = self.news_collector.get_news_summary()
            print(f"📈 数据摘要: {news_summary.get('total_news', 0)} 条新闻，{len(news_summary.get('sources', []))} 个来源")
            
            # 3. 财报生成阶段
            print("\n📋 第三阶段：财报分析生成")
            report_result = await self.report_generator.generate_report(report_type="comprehensive")
            
            if not report_result.get('success'):
                return {
                    'success': False,
                    'error': f"财报生成失败: {report_result.get('error', '未知错误')}"
                }
            
            print(f"✅ 财报生成完成: {report_result.get('file_path', '')}")
            
            # 4. 生成最终结果
            final_result = {
                'success': True,
                'workflow_completed': True,
                'collection_result': collection_result,
                'report_result': report_result,
                'news_summary': news_summary,
                'completed_at': datetime.now().isoformat(),
                'total_duration': '工作流程执行完成'
            }
            
            print("\n🎉 工作流程执行完成！")
            print(f"📄 报告文件: {report_result.get('file_path', '')}")
            
            return final_result
            
        except Exception as e:
            error_msg = f"工作流程执行失败: {str(e)}"
            print(f"❌ {error_msg}")
            return {
                'success': False,
                'error': error_msg
            }


async def main():
    """主函数"""
    print("🤖 商汤科技新闻分析示例")
    print("=" * 50)
    
    # 创建A2A通信管理器
    a2a_manager = A2ACommunication()
    
    # 执行完整工作流程
    result = await a2a_manager.execute_full_workflow()
    
    # 输出结果摘要
    print("\n" + "=" * 50)
    print("📊 执行结果摘要")
    print("=" * 50)
    
    if result.get('success'):
        print("✅ 工作流程执行成功")
        print(f"📰 收集新闻: {result.get('collection_result', {}).get('total_collected', 0)} 条")
        print(f"📄 生成报告: {result.get('report_result', {}).get('file_path', '')}")
        print(f"⏰ 完成时间: {result.get('completed_at', '')}")
    else:
        print("❌ 工作流程执行失败")
        print(f"错误信息: {result.get('error', '未知错误')}")
    
    print("\n" + "=" * 50)
    print("示例执行完成！")


if __name__ == "__main__":
    # 运行示例
    asyncio.run(main()) 