#!/usr/bin/env python3
"""
测试MCP服务器的示例脚本
演示如何使用Knowledge Base和Ticketing服务器
"""

import asyncio
import json


async def test_knowledge_base():
    """测试知识库服务器"""
    print("=" * 60)
    print("测试 Knowledge Base Server")
    print("=" * 60)
    
    # 模拟MCP调用
    print("\n1. 搜索知识库 - 找到答案")
    print("-" * 60)
    
    search_args = {
        "query": "密码",
        "top_k": 3
    }
    
    print(f"查询: {search_args['query']}")
    print("\n预期结果:")
    print("""
    {
      "results": [
        {
          "content": "要重置密码，请访问设置页面...",
          "score": 0.95,
          "metadata": {"title": "如何重置密码"}
        }
      ],
      "count": 1
    }
    """)
    
    print("\n2. 搜索知识库 - 未找到答案")
    print("-" * 60)
    
    search_args = {
        "query": "新功能不工作",
        "top_k": 5
    }
    
    print(f"查询: {search_args['query']}")
    print("\n预期结果:")
    print("""
    {
      "results": [],
      "count": 0
    }
    """)
    
    print("\n3. 添加到知识库")
    print("-" * 60)
    
    add_args = {
        "content": "要导出数据，点击设置 > 数据导出 > 选择格式",
        "metadata": {
            "title": "如何导出数据",
            "category": "数据管理",
            "tags": ["导出", "数据"]
        }
    }
    
    print(f"添加内容: {add_args['content'][:30]}...")
    print("\n预期结果:")
    print("""
    {
      "success": true,
      "id": "kb_20240130120000",
      "message": "内容已成功添加到知识库"
    }
    """)


async def test_ticketing():
    """测试工单服务器"""
    print("\n" + "=" * 60)
    print("测试 Ticketing Server")
    print("=" * 60)
    
    print("\n1. 创建工单")
    print("-" * 60)
    
    create_args = {
        "title": "用户无法登录",
        "description": "多个用户报告无法登录系统，显示'服务器错误'",
        "priority": "high",
        "labels": ["bug", "login", "urgent"]
    }
    
    print(f"标题: {create_args['title']}")
    print(f"优先级: {create_args['priority']}")
    print(f"标签: {create_args['labels']}")
    print("\n预期结果:")
    print("""
    {
      "success": true,
      "ticket": {
        "id": "TICKET-003",
        "title": "用户无法登录",
        "status": "open",
        "priority": "high",
        "created_at": "2024-01-30T10:00:00Z"
      }
    }
    """)
    
    print("\n2. 更新工单")
    print("-" * 60)
    
    update_args = {
        "ticket_id": "TICKET-003",
        "status": "in_progress",
        "assignee": "dev-team",
        "comment": "正在调查数据库连接问题"
    }
    
    print(f"工单ID: {update_args['ticket_id']}")
    print(f"新状态: {update_args['status']}")
    print(f"指派给: {update_args['assignee']}")
    print("\n预期结果:")
    print("""
    {
      "success": true,
      "ticket_id": "TICKET-003",
      "updated_fields": ["status", "assignee", "comment"]
    }
    """)
    
    print("\n3. 搜索工单")
    print("-" * 60)
    
    search_args = {
        "query": "登录",
        "status": "open",
        "priority": "high"
    }
    
    print(f"搜索: {search_args['query']}")
    print(f"过滤: status={search_args['status']}, priority={search_args['priority']}")
    print("\n预期结果:")
    print("""
    {
      "results": [
        {
          "id": "TICKET-003",
          "title": "用户无法登录",
          "status": "open",
          "priority": "high",
          "similarity": 0.95
        }
      ],
      "count": 1
    }
    """)
    
    print("\n4. 获取工单统计")
    print("-" * 60)
    print("\n预期结果:")
    print("""
    {
      "total": 3,
      "by_status": {
        "open": 1,
        "in_progress": 1,
        "resolved": 1
      },
      "by_priority": {
        "high": 2,
        "medium": 1
      },
      "unassigned": 1
    }
    """)


