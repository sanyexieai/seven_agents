# Seven Agents - 多智能体系统

基于LangChain的多智能体示例项目，集成MCP、A2A、工具调用、RAG等技术。

## 项目概述

本项目实现了七个专业智能体，每个智能体都有特定的职责：

1. **协调者智能体** (Coordinator Agent) - 负责整体任务协调和分配
2. **研究智能体** (Research Agent) - 负责信息检索和RAG操作
3. **分析智能体** (Analysis Agent) - 负责数据分析和处理
4. **工具智能体** (Tool Agent) - 负责工具调用和MCP集成
5. **通信智能体** (Communication Agent) - 负责A2A通信协议
6. **执行智能体** (Execution Agent) - 负责具体任务执行
7. **监控智能体** (Monitor Agent) - 负责系统监控和日志

## 技术特性

- **MCP (Model Context Protocol)**: 模型上下文协议，支持工具调用
- **A2A (Agent-to-Agent)**: 智能体间通信协议
- **RAG (Retrieval-Augmented Generation)**: 检索增强生成
- **向量数据库**: 知识存储和检索
- **异步处理**: 支持并发任务执行
- **可扩展架构**: 模块化设计，易于扩展

## 项目结构
seven_agents/
├── README.md # 项目说明
├── requirements.txt # 依赖包
├── main.py # 主入口文件
├── config/ # 配置文件
│ ├── init.py
│ ├── settings.py # 全局设置
│ └── agents_config.py # 智能体配置
├── agents/ # 智能体模块
│ ├── init.py
│ ├── base_agent.py # 基础智能体类
│ ├── coordinator_agent.py # 协调者智能体
│ ├── research_agent.py # 研究智能体
│ ├── analysis_agent.py # 分析智能体
│ ├── tool_agent.py # 工具智能体
│ ├── communication_agent.py # 通信智能体
│ ├── execution_agent.py # 执行智能体
│ └── monitor_agent.py # 监控智能体
├── tools/ # 工具模块
│ ├── init.py
│ ├── mcp_tools.py # MCP工具
│ ├── rag_tools.py # RAG工具
│ └── utility_tools.py # 通用工具
├── memory/ # 记忆模块
│ ├── init.py
│ ├── conversation_memory.py # 对话记忆
│ └── vector_store.py # 向量存储
├── communication/ # 通信模块
│ ├── init.py
│ ├── a2a_protocol.py # A2A协议
│ └── message_bus.py # 消息总线
├── examples/ # 示例代码
│ ├── init.py
│ ├── basic_example.py # 基础示例
│ ├── rag_example.py # RAG示例
│ └── tool_calling_example.py # 工具调用示例
├── data/ # 数据目录
│ ├── documents/ # 文档存储
│ └── vector_db/ # 向量数据库
└── logs/ # 日志目录

## 安装和设置

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 环境配置
创建 `.env` 文件：
```env
OPENAI_API_KEY=your_openai_api_key
OPENAI_BASE_URL=https://api.openai.com/v1
VECTOR_DB_PATH=./data/vector_db
LOG_LEVEL=INFO
```

### 3. 运行项目
```bash
python main.py
```

## 使用示例

### 基础使用
```python
from agents import AgentOrchestrator

# 创建智能体编排器
orchestrator = AgentOrchestrator()

# 执行任务
result = orchestrator.execute_task("分析最新的AI技术趋势")
print(result)
```

## 智能体详细说明

### 1. 协调者智能体
- **职责**: 任务分解、智能体选择、结果整合
- **工具**: 任务分解器、智能体选择器
- **特点**: 全局视角，决策能力强

### 2. 研究智能体
- **职责**: 信息检索、文档处理、知识库构建
- **工具**: 网络搜索、文档加载器、向量搜索
- **特点**: 信息收集专家，RAG核心

### 3. 分析智能体
- **职责**: 数据分析、模式识别、洞察生成
- **工具**: 数据分析器、图表生成器、统计工具
- **特点**: 数据处理能力强，洞察深刻

### 4. 工具智能体
- **职责**: 工具调用、MCP集成、外部API交互
- **工具**: MCP客户端、API调用器、工具管理器
- **特点**: 工具集成专家，扩展性强

### 5. 通信智能体
- **职责**: 智能体间通信、消息路由、协议管理
- **工具**: 消息总线、协议处理器、状态同步器
- **特点**: 通信协议专家，协调能力强

### 6. 执行智能体
- **职责**: 任务执行、结果验证、错误处理
- **工具**: 任务执行器、结果验证器、错误处理器
- **特点**: 执行效率高，可靠性强

### 7. 监控智能体
- **职责**: 系统监控、性能分析、日志管理
- **工具**: 监控器、性能分析器、日志管理器
- **特点**: 系统监控专家，问题诊断能力强

## 许可证

MIT License