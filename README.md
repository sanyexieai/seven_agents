# Seven Agents - 多智能体系统

基于LangChain的多智能体企业级应用示例，集成MCP、RAG、自动调度、工具链、向量数据库等最佳实践。

## 项目概述

本项目实现了多智能体协作框架，支持：
- 智能体注册与自动发现
- 智能体调度与自动调用
- MCP工具链配置化/自动化集成
- RAG数据库化与向量存储
- 多场景提示词模板管理
- LLM驱动参数补全与工具自动调用

### 典型智能体角色

1. **调度智能体 (AgentCoordinatorAgent)** - 负责全局智能体发现、选择与自动分配/调用
2. **工具智能体 (ToolAgent)** - 自动选择并调用MCP工具，支持schema驱动参数补全
3. **基础智能体 (BaseAgent)** - 支持LLM、记忆、工具链、提示词等通用能力
4. 其它可扩展智能体（如分析、研究、通信、执行、监控等）

## 技术特性

- **MCP (Model Context Protocol)**: 工具链能力即配置，支持本地/远程工具热插拔
- **RAG数据库化**: pgvector向量存储，ORM自动建表，embedding可配置
- **多智能体注册/调度**: 统一注册表，自动发现、分配、调用
- **多场景提示词模板**: 每个智能体/场景独立模板，支持多文件结构
- **LLM参数补全**: schema驱动+LLM自动补全+自动调用闭环
- **配置化/自动化**: 所有能力均支持json配置和自动注册，无需硬编码

## 项目结构
seven_agents/
├── README.md
├── requirements.txt
├── main.py
├── config/
│   ├── settings.py
│   └── ...
├── agents/
│   ├── base_agent.py         # 基础智能体类（自动注册）
│   ├── tool_agent.py         # 工具智能体（自动注册）
│   ├── agent_coordinator.py  # 调度智能体（自动注册）
│   ├── utils/
│   │   ├── register.py       # 智能体注册/发现机制
│   │   └── ...
│   └── prompt/
│       ├── base_agent/
│       │   └── system.txt
│       ├── tool_agent/
│       │   └── tool_select.txt
│       └── agent_coordinator/
│           ├── agent_list.txt
│           └── agent_select.txt
├── tools/
│   ├── mcp_tools.py
│   └── mcp/
│       ├── base.py
│       ├── api_call.py
│       ├── file_operation.py
│       └── google_news_search.py
├── database/
│   └── ...
├── examples/
│   ├── agent_coordinator_example.py # 调度智能体自动分配/调用示例
│   └── ...
└── ...

## 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 配置环境变量
详见 `.env` 示例。

### 3. 运行多智能体调度示例
```bash
python examples/agent_coordinator_example.py
```

## 多智能体注册与自动调度

- 所有智能体类用 `@register_agent` 装饰器自动注册到全局注册表
- 调度智能体可自动发现所有已注册智能体及其描述
- 支持 LLM 自动选择/分配/参数补全/自动调用目标智能体
- 支持多场景提示词模板，结构清晰、易扩展

## MCP工具链与RAG数据库化

- 所有MCP工具通过json配置自动注册，支持本地/远程/热插拔
- 工具schema/描述自动获取，LLM可智能参数补全
- RAG相关表自动建表，pgvector向量存储，embedding可配置

## 提示词模板管理

- 每个智能体/场景独立模板，存放于 `agents/prompt/智能体名/模板名.txt`
- 支持多场景、多轮对话、多任务提示词灵活扩展

## 典型用法

### 1. 注册与调度
```python
from agents.agent_coordinator import AgentCoordinatorAgent
coordinator = AgentCoordinatorAgent(name="调度智能体")
result = coordinator.select_and_call_agent("以商汤科技为关键词，搜索相关新闻")
print(result)
```

### 2. 工具智能体自动参数补全与调用
```python
from agents.tool_agent import ToolAgent
agent = ToolAgent(name="工具智能体")
result = agent.select_and_call_tool("以商汤科技为关键词，搜索相关新闻")
print(result)
```

## 许可证
MIT License