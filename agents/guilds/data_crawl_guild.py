from agents.utils.register import register_agent
from agents.base_agent import BaseAgent

@register_agent
class DataCrawlGuild(BaseAgent):
    def __init__(self, meta_agent):
        super().__init__(name="DataCrawlGuild")
        self.meta_agent = meta_agent

    def _get_agent_description(self):
        return "负责新闻、财报等数据抓取任务，具备多渠道数据整合与来源可靠性评估能力。"

    def handle_task(self, params):
        tool_collective = self.meta_agent.get_tool_collective()
        all_tools = self.meta_agent.get_all_tools()
        # 可通过 self.meta_agent.context 访问全局上下文
        # 1. 专家式思考：筛选所有可用于数据抓取的工具
        candidate_tools = [t for t in all_tools if any(kw in t.get("description", "") for kw in ["新闻", "数据抓取", "资讯", "爬虫", "财报"])]
        results = []
        for tool in candidate_tools:
            # 2. 多渠道抓取
            try:
                data = tool_collective.handle_tool_request({"目标": params.get("目标", "抓取数据"), **params, "tool": tool["name"]})
                reliability = self.evaluate_source_reliability(tool["name"], tool.get("description", ""))
                results.append({"data": data, "source": tool["name"], "reliability": reliability})
            except Exception as e:
                results.append({"data": None, "source": tool["name"], "reliability": 0, "error": str(e)})
        # 3. 聚合与去重（简单去重）
        unique = {}
        for r in results:
            key = str(r["data"])
            if key not in unique or r["reliability"] > unique[key]["reliability"]:
                unique[key] = r
        # 4. 按可靠性排序
        sorted_results = sorted(unique.values(), key=lambda x: x["reliability"], reverse=True)
        return sorted_results

    def evaluate_source_reliability(self, source_name, description):
        # 简单示例：官方>主流媒体>自媒体
        if any(kw in source_name+description for kw in ["官方", "authority", "政府", "证券所"]):
            return 0.95
        elif any(kw in source_name+description for kw in ["主流", "mainstream", "新华", "央视", "路透", "彭博", "新浪", "腾讯", "网易"]):
            return 0.85
        elif any(kw in source_name+description for kw in ["自媒体", "博客", "论坛", "贴吧"]):
            return 0.6
        else:
            return 0.7 