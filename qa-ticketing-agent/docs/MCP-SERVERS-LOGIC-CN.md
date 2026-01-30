# MCP Servers 逻辑详解

## 概述

两个MCP服务器的核心逻辑和实现方式。

## 1. Knowledge Base Server（知识库服务器）

### 核心逻辑

```
用户查询 → 向量化 → 相似度搜索 → 排序 → 返回结果
```

### 详细流程

#### A. 添加内容到知识库

```python
def add_to_knowledge_base(content, metadata):
    """
    步骤：
    1. 接收文本内容和元数据
    2. 生成向量嵌入（embedding）
    3. 存储到向量数据库
    4. 返回ID
    """
    
    # 1. 生成向量
    embedding = generate_embedding(content)
    # 使用 OpenAI: text-embedding-3-small
    # 或本地模型: sentence-transformers
    
    # 2. 存储
    vector_db.add(
        id=generate_id(),
        content=content,
        embedding=embedding,
        metadata=metadata
    )
    
    # 3. 返回结果
    return {"success": True, "id": id}
```

**实际实现示例（使用ChromaDB）：**

```python
import chromadb
from openai import OpenAI

class KnowledgeBase:
    def __init__(self):
        self.chroma_client = chromadb.Client()
        self.collection = self.chroma_client.create_collection("kb")
        self.openai_client = OpenAI()
    
    def add_content(self, content, metadata):
        # 生成embedding
        response = self.openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=content
        )
        embedding = response.data[0].embedding
        
        # 存储到ChromaDB
        doc_id = f"kb_{datetime.now().timestamp()}"
        self.collection.add(
            ids=[doc_id],
            documents=[content],
            embeddings=[embedding],
            metadatas=[metadata]
        )
        
        return doc_id
```

#### B. 搜索知识库

```python
def search_knowledge_base(query, top_k=5, filters=None):
    """
    步骤：
    1. 将查询文本向量化
    2. 在向量数据库中进行相似度搜索
    3. 应用过滤条件（分类、标签等）
    4. 返回top_k个最相关结果
    """
    
    # 1. 查询向量化
    query_embedding = generate_embedding(query)
    
    # 2. 向量搜索（余弦相似度）
    results = vector_db.search(
        query_embedding=query_embedding,
        top_k=top_k,
        filters=filters
    )
    
    # 3. 返回结果
    return {
        "results": [
            {
                "content": r.content,
                "metadata": r.metadata,
                "score": r.similarity_score  # 0-1之间
            }
            for r in results
        ],
        "count": len(results)
    }
```

**向量相似度计算：**

```python
import numpy as np

def cosine_similarity(vec1, vec2):
    """
    余弦相似度：衡量两个向量的方向相似性
    
    公式：cos(θ) = (A · B) / (||A|| × ||B||)
    
    返回值：-1 到 1
    - 1: 完全相同
    - 0: 正交（无关）
    - -1: 完全相反
    """
    dot_product = np.dot(vec1, vec2)
    norm_a = np.linalg.norm(vec1)
    norm_b = np.linalg.norm(vec2)
    
    return dot_product / (norm_a * norm_b)

# 示例
query_vec = [0.1, 0.2, 0.3, ...]  # 1536维（OpenAI）
doc_vec = [0.15, 0.22, 0.28, ...]

similarity = cosine_similarity(query_vec, doc_vec)
# 结果：0.95 (非常相似)
```

### 数据流示例

```
输入：
{
  "query": "如何重置密码",
  "top_k": 3,
  "filters": {"category": "账户管理"}
}

处理过程：
1. 向量化查询
   "如何重置密码" → [0.12, 0.34, 0.56, ..., 0.78]

2. 搜索向量数据库
   找到相似文档：
   - Doc1: score=0.95 "要重置密码，请访问..."
   - Doc2: score=0.88 "密码重置步骤..."
   - Doc3: score=0.82 "忘记密码？点击..."

3. 应用过滤
   只保留 category="账户管理" 的文档

4. 返回top_k
   返回前3个结果

输出：
{
  "results": [
    {
      "content": "要重置密码，请访问设置页面...",
      "metadata": {"title": "密码重置", "category": "账户管理"},
      "score": 0.95
    },
    ...
  ],
  "count": 3
}
```

## 2. Ticketing Server（工单服务器）

### 核心逻辑

```
创建工单 → 存储 → 通知 → 跟踪 → 更新 → 关闭
```

### 详细流程

#### A. 创建工单

