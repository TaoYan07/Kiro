# Python MCP Servers 实现说明

## 📋 概述

我已经用Python重写了两个MCP服务器，并提供了完整的文档和示例。

## 🎯 两个服务器的核心逻辑

### 1. Knowledge Base Server（知识库服务器）

**核心功能：**
- 语义搜索：使用向量嵌入进行相似度搜索
- 内容管理：添加、更新知识库内容
- 智能过滤：按分类、标签筛选

**工作流程：**
```
用户查询 → 向量化 → 余弦相似度搜索 → 排序 → 返回Top K结果
```

**关键技术：**
- 向量嵌入（OpenAI text-embedding-3-small）
- 向量数据库（ChromaDB/Pinecone）
- 余弦相似度计算

### 2. Ticketing Server（工单服务器）

**核心功能：**
- 工单管理：创建、更新、搜索工单
- 状态跟踪：open → in_progress → resolved → closed
- 外部集成：GitHub Issues、Jira、Linear

**工作流程：**
```
创建工单 → 存储 → 通知团队 → 跟踪状态 → 更新 → 关闭
```

**关键技术：**
- RESTful API集成
- 状态机管理
- 异步通知

## 📁 文件结构

```
mcp-servers/
├── knowledge-base-server/
│   ├── server.py              # Python实现
│   ├── src/index.ts           # TypeScript原版
│   └── package.json
├── ticketing-server/
│   ├── server.py              # Python实现
│   ├── src/index.ts           # TypeScript原版
│   └── package.json
├── requirements.txt           # Python依赖
├── test_servers.py           # 测试脚本
└── README_CN.md              # 中文说明

docs/
├── MCP-SERVERS-LOGIC-CN.md   # 详细逻辑说明
├── QA-TICKETING-FLOW-DIAGRAM.md  # 流程图
└── PYTHON-IMPLEMENTATION-CN.md   # 本文档

config/
├── mcp.json                  # TypeScript配置
└── mcp-python.json          # Python配置
```

## 🚀 快速开始

### 1. 安装依赖

```bash
# 安装Python MCP SDK
pip install mcp

# 可选：安装向量数据库和集成
pip install chromadb openai PyGithub
```

### 2. 配置环境变量

复制 `.env.example` 到 `.env` 并填写：

```bash
# OpenAI API（用于生成embeddings）
OPENAI_API_KEY=sk-...

# GitHub（用于工单集成）
GITHUB_TOKEN=ghp_...
GITHUB_REPO=owner/repo
```

### 3. 配置MCP服务器

在 `.kiro/settings/mcp.json` 中添加：

```json
{
  "mcpServers": {
    "knowledge-base": {
      "command": "python",
      "args": ["mcp-servers/knowledge-base-server/server.py"],
      "env": {
        "PYTHONPATH": ".",
        "OPENAI_API_KEY": "${OPENAI_API_KEY}"
      }
    },
    "ticketing": {
      "command": "python",
      "args": ["mcp-servers/ticketing-server/server.py"],
      "env": {
        "PYTHONPATH": ".",
        "GITHUB_TOKEN": "${GITHUB_TOKEN}"
      }
    }
  }
}
```

### 4. 测试服务器

```bash
# 运行测试脚本（查看示例输出）
python mcp-servers/test_servers.py

# 直接运行服务器
python mcp-servers/knowledge-base-server/server.py
python mcp-servers/ticketing-server/server.py
```

## 💡 使用示例

### 搜索知识库

```python
# 通过MCP调用
result = await mcp_client.call_tool(
    server="knowledge-base",
    tool="search_knowledge_base",
    arguments={
        "query": "如何重置密码",
        "top_k": 5,
        "filters": {
            "category": "账户管理"
        }
    }
)

# 返回结果
{
  "results": [
    {
      "content": "要重置密码，请访问设置页面...",
      "metadata": {"title": "密码重置", "category": "账户管理"},
      "score": 0.95
    }
  ],
  "count": 1
}
```

### 创建工单

```python
# 通过MCP调用
result = await mcp_client.call_tool(
    server="ticketing",
    tool="create_ticket",
    arguments={
        "title": "登录问题",
        "description": "用户无法登录系统",
        "priority": "high",
        "labels": ["bug", "login"]
    }
)

# 返回结果
{
  "success": true,
  "ticket": {
    "id": "TICKET-003",
    "title": "登录问题",
    "status": "open",
    "priority": "high",
    "created_at": "2024-01-30T10:00:00Z"
  }
}
```

## 🔄 完整QA工作流

### 场景1：找到答案（不创建工单）

```
用户: "如何重置密码？"
  ↓
1. 搜索知识库
   → 找到3个结果，最高分0.95
  ↓
2. 生成答案（置信度0.95 >= 0.7）
  ↓
3. 返回答案
   ✓ 不创建工单
```

**响应：**
```
"要重置密码，请访问设置页面，点击'安全'选项卡，
然后选择'重置密码'。"
```

