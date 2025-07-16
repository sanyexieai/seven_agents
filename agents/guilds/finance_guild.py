from agents.utils.register import register_agent
from agents.base_agent import BaseAgent

@register_agent
class FinanceGuild(BaseAgent):
    def __init__(self, meta_agent):
        super().__init__(name="FinanceGuild")
        self.meta_agent = meta_agent

    def _get_agent_description(self):
        return "负责财务报表分析、比率分析、估值建模等任务，具备多渠道整合与来源可靠性评估能力。"

    def handle_task(self, params):
        tool_collective = self.meta_agent.get_tool_collective()
        all_tools = self.meta_agent.get_all_tools()
        # 可通过 self.meta_agent.context 访问全局上下文
        candidate_tools = [t for t in all_tools if any(kw in t.get("description", "") for kw in ["财务", "报表", "估值", "比率", "分析", "finance", "valuation"])]
        results = []
        for tool in candidate_tools:
            try:
                data = tool_collective.handle_tool_request({"目标": params.get("目标", "财务分析"), **params, "tool": tool["name"]})
                reliability = self.evaluate_source_reliability(tool["name"], tool.get("description", ""))
                results.append({"data": data, "source": tool["name"], "reliability": reliability})
            except Exception as e:
                results.append({"data": None, "source": tool["name"], "reliability": 0, "error": str(e)})
        unique = {}
        for r in results:
            key = str(r["data"])
            if key not in unique or r["reliability"] > unique[key]["reliability"]:
                unique[key] = r
        sorted_results = sorted(unique.values(), key=lambda x: x["reliability"], reverse=True)
        return sorted_results

    def evaluate_source_reliability(self, source_name, description):
        if any(kw in source_name+description for kw in ["官方", "authority", "政府", "证监会", "交易所"]):
            return 0.95
        elif any(kw in source_name+description for kw in ["主流", "mainstream", "wind", "同花顺", "东方财富"]):
            return 0.85
        elif any(kw in source_name+description for kw in ["自媒体", "博客", "论坛", "贴吧"]):
            return 0.6
        else:
            return 0.7 