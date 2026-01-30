# MCP Servers - Python实现

这是两个MCP服务器的Python实现，用于QA和自动工单系统。

## 服务器说明

### 1. Knowledge Base Server (知识库服务器)

**功能：**
- `search_knowledge_base` - 在知识库中搜索相关信息
- `add_to_knowledge_base` - 向知识库添加新内容
- `get_knowledge_stats` - 获取知识库统计信息

**工作原理：**
1. 存储文档和元数据
2. 使用向量嵌入进行语义搜索
3. 支持按分类、标签过滤
4. 返回最相关的top_k结果

**实际集成建议：**
- 使用 ChromaDB 或 Pinecone 作为向量数据库
- 使用 OpenAI Embeddings 或 sentence-transformers 生成向量
- 添加缓存层提高性能

### 2. Ticketing Server (工单服务器)

**功能：**
- `create_ticket` - 创建新工单
- `update_ticket` - 更新工单状态、优先级、评论等
- `search_tickets` - 搜索和过滤工单
- `get_ticket` - 获取单个工单详情
- `get_ticket_stats` - 获取工单统计信息

**工作原理：**
1. 管理工单生命周期（创建、更新、关闭）
2. 支持优先级、标签、指派人
3. 记录评论历史
4. 提供搜索和统计功能

**实际集成建议：**
- 集成 GitHub Issues API
- 集成 Jira REST API
- 集成 Linear GraphQL API
- 添加 Webhook 通知

## 安装

```bash
# 安装依赖
pip install -r requirements.txt

# 或使用 uv
uv pip install -r requirements.txt
```

## 配置

在 `.kiro/settings/mcp.json` 中配置：

```json
{
  "mcpServers": {
    "knowledge-base": {
      "command": "python",
      "args": ["mcp-servers/knowledge-base-server/server.py"],
      "env": {
        "PYTHONPATH": "."
      }
    },
    "ticketing": {
      "command": "python",
      "args": ["mcp-servers/ticketing-server/server.py"],
      "env": {
        "PYTHONPATH": "."
      }
    }
  }
}
```

## 使用示例

### 搜索知识库

```python
# 通过MCP调用
result = await mcp.call_tool(
    "knowledge-base",
    "search_knowledge_base",
    {
        "query": "如何重置密码",
        "top_k": 3,
        "filters": {
            "category": "账户管理"
        }
    }
)
```

### 创建工单

```python
# 通过MCP调用
result = await mcp.call_tool(
    "ticketing",
    "create_ticket",
    {
        "title": "登录问题",
        "description": "用户无法登录系统",
        "priority": "high",
        "labels": ["bug", "login"]
    }
)
```

## 扩展建议

### Knowledge Base Server

1. **向量数据库集成**
```python
import chromadb

client = chromadb.Client()
collection = client.create_collection("knowledge_base")

# 添加文档
collection.add(
    documents=["文档内容"],
    metadatas=[{"category": "账户"}],
    ids=["kb_001"]
)

# 搜索
results = collection.query(
    query_texts=["如何重置密码"],
    n_results=5
)
```

2. **OpenAI Embeddings**
```python
from openai import OpenAI

client = OpenAI()

def get_embedding(text):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding
```

### Ticketing Server

1. **GitHub Issues集成**
```python
from github import Github

g = Github("your_token")
repo = g.get_repo("owner/repo")

# 创建issue
issue = repo.create_issue(
    title="Bug报告",
    body="详细描述",
    labels=["bug"]
)
```

2. **Jira集成**
```python
from jira import JIRA

jira = JIRA(
    server="https://your-domain.atlassian.net",
    basic_auth=("email", "api_token")
)

# 创建issue
issue = jira.create_issue(
    project="PROJ",
    summary="问题标题",
    description="详细描述",
    issuetype={"name": "Bug"}
)
```

## 架构图

```
┌─────────────────────────────────────────────────┐
│           Workflow Engine                        │
│                                                  │
│  ┌──────────────────────────────────────────┐  │
│  │  Context: user_query, results, etc.      │  │
│  └──────────────────────────────────────────┘  │
│                                                  │
└────────────┬──────────────────┬─────────────────┘
             │                  │
             ▼                  ▼
    ┌────────────────┐   ┌────────────────┐
    │  Knowledge     │   │  Ticketing     │
    │  Base Server   │   │  Server        │
    │                │   │                │
    │  Python MCP    │   │  Python MCP    │
    │                │   │                │
    │  ┌──────────┐ │   │  ┌──────────┐ │
    │  │ ChromaDB │ │   │  │ GitHub   │ │
    │  │ Pinecone │ │   │  │ Jira     │ │
    │  │ OpenAI   │ │   │  │ Linear   │ │
    │  └──────────┘ │   │  └──────────┘ │
    └────────────────┘   └────────────────┘
```

## 测试

```bash
# 测试知识库服务器
python mcp-servers/knowledge-base-server/server.py

# 测试工单服务器
python mcp-servers/ticketing-server/server.py
```

## 注意事项

1. 当前实现使用内存存储，重启后数据会丢失
2. 向量搜索使用简单的关键词匹配，实际应使用真实的向量相似度
3. 需要添加错误处理和日志记录
4. 生产环境应使用真实的数据库和外部API
5. 建议添加认证和授权机制

## 下一步

1. 集成真实的向量数据库（ChromaDB/Pinecone）
2. 添加OpenAI embeddings支持
3. 集成GitHub/Jira API
4. 添加持久化存储
5. 实现缓存机制
6. 添加监控和日志
7. 编写单元测试