### 场景2：未找到答案（自动创建工单）

```
用户: "新功能为什么不工作？"
  ↓
1. 搜索知识库
   → 找到0个结果
  ↓
2. 生成答案（置信度0.3 < 0.7）
  ↓
3. 自动创建工单 TICKET-004
  ↓
4. 返回答案 + 工单ID
```

**响应：**
```
"抱歉，我没有找到相关信息。我已创建工单 TICKET-004 
来跟进您的问题，团队会尽快回复。"
```

## 🔧 实际集成示例

### 使用ChromaDB + OpenAI

```python
import chromadb
from openai import OpenAI

# 初始化
chroma_client = chromadb.Client()
collection = chroma_client.create_collection("kb")
openai_client = OpenAI()

# 添加文档
def add_document(content, metadata):
    # 生成embedding
    response = openai_client.embeddings.create(
        model="text-embedding-3-small",
        input=content
    )
    embedding = response.data[0].embedding
    
    # 存储
    collection.add(
        ids=[f"doc_{timestamp}"],
        documents=[content],
        embeddings=[embedding],
        metadatas=[metadata]
    )

# 搜索
def search(query, top_k=5):
    response = openai_client.embeddings.create(
        model="text-embedding-3-small",
        input=query
    )
    query_embedding = response.data[0].embedding
    
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )
    
    return results
```

### 使用GitHub Issues

```python
from github import Github

# 初始化
g = Github("your_token")
repo = g.get_repo("owner/repo")

# 创建工单
def create_ticket(title, description, labels):
    issue = repo.create_issue(
        title=title,
        body=description,
        labels=labels
    )
    
    return {
        "id": f"TICKET-{issue.number}",
        "url": issue.html_url
    }

# 更新工单
def update_ticket(issue_number, comment):
    issue = repo.get_issue(issue_number)
    issue.create_comment(comment)
```

## 📊 性能优化

### 1. 缓存热门查询

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def search_cache(query: str):
    return search_knowledge_base(query)
```

### 2. 批量处理

```python
# 批量生成embeddings
embeddings = openai_client.embeddings.create(
    model="text-embedding-3-small",
    input=[doc1, doc2, doc3, ...]  # 一次处理多个
)
```

### 3. 异步操作

```python
import asyncio

async def create_ticket_async(data):
    ticket = create_ticket(data)
    
    # 异步发送通知（不阻塞）
    asyncio.create_task(send_notifications(ticket))
    
    return ticket
```

## 🎓 核心概念

### 向量相似度搜索

```python
import numpy as np

def cosine_similarity(vec1, vec2):
    """
    余弦相似度：衡量两个向量的方向相似性
    
    返回值：0-1
    - 1: 完全相同
    - 0: 完全不相关
    """
    dot_product = np.dot(vec1, vec2)
    norm_a = np.linalg.norm(vec1)
    norm_b = np.linalg.norm(vec2)
    
    return dot_product / (norm_a * norm_b)
```

### 工单生命周期

```
OPEN → IN_PROGRESS → RESOLVED → CLOSED
  ↓         ↓            ↓
评论     更新优先级    添加解决方案
```

## 📚 相关文档

- `docs/MCP-SERVERS-LOGIC-CN.md` - 详细的逻辑说明和代码示例
- `docs/QA-TICKETING-FLOW-DIAGRAM.md` - 完整的流程图和架构图
- `mcp-servers/README_CN.md` - 服务器使用说明
- `mcp-servers/test_servers.py` - 测试和示例代码

## ❓ 常见问题

### Q: 为什么要用向量搜索而不是关键词搜索？

A: 向量搜索可以理解语义，例如：
- 查询："如何修改密码" 
- 匹配："重置密码的步骤"
- 关键词不同，但语义相同

### Q: 什么时候会自动创建工单？

A: 满足以下任一条件：
1. 知识库没有找到相关结果
2. 答案置信度 < 0.7
3. 用户明确报告问题（intent=issue）

### Q: 如何集成到现有系统？

A: 三种方式：
1. 使用MCP协议（推荐）
2. 直接调用Python函数
3. 封装为REST API

## 🚧 下一步改进

1. ✅ 基础实现完成
2. ⬜ 添加真实的向量数据库（ChromaDB）
3. ⬜ 集成OpenAI embeddings
4. ⬜ 添加GitHub/Jira API集成
5. ⬜ 实现持久化存储
6. ⬜ 添加缓存层
7. ⬜ 编写单元测试
8. ⬜ 添加监控和日志

## 📞 总结

两个MCP服务器已经用Python重写完成：

1. **Knowledge Base Server** - 提供语义搜索和知识管理
2. **Ticketing Server** - 提供工单创建和跟踪

它们协同工作，实现智能QA和自动工单创建的完整流程。当知识库无法回答问题时，系统会自动创建工单，确保没有用户问题被遗漏。
