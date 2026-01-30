#!/usr/bin/env python3
"""
Ticketing System MCP Server - Python实现
提供工单创建、更新和搜索功能
"""

import asyncio
import json
from typing import Any, Optional
from datetime import datetime
from enum import Enum

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent


class TicketStatus(str, Enum):
    """工单状态"""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class TicketPriority(str, Enum):
    """工单优先级"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TicketingServer:
    """工单系统MCP服务器"""
    
    def __init__(self):
        self.server = Server("ticketing-server")
        
        # 模拟工单数据库（实际应使用真实数据库或API）
        self.tickets = [
            {
                "id": "TICKET-001",
                "title": "登录页面加载缓慢",
                "description": "用户报告登录页面加载时间超过5秒",
                "status": TicketStatus.IN_PROGRESS,
                "priority": TicketPriority.HIGH,
                "labels": ["performance", "login"],
                "assignee": "dev-team",
                "created_at": "2024-01-20T10:00:00Z",
                "updated_at": "2024-01-21T14:30:00Z",
                "comments": [
                    {
                        "author": "system",
                        "text": "工单已创建",
                        "timestamp": "2024-01-20T10:00:00Z"
                    }
                ]
            },
            {
                "id": "TICKET-002",
                "title": "API文档缺失",
                "description": "新的v2 API缺少详细文档",
                "status": TicketStatus.OPEN,
                "priority": TicketPriority.MEDIUM,
                "labels": ["documentation", "api"],
                "assignee": None,
                "created_at": "2024-01-22T09:15:00Z",
                "updated_at": "2024-01-22T09:15:00Z",
                "comments": []
            }
        ]
        
        self.ticket_counter = 3  # 下一个工单编号
        
        self.setup_handlers()
    
    def setup_handlers(self):
        """设置请求处理器"""
        
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """列出所有可用工具"""
            return [
                Tool(
                    name="create_ticket",
                    description="创建新的支持工单",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "工单标题"
                            },
                            "description": {
                                "type": "string",
                                "description": "详细描述"
                            },
                            "priority": {
                                "type": "string",
                                "enum": ["low", "medium", "high", "urgent"],
                                "default": "medium",
                                "description": "优先级"
                            },
                            "labels": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "工单标签/标记"
                            },
                            "assignee": {
                                "type": "string",
                                "description": "可选的指派人用户名"
                            }
                        },
                        "required": ["title", "description"]
                    }
                ),
                Tool(
                    name="update_ticket",
                    description="更新现有工单",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "ticket_id": {
                                "type": "string",
                                "description": "工单ID"
                            },
                            "status": {
                                "type": "string",
                                "enum": ["open", "in_progress", "resolved", "closed"],
                                "description": "更新状态"
                            },
                            "priority": {
                                "type": "string",
                                "enum": ["low", "medium", "high", "urgent"],
                                "description": "更新优先级"
                            },
                            "assignee": {
                                "type": "string",
                                "description": "更新指派人"
                            },
                            "comment": {
                                "type": "string",
                                "description": "添加评论"
                            },
                            "labels": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "更新标签"
                            }
                        },
                        "required": ["ticket_id"]
                    }
                ),
                Tool(
                    name="search_tickets",
                    description="搜索现有工单",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "搜索查询"
                            },
                            "status": {
                                "type": "string",
                                "enum": ["open", "in_progress", "resolved", "closed"],
                                "description": "按状态过滤"
                            },
                            "priority": {
                                "type": "string",
                                "enum": ["low", "medium", "high", "urgent"],
                                "description": "按优先级过滤"
                            },
                            "labels": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "按标签过滤"
                            },
                            "assignee": {
                                "type": "string",
                                "description": "按指派人过滤"
                            }
                        },
                        "required": ["query"]
                    }
                ),
                Tool(
                    name="get_ticket",
                    description="获取单个工单的详细信息",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "ticket_id": {
                                "type": "string",
                                "description": "工单ID"
                            }
                        },
                        "required": ["ticket_id"]
                    }
                ),
                Tool(
                    name="get_ticket_stats",
                    description="获取工单统计信息",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                )
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Any) -> list[TextContent]:
            """处理工具调用"""
            
            if name == "create_ticket":
                return await self.create_ticket(arguments)
            elif name == "update_ticket":
                return await self.update_ticket(arguments)
            elif name == "search_tickets":
                return await self.search_tickets(arguments)
            elif name == "get_ticket":
                return await self.get_ticket(arguments)
            elif name == "get_ticket_stats":
                return await self.get_ticket_stats(arguments)
            else:
                raise ValueError(f"未知工具: {name}")
    
    async def create_ticket(self, args: dict) -> list[TextContent]:
        """
        创建新工单
        
        实际实现应该：
        1. 验证输入数据
        2. 调用外部API（GitHub Issues、Jira、Linear等）
        3. 存储到数据库
        4. 发送通知
        """
        title = args.get("title", "")
        description = args.get("description", "")
        priority = args.get("priority", "medium")
        labels = args.get("labels", [])
        assignee = args.get("assignee")
        
        if not title or not description:
            raise ValueError("标题和描述不能为空")
        
        # 生成工单ID
        ticket_id = f"TICKET-{str(self.ticket_counter).zfill(3)}"
        self.ticket_counter += 1
        
        # 创建工单对象
        now = datetime.now().isoformat() + "Z"
        ticket = {
            "id": ticket_id,
            "title": title,
            "description": description,
            "status": TicketStatus.OPEN,
            "priority": priority,
            "labels": labels,
            "assignee": assignee,
            "created_at": now,
            "updated_at": now,
            "comments": [
                {
                    "author": "system",
                    "text": "工单已自动创建",
                    "timestamp": now
                }
            ]
        }
        
        # 存储工单
        self.tickets.append(ticket)
        
        # 实际实现中，这里应该：
        # - 调用GitHub API创建issue
        # - 或调用Jira API创建ticket
        # - 或调用Linear API创建issue
        # - 发送邮件/Slack通知
        
        response = {
            "success": True,
            "ticket": ticket,
            "message": f"工单 {ticket_id} 创建成功"
        }
        
        return [TextContent(
            type="text",
            text=json.dumps(response, ensure_ascii=False, indent=2)
        )]
    
    async def update_ticket(self, args: dict) -> list[TextContent]:
        """更新工单"""
        ticket_id = args.get("ticket_id", "")
        status = args.get("status")
        priority = args.get("priority")
        assignee = args.get("assignee")
        comment = args.get("comment")
        labels = args.get("labels")
        
        # 查找工单
        ticket = None
        for t in self.tickets:
            if t["id"] == ticket_id:
                ticket = t
                break
        
        if not ticket:
            raise ValueError(f"工单 {ticket_id} 不存在")
        
        # 更新字段
        updated_fields = []
        
        if status:
            ticket["status"] = status
            updated_fields.append("status")
        
        if priority:
            ticket["priority"] = priority
            updated_fields.append("priority")
        
        if assignee is not None:
            ticket["assignee"] = assignee
            updated_fields.append("assignee")
        
        if labels is not None:
            ticket["labels"] = labels
            updated_fields.append("labels")
        
        # 添加评论
        if comment:
            ticket["comments"].append({
                "author": "user",
                "text": comment,
                "timestamp": datetime.now().isoformat() + "Z"
            })
            updated_fields.append("comment")
        
        # 更新时间戳
        ticket["updated_at"] = datetime.now().isoformat() + "Z"
        
        response = {
            "success": True,
            "ticket_id": ticket_id,
            "updated_fields": updated_fields,
            "ticket": ticket,
            "message": f"工单 {ticket_id} 更新成功"
        }
        
        return [TextContent(
            type="text",
            text=json.dumps(response, ensure_ascii=False, indent=2)
        )]
    
    async def search_tickets(self, args: dict) -> list[TextContent]:
        """搜索工单"""
        query = args.get("query", "").lower()
        status_filter = args.get("status")
        priority_filter = args.get("priority")
        labels_filter = args.get("labels", [])
        assignee_filter = args.get("assignee")
        
        results = []
        
        for ticket in self.tickets:
            # 文本搜索
            if query:
                searchable_text = (
                    ticket["title"].lower() + " " +
                    ticket["description"].lower()
                )
                if query not in searchable_text:
                    continue
            
            # 状态过滤
            if status_filter and ticket["status"] != status_filter:
                continue
            
            # 优先级过滤
            if priority_filter and ticket["priority"] != priority_filter:
                continue
            
            # 标签过滤
            if labels_filter:
                ticket_labels = set(ticket["labels"])
                filter_labels = set(labels_filter)
                if not ticket_labels.intersection(filter_labels):
                    continue
            
            # 指派人过滤
            if assignee_filter and ticket["assignee"] != assignee_filter:
                continue
            
            # 计算相似度分数（简化版）
            similarity = self._calculate_ticket_similarity(query, ticket)
            
            results.append({
                **ticket,
                "similarity": similarity
            })
        
        # 按相似度排序
        results.sort(key=lambda x: x["similarity"], reverse=True)
        
        response = {
            "success": True,
            "results": results,
            "count": len(results),
            "query": query,
            "filters": {
                "status": status_filter,
                "priority": priority_filter,
                "labels": labels_filter,
                "assignee": assignee_filter
            }
        }
        
        return [TextContent(
            type="text",
            text=json.dumps(response, ensure_ascii=False, indent=2)
        )]
    
    async def get_ticket(self, args: dict) -> list[TextContent]:
        """获取单个工单详情"""
        ticket_id = args.get("ticket_id", "")
        
        ticket = None
        for t in self.tickets:
            if t["id"] == ticket_id:
                ticket = t
                break
        
        if not ticket:
            raise ValueError(f"工单 {ticket_id} 不存在")
        
        response = {
            "success": True,
            "ticket": ticket
        }
        
        return [TextContent(
            type="text",
            text=json.dumps(response, ensure_ascii=False, indent=2)
        )]
    
    async def get_ticket_stats(self, args: dict) -> list[TextContent]:
        """获取工单统计信息"""
        stats = {
            "total": len(self.tickets),
            "by_status": {},
            "by_priority": {},
            "by_assignee": {},
            "unassigned": 0
        }
        
        for ticket in self.tickets:
            # 按状态统计
            status = ticket["status"]
            stats["by_status"][status] = stats["by_status"].get(status, 0) + 1
            
            # 按优先级统计
            priority = ticket["priority"]
            stats["by_priority"][priority] = stats["by_priority"].get(priority, 0) + 1
            
            # 按指派人统计
            assignee = ticket.get("assignee")
            if assignee:
                stats["by_assignee"][assignee] = stats["by_assignee"].get(assignee, 0) + 1
            else:
                stats["unassigned"] += 1
        
        response = {
            "success": True,
            "stats": stats
        }
        
        return [TextContent(
            type="text",
            text=json.dumps(response, ensure_ascii=False, indent=2)
        )]
    
    def _calculate_ticket_similarity(self, query: str, ticket: dict) -> float:
        """计算工单与查询的相似度"""
        if not query:
            return 1.0
        
        query_words = set(query.lower().split())
        ticket_text = (ticket["title"] + " " + ticket["description"]).lower()
        ticket_words = set(ticket_text.split())
        
        if not query_words:
            return 0.0
        
        intersection = query_words.intersection(ticket_words)
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
    server = TicketingServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
