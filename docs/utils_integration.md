# 工具集成说明

本文档介绍了从其他项目集成的工具模块及其使用方法。

## 集成的工具

### 1. LLMHelper - LangChain集成的LLM调用工具

**功能**: 继承LangChain LLM类，提供统一的LLM调用接口，支持同步和异步调用，具有日志记录和备用API切换功能。

**主要特性**:
- 完全兼容LangChain生态系统
- 同步和异步调用支持
- 自动日志记录
- 备用API自动切换
- YAML响应解析
- 错误重试机制
- 支持LangChain的所有功能（记忆、工具、链等）

**使用示例**:
```python
from agents.utils.llm_helper import LLMHelper
from config.llm_config import LLMConfig

# 创建配置
config = LLMConfig(
    api_key="your-api-key",
    model="gpt-3.5-turbo",
    max_tokens=1000,
    temperature=0.7
)

# 创建LLMHelper实例（现在是LangChain LLM）
llm = LLMHelper(config)

# 同步调用
response = llm.call("你好，请介绍一下自己")

# 异步调用
response = await llm.async_call("异步调用示例")

# 解析YAML响应
parsed_data = llm.parse_yaml_response(yaml_response)

# 在LangChain链中使用
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

prompt = PromptTemplate.from_template("回答: {question}")
chain = LLMChain(llm=llm, prompt=prompt)
result = chain.run("什么是人工智能？")
```

### 2. AsyncFallbackOpenAIClient - 备用API客户端

**功能**: 支持主备API自动切换的异步OpenAI客户端，当主API失败时自动切换到备用API。

**主要特性**:
- 主备API自动切换
- 内容过滤错误处理
- 可配置重试机制
- 网络错误自动重试

**使用示例**:
```python
from agents.utils.fallback_openai_client import AsyncFallbackOpenAIClient

client = AsyncFallbackOpenAIClient(
    primary_api_key="primary-key",
    primary_base_url="https://api.openai.com/v1",
    primary_model_name="gpt-3.5-turbo",
    fallback_api_key="fallback-key",
    fallback_base_url="https://api.anthropic.com/v1",
    fallback_model_name="claude-3-sonnet-20240229"
)

response = await client.chat_completions_create(
    messages=[{"role": "user", "content": "Hello"}]
)
```

### 3. CodeExecutor - 安全代码执行器

**功能**: 基于IPython的安全代码执行器，支持数据分析环境，具有输出捕获和格式化功能。

**主要特性**:
- 安全的代码执行环境
- 支持pandas、numpy、matplotlib等库
- 输出捕获和格式化
- 图片自动保存
- 中文字体支持

**使用示例**:
```python
from agents.utils.code_executor import CodeExecutor

executor = CodeExecutor(output_dir="outputs")

# 执行代码
result = executor.execute_code("""
import pandas as pd
import matplotlib.pyplot as plt

data = pd.DataFrame({'x': [1, 2, 3], 'y': [4, 5, 6]})
plt.plot(data['x'], data['y'])
plt.title('测试图表')
plt.savefig('test.png')
""")

print(result['success'])  # 是否执行成功
print(result['output'])   # 输出内容
print(result['error'])    # 错误信息
```

### 4. 数据分析智能体 (DataAnalysisAgent)

**功能**: 集成CodeExecutor的数据分析智能体，支持自动代码生成和执行。

**主要特性**:
- 自动生成分析代码
- 安全代码执行
- 结果保存和管理
- 会话隔离
- 分析历史记录

**使用示例**:
```python
from agents.data_analysis_agent import DataAnalysisAgent

# 创建数据分析智能体
agent = DataAnalysisAgent(
    name="数据分析助手",
    output_dir="analysis_outputs"
)

# 设置数据文件
agent.set_data_file("data.csv")

# 执行分析
result = agent.analyze_data(
    "请对数据进行基础统计分析，包括均值、标准差等"
)

if result['success']:
    print(result['formatted_result'])
    print(f"结果保存在: {result['session_dir']}")
```