```python
def create_ticket(title, description, priority, labels):
    """
    步骤：
    1. 验证输入
    2. 生成工单ID
    3. 设置初始状态
    4. 存储到数据库/外部系统
    5. 发送通知
    6. 返回工单信息
    """
    
    # 1. 生成ID
    ticket_id = f"TICKET-{counter}"
    
    # 2. 创建工单对象
    ticket = {
        "id": ticket_id,
        "title": title,
        "description": description,
        "status": "open",
        "priority": priority,
        "labels": labels,
        "created_at": now(),
        "updated_at": now(),
        "comments": []
    }
    
    # 3. 存储
    database.save(ticket)
    
    # 4. 调用外部API（可选）
    github.create_issue(title, description, labels)
    # 或
    jira.create_issue(project, summary, description)
    
    # 5. 发送通知
    notify_team(ticket)
    
    return ticket
```

**实际实现示例（GitHub集成）：**

```python
from github import Github

class TicketingSystem:
    def __init__(self, github_token, repo_name):
        self.github = Github(github_token)
        self.repo = self.github.get_repo(repo_name)
    
    def create_ticket(self, title, description, priority, labels):
        # 根据优先级添加标签
        all_labels = labels + [f"priority:{priority}"]
        
        # 在GitHub创建issue
        issue = self.repo.create_issue(
            title=title,
            body=description,
            labels=all_labels
        )
        
        # 存储到本地数据库
        ticket = {
            "id": f"TICKET-{issue.number}",
            "github_issue_id": issue.number,
            "title": title,
            "description": description,
            "status": "open",
            "priority": priority,
            "labels": all_labels,
            "url": issue.html_url,
            "created_at": issue.created_at.isoformat()
        }
        
        self.db.save(ticket)
        
        return ticket
```

#### B. 更新工单

```python
def update_ticket(ticket_id, status=None, comment=None, assignee=None):
    """
    步骤：
    1. 查找工单
    2. 更新字段
    3. 添加评论
    4. 记录历史
    5. 同步到外部系统
    6. 发送通知
    """
    
    # 1. 查找
    ticket = database.find(ticket_id)
    
    # 2. 更新
    if status:
        ticket["status"] = status
    
    if assignee:
        ticket["assignee"] = assignee
    
    # 3. 添加评论
    if comment:
        ticket["comments"].append({
            "author": current_user,
            "text": comment,
            "timestamp": now()
        })
    
    # 4. 更新时间戳
    ticket["updated_at"] = now()
    
    # 5. 保存
    database.save(ticket)
    
    # 6. 同步到GitHub/Jira
    external_api.update_issue(ticket_id, status, comment)
    
    return ticket
```

#### C. 搜索工单

```python
def search_tickets(query, status=None, priority=None, labels=None):
    """
    步骤：
    1. 构建搜索条件
    2. 文本搜索（标题+描述）
    3. 应用过滤器
    4. 计算相关性分数
    5. 排序返回
    """
    
    results = []
    
    for ticket in database.all_tickets():
        # 1. 文本匹配
        if query:
            text = ticket["title"] + " " + ticket["description"]
            if query.lower() not in text.lower():
                continue
        
        # 2. 状态过滤
        if status and ticket["status"] != status:
            continue
        
        # 3. 优先级过滤
        if priority and ticket["priority"] != priority:
            continue
        
        # 4. 标签过滤
        if labels:
            if not set(labels).intersection(set(ticket["labels"])):
                continue
        
        # 5. 计算相关性
        score = calculate_relevance(query, ticket)
        
        results.append({
            **ticket,
            "relevance_score": score
        })
    
    # 6. 排序
    results.sort(key=lambda x: x["relevance_score"], reverse=True)
    
    return results
```

### 工单生命周期

```
┌──────────┐
│  创建     │ create_ticket()
│  OPEN    │
└────┬─────┘
     │
     ▼
┌──────────┐
│ 处理中    │ update_ticket(status="in_progress")
│IN_PROGRESS│
└────┬─────┘
     │
     ├─→ 添加评论 update_ticket(comment="...")
     │
     ├─→ 更改优先级 update_ticket(priority="high")
     │
     ├─→ 指派人员 update_ticket(assignee="dev1")
     │
     ▼
┌──────────┐
│  已解决   │ update_ticket(status="resolved")
│ RESOLVED │
└────┬─────┘
     │
     ▼
┌──────────┐
│  已关闭   │ update_ticket(status="closed")
│  CLOSED  │
└──────────┘
```

### 数据流示例

