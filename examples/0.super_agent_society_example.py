import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.meta_agent import MetaAgent
from agents.task_incubator import TaskIncubator
from agents.orchestrator import Orchestrator
from agents.guilds.data_crawl_guild import DataCrawlGuild
from agents.guilds.knowledge_guild import KnowledgeGuild
from agents.guilds.chart_guild import ChartGuild
from agents.guilds.finance_guild import FinanceGuild
from agents.guilds.industry_guild import IndustryGuild
from agents.guilds.audit_guild import AuditGuild
from agents.guilds.report_guild import ReportGuild

if __name__ == "__main__":
    # 1. 初始化元治理智能体
    meta = MetaAgent(auto_register_all=True)
    # 3. 注册各 Guild/Agent，全部传入 meta
    meta.register("DataCrawlGuild", DataCrawlGuild(meta))
    meta.register("KnowledgeGuild", KnowledgeGuild(meta))
    meta.register("ChartGuild", ChartGuild(meta))
    meta.register("FinanceGuild", FinanceGuild(meta))
    meta.register("IndustryGuild", IndustryGuild(meta))
    meta.register("AuditGuild", AuditGuild(meta))
    meta.register("ReportGuild", ReportGuild(meta))

    # 4. 初始化 TaskIncubator 和 Orchestrator
    incubator = TaskIncubator(meta)
    orchestrator = Orchestrator(meta)
    meta.register("TaskIncubator", incubator)
    meta.register("Orchestrator", orchestrator)

    # 5. 用户输入
    user_input = "以商汤科技为关键词，搜索相关新闻,整理一份研报，并生成图表，以markdown格式保存到output目录下，不需要操作数据库"
    print(f"用户输入: {user_input}")

    # 6. 任务孵化
    task_blueprint = incubator.incubate(user_input, meta)
    print(f"任务蓝图: {task_blueprint}")

    # 7. 调度分发
    result = orchestrator.dispatch(task_blueprint)
    print("最终结果：", result) 