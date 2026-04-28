\[TOC]

# 参考文档{#Ref}

\[LangChain中文文档]\([LangChain 中文教程 | LangChain 中文文档](https://langchain-doc.cn/))

\[智谱LangChain集成]\([LangChain 集成 - 智谱AI开放文档](https://docs.bigmodel.cn/cn/guide/develop/langchain/introduction#langchain))

注: 本项目基于LangChain v1.0 构建, LangChain v1.0 中许多旧版api被弃用, 而智谱官方文档的例子还停留在v.03的版本, 本文已经默认修改为v1.0版能运行的代码.

# 安装{#Installation}

uv: 超高速 Python 包管理器, 比anaconda/ pip轻量级, 快速. 添加包的命令只需要把`pip install` 换成 `uv add`. 注意vscode中要选择解释器和包管理器, 两者都要匹配

在以下两种方式中选一种安装, 本项目使用uv

```bash
# anaconda/pip
pip install -U langchain
```

```bash
# uv,在项目目录下
uv init
uv add langchain
```

# 智能体{#Agent}

包含以下核心组件: 模型, 工具, 系统提示词. 在介绍完这些组件之后, 本章会演示智能体调用以及介绍一些高级概念.

## 模型{#model}

示例用免费的智谱, 首先在[智谱官网](https://open.bigmodel.cn/)获取API KEY, 然后在环境中安装langchain集成依赖

**完整安装**

```bash
# 一次性安装所有相关包
uv add langchain langchain-openai langchainhub httpx_sse

# 验证安装
python -c "import langchain; print(langchain.__version__)"
```

**创建大模型实例**

创建大模型实例需要填写api key, 支持在代码中直接输入, 也可以读取环境变量. 这里展示读取环境变量的方式.

安装python-dotenv, 用于读取环境变量

```bash
uv add python-dotenv
```

然后在项目的.env文件夹下填写获得的api key.

注意把.env文件添加到gitignore中, 避免提交到版本控制.

```bash
ZAI_API_KEY={your api key}
```

在主程序中读取环境变量, 创建大模型实例

```python
from dotenv import load_dotenv  # 关键：加载.env
from langchain_openai import ChatOpenAI
import os

# 加载环境变量
load_dotenv()

model = ChatOpenAI(
    temperature=0.6,
    model="glm-4.7-flash",
    openai_api_key=os.getenv("ZAI_API_KEY"),
    openai_api_base="https://open.bigmodel.cn/api/paas/v4/"
    )
```

以上是创建静态模型的方法. 静态模型在创建智能体时配置一次，并在整个执行过程中保持不变。这是最常见且直接的方法。

如果要创建动态模型, 请使用 [`@wrap_model_call`](https://reference.langchain.com/python/langchain/middleware/#langchain.agents.middleware.wrap_model_call) 装饰器创建中间件. 本项目暂时没有使用动态模型.

**简单对话**

```python
from langchain_openai import ChatOpenAI

from langchain_core.messages import HumanMessage, SystemMessage

# 创建 LLM 实例
model = ChatOpenAI(
    temperature=0.7,
    model="glm-5",
    openai_api_key="your-zhipuai-api-key",
    openai_api_base="https://open.bigmodel.cn/api/paas/v4/"
)

# 创建消息
messages = [
    SystemMessage(content="你是一个有用的 AI 助手"),
    HumanMessage(content="请介绍一下人工智能的发展历程")
]

# 调用模型
response = model.invoke(messages)
print(response.content)
```

## 工具{#tool}

工具赋予智能体执行行动的能力。智能体超越了简单的仅模型工具绑定，实现了：

- 序列中的多个工具调用（由单个提示触发）
- 适当的并行工具调用
- 基于先前结果的动态工具选择
- 工具重试逻辑和错误处理
- 工具调用之间的状态持久化

**定义工具**

```python
from langchain.tools import tool
from langchain.agents import create_agent


@tool
def search(query: str) -> str:
    """搜索信息。"""
    return f"结果：{query}"

@tool
def get_weather(location: str) -> str:
    """获取位置的天气信息。"""
    return f"{location} 的天气：晴朗，72°F"

agent = create_agent(model, tools=[search, get_weather])
```

**工具错误处理**

要自定义工具错误的处理方式，请使用 [`@wrap_tool_call`](https://reference.langchain.com/python/langchain/middleware/#langchain.agents.middleware.wrap_tool_call) 装饰器创建中间件. 略

**ReAct循环中的工具使用**

智能体遵循 ReAct（“推理 + 行动”）模式，在简短的推理步骤与针对性的工具调用之间交替，并将结果观察反馈到后续决策中，直到能够提供最终答案。

## 系统提示词{#system-prompt}

[`system_prompt`](https://reference.langchain.com/python/langchain/agents/#langchain.agents.create_agent\(system_prompt\)) 是一个可选参数, 可以作为字符串提供给智能体：

```python
agent = create_agent(
    model,
    tools,
    system_prompt="你是一个有帮助的助手。请简洁准确。"
)
```

**动态系统提示**

对于需要根据运行时上下文或智能体状态修改系统提示的高级用例, 您可以使用 [中间件](https://langchain-doc.cn/v1/python/langchain/middleware). [`@dynamic_prompt`](https://reference.langchain.com/python/langchain/middleware/#langchain.agents.middleware.dynamic_prompt) 装饰器创建中间件，根据模型请求动态生成系统提示.

之后应该还会出现很多装饰器和中间件, 本项目会有选择的进行实现.

## 调用{#call}

智能体存在状态State, 状态中包含消息序列. 调用就是向消息序列中传递新的消息

```python
result = agent.invoke(
    {"messages": [{"role": "user", "content": "旧金山天气如何？"}]}
)
```

## 高级概念{#concepts}

### 结构化输出{#structural-output}

在某些情况下，您可能希望智能体以特定格式返回输出。LangChain 通过 [`response_format`](https://reference.langchain.com/python/langchain/middleware/#langchain.agents.middleware.ModelRequest\(response_format\)) 参数提供结构化输出策略。

有两种方式实现, 分别是**ToolStrategy**和**ProviderStrategy**.`ToolStrategy` 使用人工工具调用生成结构化输出, 这适用于任何支持工具调用的模型。`ProviderStrategy` 使用模型提供商的原生结构化输出生成, 这更可靠，但仅适用于支持原生结构化输出的提供商（例如 OpenAI）.

下面是一个使用`ToolStrategy`的例子

```python
from pydantic import BaseModel
from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy


class ContactInfo(BaseModel):
    name: str
    email: str
    phone: str

agent = create_agent(
    model="openai:gpt-4o-mini",
    tools=[search_tool],
    response_format=ToolStrategy(ContactInfo)
)

result = agent.invoke({
    "messages": [{"role": "user", "content": "从以下内容提取联系信息：John Doe, john@example.com, (555) 123-4567"}]
})

result["structured_response"]
# ContactInfo(name='John Doe', email='john@example.com', phone='(555) 123-4567')
```

### 记忆{#memory}

智能体通过消息状态自动维护对话历史。您还可以配置智能体使用自定义状态模式，在对话期间记住额外信息。

存储在状态中的信息可以被视为智能体的[短期记忆](https://langchain-doc.cn/v1/python/langchain/short-term-memory)：

自定义状态模式必须扩展 [`AgentState`](https://reference.langchain.com/python/langchain/agents/#langchain.agents.AgentState) 作为 `TypedDict`。

定义自定义状态有两种方式：

1. 通过 [中间件](https://langchain-doc.cn/v1/python/langchain/middleware)（推荐）
2. 通过 [`create_agent`](https://reference.langchain.com/python/langchain/agents/#langchain.agents.create_agent) 上的 [`state_schema`](https://reference.langchain.com/python/langchain/middleware/#langchain.agents.middleware.AgentMiddleware.state_schema)

> **注意**
> 推荐通过中间件定义自定义状态，而不是通过 [`create_agent`](https://reference.langchain.com/python/langchain/agents/#langchain.agents.create_agent) 上的 [`state_schema`](https://reference.langchain.com/python/langchain/middleware/#langchain.agents.middleware.AgentMiddleware.state_schema)，因为它允许您将状态扩展概念上限定在相关中间件和工具的范围内。
>
> [`state_schema`](https://reference.langchain.com/python/langchain/middleware/#langchain.agents.middleware.AgentMiddleware.state_schema) 仍支持用于向后兼容，在 [`create_agent`](https://reference.langchain.com/python/langchain/agents/#langchain.agents.create_agent) 上。

**通过中间件定义状态**

```python
from langchain.agents import AgentState
from langchain.agents.middleware import AgentMiddleware


class CustomState(AgentState):
    user_preferences: dict

class CustomMiddleware(AgentMiddleware):
    state_schema = CustomState
    tools = [tool1, tool2]

    def before_model(self, state: CustomState, runtime) -> dict[str, Any] | None:
        ...

agent = create_agent(
    model,
    tools=tools,
    middleware=[CustomMiddleware()]
)

# 智能体现在可以跟踪消息之外的额外状态
result = agent.invoke({
    "messages": [{"role": "user", "content": "我更喜欢技术性解释"}],
    "user_preferences": {"style": "technical", "verbosity": "detailed"},
})
```

**通过** **`state_schema`** **定义状态**

```python
from langchain.agents import AgentState


class CustomState(AgentState):
    user_preferences: dict

agent = create_agent(
    model,
    tools=[tool1, tool2],
    state_schema=CustomState
)
# 智能体现在可以跟踪消息之外的额外状态
result = agent.invoke({
    "messages": [{"role": "user", "content": "我更喜欢技术性解释"}],
    "user_preferences": {"style": "technical", "verbosity": "detailed"},
})
```

### 流式传输{#stream}

我们已经看到如何使用 `invoke` 调用智能体以获取最终响应。如果智能体执行多个步骤，这可能需要一段时间。为了显示中间进度，我们可以随着消息的发生而流式传回。

```python
for chunk in agent.stream({
    "messages": [{"role": "user", "content": "搜索 AI 新闻并总结发现"}]
}, stream_mode="values"):
    # 每个块包含该时间点的完整状态
    latest_message = chunk["messages"][-1]
    if latest_message.content:
        print(f"智能体：{latest_message.content}")
    elif latest_message.tool_calls:
        print(f"正在调用工具：{[tc['name'] for tc in latest_message.tool_calls]}")
```

### 中间件{#middleware}

[中间件](https://langchain-doc.cn/v1/python/langchain/middleware) 为在执行的不同阶段自定义智能体行为提供了强大的扩展性。您可以使用中间件来：

- 在调用模型之前处理状态（例如消息裁剪、上下文注入）
- 修改或验证模型的响应（例如防护栏、内容过滤）
- 使用自定义逻辑处理工具执行错误
- 基于状态或上下文实现动态模型选择
- 添加自定义日志、监控或分析

中间件无缝集成到智能体的执行图中，允许您在关键点拦截和修改数据流，而无需更改核心智能体逻辑

# 模型{#Model}

总结: LLM是大脑, Agent是有完整执行功能的身体.

[大语言模型（LLMs）](https://en.wikipedia.org/wiki/Large_language_model) 是强大的 AI 工具，能够像人类一样理解和生成文本。它们用途广泛，可用于撰写内容、翻译语言、总结信息和回答问题，而无需针对每项任务进行专门训练。

除了文本生成之外，许多模型还支持：

- [工具调用](https://langchain-doc.cn/v1/python/langchain/models.html#工具调用) - 调用外部工具（如数据库查询或 API 调用）并将结果用于响应中。
- [结构化输出](https://langchain-doc.cn/v1/python/langchain/models.html#结构化输出) - 模型的响应被限制为遵循定义的格式。
- [多模态](https://langchain-doc.cn/v1/python/langchain/models.html#多模态) - 处理和返回非文本数据，如图像、音频和视频。
- [推理](https://langchain-doc.cn/v1/python/langchain/models.html#推理) - 模型执行多步推理以得出结论。

模型是 [智能体](https://langchain-doc.cn/v1/python/langchain/agents) 的推理引擎。它们驱动代理的决策过程，决定调用哪些工具、如何解释结果以及何时提供最终答案。

您选择的模型的质量和能力直接影响代理的可靠性和性能。不同模型在不同任务上表现出色——有些更擅长遵循复杂指令，有些更擅长结构化推理，有些支持更大的上下文窗口以处理更多信息。

LangChain 的标准模型接口为您提供对众多不同提供商集成的访问，这使得实验和切换模型以找到最适合您用例的模型变得非常容易。

## 基本用法{#basic-use}

主要有两种: **单独使用**, **与智能体一起使用**

老实说, 单独使用和直接打开豆包/gpt/gemini区别不大. 我是来学智能体的, 所以直接上第二种方式.

### 初始化模型{#model-init}

在 LangChain 中开始使用独立模型的最简单方法是使用 [`init_chat_model`](https://reference.langchain.com/python/langchain/models/#langchain.chat_models.init_chat_model) 从您选择的[提供商](https://langchain-doc.cn/v1/python/integrations/providers/overview)初始化一个模型.

智谱真的路边, 找半天不在主流提供商中, 也无法在`init_chat_model`中初始化, 它的初始化方法见[模型]({#model}). 在很边角料的地方找到了[智谱聊天模型的集成](https://docs.langchain.com/oss/python/integrations/chat/zhipuai), 例子用的是很低的版本glm-4, 而且不想下载额外的依赖, 这里不演示了.

### 关键方法{#key-methods}

| 方法         | 说明                        |
| ---------- | ------------------------- |
| **Invoke** | 模型接受消息作为输入，并在生成完整响应后输出消息。 |
| **Stream** | 调用模型，但实时流式传输生成的输出。        |
| **Batch**  | 将多个请求批量发送给模型，以实现更高效的处理。   |

> **信息**
> 除了聊天模型之外，LangChain 还支持其他相关技术，如嵌入模型和向量存储。详情请参阅[集成页面](https://langchain-doc.cn/v1/python/integrations/providers/overview)。

## 参数{#parameter}

聊天模型接受可用于配置其行为的一组参数。支持的参数集因模型和提供商而异，但标准参数包括：

| 参数            | 类型     | 必填 | 说明                                               |
| ------------- | ------ | -- | ------------------------------------------------ |
| `model`       | string | 是  | 您想使用的特定模型的名称或标识符。                                |
| `api_key`     | string | 否  | 用于向模型提供商进行身份验证的密钥。通常在注册访问模型时颁发。通常通过设置**环境变量**访问。 |
| `temperature` | number | 否  | 控制模型输出的随机性。值越高，响应越具创造性；值越低，响应越确定性。               |
| `timeout`     | number | 否  | 在取消请求之前等待模型响应的最大时间（秒）。                           |
| `max_tokens`  | number | 否  | 限制响应中的**令牌**总数，有效控制输出长度。                         |
| `max_retries` | number | 否  | 如果因网络超时或速率限制等问题而失败，系统将重新发送请求的最大尝试次数。             |

使用 [`init_chat_model`](https://reference.langchain.com/python/langchain/models/#langchain.chat_models.init_chat_model)，将这些参数作为内联 `**kwargs` 传递

## 调用{#invoke}

有三种调用方式

- `invoke()`传入单个消息或消息列表
- `stream()`返回一个迭代器,它在生成时逐块产生输出。

  迭代器中有多个 **AIMessageChunk**对象, 每个对象包含一部分输出文本, 流中的每个块通过求和聚合成完整消息
  ```python
  full = None  # None | AIMessageChunk
  for chunk in model.stream("天空是什么颜色？"):
      full = chunk if full is None else full + chunk
      print(full.text)
  
  # 天空
  # 天空是
  # 天空通常
  # 天空通常是蓝色
  # ...
  
  print(full.content_blocks)
  # [{"type": "text", "text": "天空通常是蓝色..."}]
  ```
- `batch()`将一组独立请求批量处理给模型可以显著提高性能并降低成本，因为处理可以并行进行
  ```python
  responses = model.batch([
      "为什么鹦鹉有五颜六色的羽毛？",
      "飞机是如何飞行的？",
      "什么是量子计算？"
  ])
  for response in responses:
      print(response)
  ```

## 工具调用{#tool-calls}

模型可以请求调用执行任务的工具，例如从数据库获取数据、搜索网络或运行代码。工具是以下内容的配对：

1. 架构，包括工具的名称、描述和/或参数定义（通常是 JSON 架构）
2. 要执行的函数或**协程**

> **注意**
> 您可能会听到“函数调用”一词。我们将此与“工具调用”互换使用。

要使您定义的工具可供模型使用，您必须使用 [`bind_tools()`](https://reference.langchain.com/python/langchain_core/language_models/#langchain_core.language_models.chat_models.BaseChatModel.bind_tools) 绑定它们。在后续调用中，模型可以根据需要选择调用任何绑定的工具。

```python
from langchain.tools import tool

@tool
def get_weather(location: str) -> str:
    """获取某个位置的天气。"""
    return f"{location} 天气晴朗。"

model_with_tools = model.bind_tools([get_weather])  # [!code highlight]

response = model_with_tools.invoke("波士顿的天气怎么样？")
for tool_call in response.tool_calls:
    # 查看模型发出的工具调用
    print(f"工具：{tool_call['name']}")
    print(f"参数：{tool_call['args']}")
```

### 工具执行循环{#tool-call-loop}

当模型返回工具调用时，您需要执行工具并将结果传递回模型。这会创建一个对话循环，模型可以使用工具结果生成其最终响应。LangChain 包含[智能体](https://langchain-doc.cn/v1/python/langchain/agents)抽象来为您处理此协调。

```python
# 将（可能多个）工具绑定到模型
model_with_tools = model.bind_tools([get_weather])

# 步骤 1：模型生成工具调用
messages = [{"role": "user", "content": "波士顿的天气怎么样？"}]
ai_msg = model_with_tools.invoke(messages)
messages.append(ai_msg)

# 步骤 2：执行工具并收集结果
for tool_call in ai_msg.tool_calls:
    # 使用生成的参数执行工具
    tool_result = get_weather.invoke(tool_call)
    messages.append(tool_result)

# 步骤 3：将结果传递回模型以获取最终响应
final_response = model_with_tools.invoke(messages)
print(final_response.text)
# "波士顿当前天气为 72°F，晴朗。"
```

### 强制工具调用{#tool-call-enforce}

默认情况下，模型可以根据用户输入自由选择使用哪个绑定的工具。但是，您可能希望强制选择工具，确保模型使用特定工具或给定列表中的**任何**工具：

```python
model_with_tools = model.bind_tools([tool_1], tool_choice="any")
```

```python
model_with_tools = model.bind_tools([tool_1], tool_choice="tool_1")
```

### 并行工具调用{#tool-call-parallel}

许多模型支持在适当时并行调用多个工具。这允许模型同时从不同来源收集信息。

```python
model_with_tools = model.bind_tools([get_weather])

response = model_with_tools.invoke(
    "波士顿和东京的天气怎么样？"
)

# 模型可能会生成多个工具调用
print(response.tool_calls)
# [
#   {'name': 'get_weather', 'args': {'location': 'Boston'}, 'id': 'call_1'},
#   {'name': 'get_weather', 'args': {'location': 'Tokyo'}, 'id': 'call_2'},
# ]

# 执行所有工具（可以使用 async 并行执行）
results = []
for tool_call in response.tool_calls:
    if tool_call['name'] == 'get_weather':
        result = get_weather.invoke(tool_call)
    ...
    results.append(result)
```

### 流式传输工具调用{#tool-call-stream}

在流式传输响应时，工具调用通过 [`ToolCallChunk`](https://reference.langchain.com/python/langchain/messages/#langchain.messages.ToolCallChunk) 逐步构建。这允许您在生成工具调用时查看它们，而不是等待完整响应。

```python
for chunk in model_with_tools.stream(
    "波士顿和东京的天气怎么样？"
):
    # 工具调用块逐步到达
    for tool_chunk in chunk.tool_call_chunks:
        if name := tool_chunk.get("name"):
            print(f"工具：{name}")
        if id_ := tool_chunk.get("id"):
            print(f"ID：{id_}")
        if args := tool_chunk.get("args"):
            print(f"参数：{args}")

# 输出：
# 工具：get_weather
# ID：call_SvMlU1TVIZugrFLckFE2ceRE
# 参数：{"lo
# 参数：catio
# 参数：n": "B
# 参数：osto
# 参数：n"}
# 工具：get_weather
# ID：call_QMZdy6qInx13oWKE7KhuhOLR
# 参数：{"lo
# 参数：catio
# 参数：n": "T
# 参数：okyo
# 参数："}
```

## 结构化输出{#structural-out}

可以请求模型以匹配给定架构的格式提供其响应。这对于确保输出易于解析并用于后续处理非常有用。LangChain 支持多种架构类型和强制执行结构化输出的方法。主要有Pydantic, TypedDict, JSON Schema三种方法.

**Pydantic**返回一个BaseModel对象, **TypeDict**返回一个dict, **JSON Schema**返回一个dict

# 消息{#Message}

消息是 LangChain 中模型上下文的基本单位。它们代表模型的输入和输出，携带内容和元数据，用于在与 LLM 交互时表示对话状态。

消息是包含以下内容的对象：

- **角色** - 标识消息类型（例如 `system`、`user`）
- **内容** - 表示消息的实际内容（例如文本、图像、音频、文档等）
- **元数据** - 可选字段，例如响应信息、消息 ID 和令牌使用情况



调用模型时传入消息

```python
model.invoke(messages)
```



## 基本用法{#usage}

消息可以是以下类型: 字符串(使用的是human message)/列表/字典

## 消息类型

- [系统消息(system message)](https://langchain-doc.cn/v1/python/langchain/messages.html#系统消息) - 告诉模型如何行为并为交互提供上下文
- [人类消息(human message)](https://langchain-doc.cn/v1/python/langchain/messages.html#人类消息) - 表示用户输入和与模型的交互
- [AI 消息(ai message)](https://langchain-doc.cn/v1/python/langchain/messages.html#ai-消息) - 模型生成的响应，包括文本内容、工具调用和元数据
- [工具消息(tool message)](https://langchain-doc.cn/v1/python/langchain/messages.html#工具消息) - 表示[工具调用](https://langchain-doc.cn/v1/python/langchain/models#tool-calling)的输出

前两个是人为输入, 后两个可以是模型的返回结果, 也可以是人为输入

## 消息内容

您可以将消息的内容视为发送给模型的数据负载。消息具有一个松散类型的 `content` 属性，支持字符串和未类型对象列表（例如字典）。这允许在 LangChain 聊天模型中直接支持提供商原生结构，例如[多模态](https://langchain-doc.cn/v1/python/langchain/messages.html#多模态)内容和其他数据。

LangChain 另外为文本、推理、引用、多模态数据、服务器端工具调用和其他消息内容提供了专用内容类型。请参阅下面的[标准内容块](https://langchain-doc.cn/v1/python/langchain/messages.html#标准内容块)。

LangChain 聊天模型接受 `content` 属性中的消息内容，可以包含：

1. 一个字符串
2. 提供商原生格式的内容块列表
3. [LangChain 的标准内容块](https://langchain-doc.cn/v1/python/langchain/messages.html#标准内容块)列表

# 工具{#Tools}

许多 AI 应用程序通过自然语言与用户交互。然而，某些用例要求模型使用结构化输入直接与外部系统（例如 **API**、**数据库** 或 **文件系统**）对接。

**工具** 是 **[代理（agents）](https://langchain-doc.cn/v1/python/langchain/agents)** 调用来执行操作的组件。它们通过允许模型通过定义明确的输入和输出与世界交互来扩展模型的功能。工具封装了一个可调用的函数及其输入架构（schema）。这些可以传递给兼容的 **[聊天模型（chat models）](https://langchain-doc.cn/v1/python/langchain/models)**，让模型决定是否以及使用什么参数来调用工具。在这些场景中，**工具调用** 使模型能够生成符合指定输入架构的请求。

## 创建工具