### 5. 辅助工具

#### extract_code - 代码提取工具
从LLM响应中提取代码块，支持YAML和markdown格式。

#### format_execution_result - 结果格式化工具
将代码执行结果格式化为用户友好的反馈。

#### create_session_dir - 会话目录创建工具
为每次分析创建独立的输出目录。

## 配置说明

### LLM配置 (config/llm_config.py)

```python
from config.llm_config import LLMConfig

# 从应用设置创建配置（从.env读取）
config = LLMConfig.from_settings()

# 创建OpenAI配置
config = LLMConfig.create_openai_config("your-api-key", "gpt-4")

# 创建Anthropic配置
config = LLMConfig.create_anthropic_config("your-api-key", "claude-3-sonnet-20240229")
```

### 智能体配置方式

#### 1. 默认配置（从.env读取）
```python
from agents.base_agent import BaseAgent

# 不传任何配置，使用默认配置
agent = BaseAgent("默认智能体")
```

#### 2. 自定义LLM参数
```python
# 传入自定义参数，覆盖默认值
agent = BaseAgent(
    "自定义智能体",
    llm={
        'model': 'gpt-4',
        'temperature': 0.3,
        'max_tokens': 500
    }
)
```

#### 3. 完全自定义LLM配置
```python
from config.llm_config import LLMConfig

# 创建完全自定义的配置
custom_config = LLMConfig(
    api_key="your-api-key",
    model="gpt-4",
    temperature=0.5,
    max_tokens=800
)

# 传入自定义配置
agent = BaseAgent(
    "自定义配置智能体",
    llm_config=custom_config
)
```

### 环境变量

```bash
# OpenAI配置
OPENAI_API_KEY=your-openai-api-key
OPENAI_BASE_URL=https://api.openai.com/v1
DEFAULT_LLM_MODEL=gpt-3.5-turbo
DEFAULT_LLM_TEMPERATURE=0.7
DEFAULT_LLM_MAX_TOKENS=1000

# Anthropic配置（备用）
ANTHROPIC_API_KEY=your-anthropic-api-key
ANTHROPIC_BASE_URL=https://api.anthropic.com/v1
ANTHROPIC_MODEL=claude-3-sonnet-20240229

# 重试配置
LLM_MAX_RETRIES_PRIMARY=1
LLM_MAX_RETRIES_FALLBACK=1
LLM_RETRY_DELAY_SECONDS=1.0

# 内容过滤配置
LLM_CONTENT_FILTER_ERROR_CODE=1301
LLM_CONTENT_FILTER_ERROR_FIELD=contentFilter
```

## 运行示例

### 数据分析示例
```bash
python examples/data_analysis_example.py
```

### LLMHelper示例
```bash
python examples/llm_helper_example.py
```

### LLM配置示例
```bash
python examples/llm_config_example.py
```

## 依赖安装

```bash
pip install -r requirements.txt
```

新增的依赖包括：
- `ipython>=8.0.0` - 代码执行环境
- `duckdb>=0.9.0` - 数据分析数据库
- `plotly>=5.15.0` - 交互式图表
- `dash>=2.14.0` - Web应用框架
- `nest-asyncio>=1.5.0` - 异步支持

## 注意事项

1. **安全性**: CodeExecutor限制了可导入的库，确保代码执行安全
2. **API密钥**: 请确保正确设置API密钥环境变量
3. **输出目录**: 代码执行结果会保存在指定的输出目录中
4. **会话隔离**: 每次分析都会创建独立的会话目录
5. **错误处理**: 所有工具都包含完善的错误处理机制

## 扩展开发

### 添加新的代码执行库
在 `CodeExecutor.ALLOWED_IMPORTS` 中添加新的库名。

### 自定义LLM配置
继承 `LLMConfig` 类创建自定义配置。

### 扩展数据分析功能
继承 `DataAnalysisAgent` 类添加新的分析功能。 