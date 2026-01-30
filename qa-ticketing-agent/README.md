# QA Answering & Auto-Ticketing Agent

一个智能代理系统，从知识库回答问题，并在需要时自动创建工单。

## 🎯 核心功能

- **智能问答**：从知识库搜索答案，使用语义搜索
- **自动工单**：当无法回答时自动创建工单
- **意图识别**：区分问题、报告、请求
- **优先级管理**：根据问题类型自动设置优先级

## 📋 架构

- **Workflow Engine**: Dify风格的工作流编排
- **MCP Servers**: 模块化工具（知识库搜索、工单创建）
- **Agent Logic**: QA和工单流程的智能路由

## 🗂️ 项目结构

```
.
├── workflow/                    # 工作流定义
│   ├── qa-ticketing-flow.json  # QA工作流配置
│   └── workflow-engine.ts      # 工作流引擎
│
├── mcp-servers/                 # MCP服务器
│   ├── knowledge-base-server/  # 知识库服务器
│   │   ├── server.py           # Python实现 ⭐
│   │   └── src/index.ts        # TypeScript实现
│   ├── ticketing-server/       # 工单服务器
│   │   ├── server.py           # Python实现 ⭐
│   │   └── src/index.ts        # TypeScript实现
│   ├── requirements.txt        # Python依赖
│   ├── test_servers.py         # 测试脚本
│   └── README_CN.md            # 中文说明
│
├── docs/                        # 文档
│   ├── ARCHITECTURE.md         # 架构说明
│   ├── QA-TICKETING-FLOW-DIAGRAM.md      # 流程图 ⭐
│   ├── MCP-SERVERS-LOGIC-CN.md           # 服务器逻辑详解 ⭐
│   ├── PYTHON-IMPLEMENTATION-CN.md       # Python实现说明 ⭐
│   └── SERVERS-COMPARISON-CN.md          # TS vs Python对比 ⭐
│
├── config/                      # 配置文件
│   ├── mcp.json                # TypeScript MCP配置
│   └── mcp-python.json         # Python MCP配置
│
└── .env.example                # 环境变量示例
```

## 🚀 快速开始

### 选项1：使用Python实现（推荐用于AI功能）

```bash
# 1. 安装Python依赖
pip install mcp

# 可选：安装AI库
pip install chromadb openai PyGithub

# 2. 配置环境变量
cp .env.example .env
# 编辑.env，填写API密钥

# 3. 配置MCP服务器
# 在 .kiro/settings/mcp.json 中添加：
{
  "mcpServers": {
    "knowledge-base": {
      "command": "python",
      "args": ["mcp-servers/knowledge-base-server/server.py"]
    },
    "ticketing": {
      "command": "python",
      "args": ["mcp-servers/ticketing-server/server.py"]
    }
  }
}

# 4. 测试服务器
python mcp-servers/test_servers.py
```

### 选项2：使用TypeScript实现

```bash
# 1. 安装依赖
npm install

# 2. 配置MCP服务器
# 使用 config/mcp.json

# 3. 运行
npm run build
```

## 📚 核心文档

### 🎯 快速导航

- **看图理解系统** → [可视化总结](docs/VISUAL-SUMMARY-CN.md) ⭐⭐⭐
- **理解工作流程** → [流程图](docs/QA-TICKETING-FLOW-DIAGRAM.md) ⭐⭐⭐
- **深入理解逻辑** → [服务器逻辑详解](docs/MCP-SERVERS-LOGIC-CN.md) ⭐⭐⭐
- **开始使用Python** → [Python实现说明](docs/PYTHON-IMPLEMENTATION-CN.md) ⭐⭐⭐
- **选择技术栈** → [TypeScript vs Python对比](docs/SERVERS-COMPARISON-CN.md) ⭐⭐
- **查看完整总结** → [总结文档](docs/SUMMARY-CN.md) ⭐⭐⭐
- **文档导航** → [文档索引](docs/INDEX-CN.md) 📚

### 必读文档

1. **[可视化总结](docs/VISUAL-SUMMARY-CN.md)** ⭐⭐⭐
   - 系统架构图
   - 数据流动图
   - 向量搜索原理
   - 决策树和性能指标

2. **[流程图和架构](docs/QA-TICKETING-FLOW-DIAGRAM.md)** ⭐⭐⭐
   - 完整的系统流程图
   - 6步工作流程
   - 3个实际场景示例

