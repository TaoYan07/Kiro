#!/usr/bin/env python3
"""
Knowledge Base MCP Server - Python实现
提供知识库搜索和管理功能
"""

import asyncio
import json
from typing import Any, Optional
from datetime import datetime

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent


class KnowledgeBaseServer:
    """知识库MCP服务器"""
    
    def __init__(self):
        self.server = Server("knowledge-base-server")
        
        # 模拟向量数据库存储（实际应使用ChromaDB、Pinecone等）
        self.knowledge_base = [
            {
                "id": "kb_001",
                "content": "要重置密码，请访问设置页面，点击'安全'选项卡，然后选择'重置密码'。",
                "metadata": {
                    "title": "如何重置密码",
                    "category": "账户管理",
                    "tags": ["密码", "安全", "账户"],
                    "created_at": "2024-01-15"
                },
                "embedding": [0.1, 0.2, 0.3]  # 模拟向量
            },
            {
                "id": "kb_002",
                "content": "要启用两步验证，进入设置 > 安全 > 两步验证，按照提示操作。",
                "metadata": {
                    "title": "启用两步验证",
                    "category": "安全",
                    "tags": ["2FA", "安全", "验证"],
                    "created_at": "2024-01-16"
                },
                "embedding": [0.15, 0.25, 0.35]
            },
            {
                "id": "kb_003",
                "content": "API限流设置为每分钟100次请求。超过限制会返回429错误。",
                "metadata": {
                    "title": "API限流说明",
                    "category": "API文档",
                    "tags": ["API", "限流", "错误"],
                    "created_at": "2024-01-17"
                },
                "embedding": [0.5, 0.6, 0.7]
            }
        ]
        
        self.setup_handlers()
    
    def setup_handlers(self):
        """设置请求处理器"""
        
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """列出所有可用工具"""
            return [
                Tool(
                    name="search_knowledge_base",
                    description="在知识库中搜索相关信息，使用语义搜索找到最相关的内容",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "搜索查询文本"
                            },
                            "top_k": {
                                "type": "number",
                                "description": "返回结果数量",
                                "default": 5
                            },
                            "filters": {
                                "type": "object",
                                "description": "可选过滤条件（category、tags等）",
                                "properties": {
                                    "category": {"type": "string"},
                                    "tags": {
                                        "type": "array",
                                        "items": {"type": "string"}
                                    }
                                }
                            }
                        },
                        "required": ["query"]
                    }
                ),
                Tool(
                    name="add_to_knowledge_base",
                    description="向知识库添加新内容",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "content": {
                                "type": "string",
                                "description": "要添加的内容"
                            },
                            "metadata": {
                                "type": "object",
                                "description": "元数据（标题、分类、标签等）",
                                "properties": {
                                    "title": {"type": "string"},
                                    "category": {"type": "string"},
                                    "tags": {
                                        "type": "array",
                                        "items": {"type": "string"}
                                    }
                                }
                            }
                        },
                        "required": ["content"]
                    }
                ),
                Tool(
                    name="get_knowledge_stats",
                    description="获取知识库统计信息",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                )
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Any) -> list[TextContent]:
            """处理工具调用"""
            
            if name == "search_knowledge_base":
                return await self.search_knowledge_base(arguments)
            elif name == "add_to_knowledge_base":
                return await self.add_to_knowledge_base(arguments)
            elif name == "get_knowledge_stats":
                return await self.get_knowledge_stats(arguments)
            else:
                raise ValueError(f"未知工具: {name}")
    
    async def search_knowledge_base(self, args: dict) -> list[TextContent]:
        """
        搜索知识库
        
        实际实现应该：
        1. 将查询文本转换为向量（使用OpenAI embeddings或本地模型）
        2. 在向量数据库中进行相似度搜索
        3. 应用过滤条件
        4. 返回top_k个最相关结果
        """
        query = args.get("query", "")
        top_k = args.get("top_k", 5)
        filters = args.get("filters", {})
        
        # 模拟向量搜索（实际应使用真实的向量相似度计算）
        results = []
        
        for item in self.knowledge_base:
            # 应用过滤条件
            if filters:
                if "category" in filters:
                    if item["metadata"].get("category") != filters["category"]:
                        continue
                
                if "tags" in filters:
                    item_tags = set(item["metadata"].get("tags", []))
                    filter_tags = set(filters["tags"])
                    if not item_tags.intersection(filter_tags):
                        continue
            
            # 模拟相似度分数（实际应计算余弦相似度）
            score = self._calculate_similarity(query, item["content"])
            
            results.append({
                "id": item["id"],
                "content": item["content"],
                "metadata": item["metadata"],
                "score": score
            })
        
        # 按分数排序并返回top_k
        results.sort(key=lambda x: x["score"], reverse=True)
        results = results[:top_k]
        
        response = {
            "success": True,
            "results": results,
            "count": len(results),
            "query": query,
            "filters_applied": filters
        }
        
        return [TextContent(
            type="text",
            text=json.dumps(response, ensure_ascii=False, indent=2)
        )]
    
    async def add_to_knowledge_base(self, args: dict) -> list[TextContent]:
        """向知识库添加新内容"""
        content = args.get("content", "")
        metadata = args.get("metadata", {})
        
        if not content:
            raise ValueError("内容不能为空")
        
        # 生成ID和时间戳
        kb_id = f"kb_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # 实际实现应该：
        # 1. 生成内容的向量表示
        # 2. 存储到向量数据库
        # 3. 更新索引
        
        new_item = {
            "id": kb_id,
            "content": content,
            "metadata": {
                **metadata,
                "created_at": datetime.now().isoformat()
            },
            "embedding": [0.0, 0.0, 0.0]  # 模拟向量
        }
        
        self.knowledge_base.append(new_item)
        
        response = {
            "success": True,
            "id": kb_id,
            "message": "内容已成功添加到知识库",
            "item": new_item
        }
        
        return [TextContent(
            type="text",
            text=json.dumps(response, ensure_ascii=False, indent=2)
        )]
    
    async def get_knowledge_stats(self, args: dict) -> list[TextContent]:
        """获取知识库统计信息"""
        categories = {}
        total_tags = set()
        
        for item in self.knowledge_base:
            category = item["metadata"].get("category", "未分类")
            categories[category] = categories.get(category, 0) + 1
            
            tags = item["metadata"].get("tags", [])
            total_tags.update(tags)
        
        response = {
            "total_items": len(self.knowledge_base),
            "categories": categories,
            "total_tags": len(total_tags),
            "tags": list(total_tags)
        }
        
        return [TextContent(
            type="text",
            text=json.dumps(response, ensure_ascii=False, indent=2)
        )]
    
    def _calculate_similarity(self, query: str, content: str) -> float:
        """
        计算相似度分数（简化版本）
        实际应使用向量余弦相似度
        """
        query_lower = query.lower()
        content_lower = content.lower()
        
        # 简单的关键词匹配
        query_words = set(query_lower.split())
        content_words = set(content_lower.split())
        
        if not query_words:
            return 0.0
        
        intersection = query_words.intersection(content_words)
        score = len(intersection) / len(query_words)
        
        return round(score, 2)
    
    async def run(self):
        """运行服务器"""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


async def main():
    """主函数"""
    server = KnowledgeBaseServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