async def test_qa_workflow():
    """测试完整的QA工作流"""
    print("\n" + "=" * 60)
    print("测试完整QA工作流")
    print("=" * 60)
    
    print("\n场景1: 用户提问 - 知识库有答案")
    print("-" * 60)
    
    user_query = "如何重置密码？"
    print(f"用户查询: {user_query}")
    
    print("\n工作流:")
    print("1. 搜索知识库")
    print("   → 找到3个结果，最高分0.95")
    print("2. 生成答案")
    print("   → 置信度: 0.95 (>= 0.7)")
    print("3. 返回答案")
    print("   → 不创建工单")
    
    print("\n最终响应:")
    print("""
    "要重置密码，请访问设置页面，点击'安全'选项卡，
    然后选择'重置密码'。系统会发送验证邮件到您的注册邮箱。"
    """)
    
    print("\n场景2: 用户提问 - 知识库无答案")
    print("-" * 60)
    
    user_query = "新功能为什么不工作？"
    print(f"用户查询: {user_query}")
    
    print("\n工作流:")
    print("1. 搜索知识库")
    print("   → 找到0个结果")
    print("2. 生成答案")
    print("   → 置信度: 0.3 (< 0.7)")
    print("3. 创建工单")
    print("   → TICKET-004 (priority: medium)")
    print("4. 返回答案 + 工单")
    
    print("\n最终响应:")
    print("""
    "抱歉，我没有找到关于新功能的相关信息。
    我已经创建了工单 TICKET-004 来跟进您的问题，
    我们的团队会尽快回复您。"
    """)
    
    print("\n场景3: 用户报告问题 - 自动高优先级")
    print("-" * 60)
    
    user_query = "系统崩溃了！"
    print(f"用户查询: {user_query}")
    
    print("\n工作流:")
    print("1. 意图分类")
    print("   → intent: 'issue' (问题报告)")
    print("2. 搜索知识库")
    print("   → 找到1个结果，分数0.6")
    print("3. 生成答案")
    print("   → 置信度: 0.6 (< 0.7)")
    print("4. 创建工单")
    print("   → TICKET-005 (priority: HIGH - 因为是issue)")
    print("5. 返回答案 + 工单")
    
    print("\n最终响应:")
    print("""
    "我理解您遇到了系统崩溃的问题。这里是一些可能的解决方案...
    
    我已经创建了高优先级工单 TICKET-005，我们的技术团队会立即处理。"
    """)


async def test_integration_example():
    """集成示例：实际使用场景"""
    print("\n" + "=" * 60)
    print("实际集成示例")
    print("=" * 60)
    
    print("\n使用ChromaDB + OpenAI的完整示例:")
    print("-" * 60)
    
    code_example = '''
import chromadb
from openai import OpenAI

# 初始化
chroma_client = chromadb.Client()
kb_collection = chroma_client.create_collection("knowledge_base")
openai_client = OpenAI()

# 1. 添加文档到知识库
def add_document(content, metadata):
    # 生成embedding
    response = openai_client.embeddings.create(
        model="text-embedding-3-small",
        input=content
    )
    embedding = response.data[0].embedding
    
    # 存储到ChromaDB
    kb_collection.add(
        ids=[f"doc_{timestamp}"],
        documents=[content],
        embeddings=[embedding],
        metadatas=[metadata]
    )

# 2. 搜索知识库
def search_kb(query, top_k=5):
    # 生成查询embedding
    response = openai_client.embeddings.create(
        model="text-embedding-3-small",
        input=query
    )
    query_embedding = response.data[0].embedding
    
    # 搜索
    results = kb_collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )
    
    return results

# 3. QA流程
def qa_with_auto_ticketing(user_query):
    # 搜索知识库
    kb_results = search_kb(user_query, top_k=3)
    
    # 检查结果质量
    if kb_results and kb_results['distances'][0][0] < 0.3:  # 距离小=相似度高
        # 找到好答案
        return kb_results['documents'][0][0]
    else:
        # 未找到好答案，创建工单
        ticket = create_ticket(
            title=user_query,
            description=f"自动创建：知识库未找到答案\\n\\n查询：{user_query}",
            priority="medium"
        )
        
        return f"我已创建工单 {ticket['id']} 来跟进您的问题。"

# 使用
answer = qa_with_auto_ticketing("如何重置密码？")
print(answer)
'''
    
    print(code_example)
    
    print("\n使用GitHub Issues的工单集成:")
    print("-" * 60)
    
    github_example = '''
from github import Github

# 初始化GitHub客户端
g = Github("your_github_token")
repo = g.get_repo("your-org/your-repo")

# 创建工单（GitHub Issue）
def create_ticket(title, description, priority, labels):
    # 添加优先级标签
    all_labels = labels + [f"priority-{priority}"]
    
    # 创建issue
    issue = repo.create_issue(
        title=title,
        body=description,
        labels=all_labels
    )
    
    return {
        "id": f"TICKET-{issue.number}",
        "url": issue.html_url,
        "number": issue.number
    }

# 更新工单
def update_ticket(issue_number, comment=None, status=None):
    issue = repo.get_issue(issue_number)
    
    # 添加评论
    if comment:
        issue.create_comment(comment)
    
    # 更新状态（通过标签）
    if status == "closed":
        issue.edit(state="closed")
    
    return {"success": True}

# 搜索工单
def search_tickets(query, labels=None):
    query_str = f"repo:{repo.full_name} {query}"
    if labels:
        query_str += " " + " ".join([f"label:{l}" for l in labels])
    
    issues = g.search_issues(query_str)
    
    return [
        {
            "id": f"TICKET-{issue.number}",
            "title": issue.title,
            "status": issue.state,
            "url": issue.html_url
        }
        for issue in issues
    ]
'''
    
    print(github_example)


async def main():
    """运行所有测试"""
    await test_knowledge_base()
    await test_ticketing()
    await test_qa_workflow()
    await test_integration_example()
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)
    print("\n要运行实际的MCP服务器，请执行:")
    print("  python mcp-servers/knowledge-base-server/server.py")
    print("  python mcp-servers/ticketing-server/server.py")
    print("\n要在Kiro中使用，请配置 .kiro/settings/mcp.json")


if __name__ == "__main__":
    asyncio.run(main())