3. **[MCP服务器逻辑详解](docs/MCP-SERVERS-LOGIC-CN.md)** ⭐⭐⭐
   - Knowledge Base Server工作原理
   - Ticketing Server工作原理
   - 向量搜索和相似度计算
   - 实际集成示例

4. **[Python实现说明](docs/PYTHON-IMPLEMENTATION-CN.md)** ⭐⭐⭐
   - 快速开始指南
   - 使用示例
   - 集成ChromaDB和GitHub
   - 性能优化建议

5. **[完整总结](docs/SUMMARY-CN.md)** ⭐⭐⭐
   - 核心逻辑详解
   - 三个典型场景
   - 技术实现细节
   - 使用指南

## 🔄 工作流程

```
用户提问
    ↓
1. 意图分类（question/issue/request）
    ↓
2. 搜索知识库（向量搜索）
    ↓
3. 生成答案（LLM）
    ↓
4. 置信度检查
    ├─ 高置信度（≥0.7）→ 返回答案
    └─ 低置信度（<0.7）→ 创建工单 + 返回答案
```

## 💡 使用示例

### 场景1：找到答案

```
输入: "如何重置密码？"

处理:
  1. 搜索知识库 → 找到3个结果（最高分0.95）
  2. 生成答案 → 置信度0.95
  3. 返回答案 ✓

输出: "要重置密码，请访问设置页面..."
```

### 场景2：未找到答案，自动创建工单

```
输入: "新功能为什么不工作？"

处理:
  1. 搜索知识库 → 0个结果
  2. 生成答案 → 置信度0.3
  3. 创建工单 → TICKET-004
  4. 返回答案 + 工单ID ✓

输出: "抱歉，我没有找到相关信息。
       我已创建工单 TICKET-004 来跟进您的问题。"
```

## 🔧 MCP服务器

### Knowledge Base Server（知识库服务器）

**功能：**
- `search_knowledge_base` - 语义搜索
- `add_to_knowledge_base` - 添加内容
- `get_knowledge_stats` - 统计信息

**技术栈：**
- 向量嵌入（OpenAI embeddings）
- 向量数据库（ChromaDB/Pinecone）
- 余弦相似度搜索

### Ticketing Server（工单服务器）

**功能：**
- `create_ticket` - 创建工单
- `update_ticket` - 更新工单
- `search_tickets` - 搜索工单
- `get_ticket` - 获取工单详情
- `get_ticket_stats` - 统计信息

**集成：**
- GitHub Issues
- Jira
- Linear

## 🎓 核心概念

### 向量搜索

```python
# 1. 文本 → 向量
"如何重置密码" → [0.12, 0.34, 0.56, ..., 0.78]

# 2. 计算相似度
cosine_similarity(query_vec, doc_vec) = 0.95

# 3. 返回最相关结果
```

### 自动工单触发条件

- ❌ 知识库无结果
- ❌ 答案置信度 < 0.7
- ❌ 用户报告问题（intent=issue）

## 📊 性能优化

```python
# 1. 缓存热门查询
@lru_cache(maxsize=1000)
def search_cache(query):
    return search_kb(query)

# 2. 批量处理
embeddings = openai.embeddings.create(
    input=[doc1, doc2, doc3, ...]
)

# 3. 异步操作
asyncio.create_task(send_notifications(ticket))
```

## 🔌 集成示例

### ChromaDB + OpenAI

```python
import chromadb
from openai import OpenAI

client = chromadb.Client()
collection = client.create_collection("kb")

# 添加文档
response = openai_client.embeddings.create(
    model="text-embedding-3-small",
    input="文档内容"
)
collection.add(
    documents=["文档内容"],
    embeddings=[response.data[0].embedding]
)

# 搜索
results = collection.query(
    query_embeddings=[query_embedding],
    n_results=5
)
```

### GitHub Issues

```python
from github import Github

g = Github("token")
repo = g.get_repo("owner/repo")

# 创建工单
issue = repo.create_issue(
    title="Bug报告",
    body="详细描述",
    labels=["bug", "high-priority"]
)
```

## 🧪 测试

```bash
# 运行测试脚本（查看示例输出）
python mcp-servers/test_servers.py

# 直接运行服务器
python mcp-servers/knowledge-base-server/server.py
python mcp-servers/ticketing-server/server.py
```

## 📖 更多资源

- [MCP协议文档](https://modelcontextprotocol.io)
- [ChromaDB文档](https://docs.trychroma.com)
- [OpenAI Embeddings](https://platform.openai.com/docs/guides/embeddings)
- [PyGithub文档](https://pygithub.readthedocs.io)

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可

MIT License