```
输入（创建工单）：
{
  "title": "登录页面加载缓慢",
  "description": "用户报告登录页面加载时间超过5秒...",
  "priority": "high",
  "labels": ["performance", "login"]
}

处理过程：
1. 生成ID: TICKET-003
2. 设置状态: open
3. 记录时间: 2024-01-30T10:00:00Z
4. 调用GitHub API创建issue
5. 发送Slack通知给团队

输出：
{
  "success": true,
  "ticket": {
    "id": "TICKET-003",
    "title": "登录页面加载缓慢",
    "status": "open",
    "priority": "high",
    "labels": ["performance", "login"],
    "created_at": "2024-01-30T10:00:00Z",
    "url": "https://github.com/org/repo/issues/123"
  }
}
```

## 两个服务器的协同工作

### 在QA流程中的配合

```
用户提问
    ↓
1. Knowledge Base Server 搜索
    ↓
   找到答案？
    ├─ 是 → 返回答案（置信度高）
    │
    └─ 否 → 2. Ticketing Server 创建工单
              ↓
              返回答案 + 工单ID
```

### 实际场景示例

**场景1：找到答案**
```python
# 1. 搜索知识库
kb_result = await kb_server.search({
    "query": "如何重置密码",
    "top_k": 5
})

# 结果：找到3个相关文档，最高分0.95
if kb_result["count"] > 0 and kb_result["results"][0]["score"] > 0.7:
    # 置信度高，直接返回答案
    return kb_result["results"][0]["content"]
```

**场景2：未找到答案，创建工单**
```python
# 1. 搜索知识库
kb_result = await kb_server.search({
    "query": "新功能为什么不工作",
    "top_k": 5
})

# 结果：没有找到相关文档
if kb_result["count"] == 0:
    # 2. 自动创建工单
    ticket = await ticketing_server.create({
        "title": "新功能为什么不工作",
        "description": f"用户查询：{user_query}\n\n知识库未找到相关信息",
        "priority": "medium",
        "labels": ["auto-generated", "question"]
    })
    
    # 3. 返回组合响应
    return f"抱歉，我没有找到相关信息。我已创建工单 {ticket['id']} 来跟进此问题。"
```

## 技术栈对比

### TypeScript实现
```typescript
// 使用 @modelcontextprotocol/sdk
import { Server } from "@modelcontextprotocol/sdk/server/index.js";

const server = new Server({
  name: "knowledge-base-server",
  version: "1.0.0"
});

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  // 处理逻辑
});
```

### Python实现
```python
# 使用 mcp Python SDK
from mcp.server import Server

server = Server("knowledge-base-server")

@server.call_tool()
async def call_tool(name: str, arguments: Any):
    # 处理逻辑
    pass
```

## 性能优化建议

### Knowledge Base Server
1. **缓存热门查询**
```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def search_cache(query: str):
    return search_knowledge_base(query)
```

2. **批量向量化**
```python
# 一次性处理多个文档
embeddings = openai.embeddings.create(
    model="text-embedding-3-small",
    input=[doc1, doc2, doc3, ...]  # 批量
)
```

3. **使用近似最近邻（ANN）**
```python
# 使用FAISS加速搜索
import faiss

index = faiss.IndexFlatL2(dimension)
index.add(embeddings)
distances, indices = index.search(query_embedding, k=5)
```

### Ticketing Server
1. **数据库索引**
```sql
CREATE INDEX idx_status ON tickets(status);
CREATE INDEX idx_priority ON tickets(priority);
CREATE INDEX idx_created_at ON tickets(created_at);
```

2. **异步通知**
```python
import asyncio

async def create_ticket_async(data):
    # 创建工单
    ticket = create_ticket(data)
    
    # 异步发送通知（不阻塞）
    asyncio.create_task(send_notifications(ticket))
    
    return ticket
```

3. **批量操作**
```python
# 批量更新工单
def bulk_update_tickets(ticket_ids, updates):
    database.bulk_update(
        {"id": {"$in": ticket_ids}},
        {"$set": updates}
    )
```

## 总结

### Knowledge Base Server核心
- **输入**：文本查询
- **处理**：向量化 → 相似度搜索
- **输出**：相关文档 + 分数

### Ticketing Server核心
- **输入**：工单信息
- **处理**：存储 → 跟踪 → 通知
- **输出**：工单对象 + 状态

### 协同工作
- KB找不到答案 → 自动创建工单
- 工单解决后 → 添加到KB
- 形成知识积累的闭环
