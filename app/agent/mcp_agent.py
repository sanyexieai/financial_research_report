# -*- coding: utf-8 -*-
import json
import os
from contextlib import AsyncExitStack
from typing import List, Optional

from dotenv import load_dotenv
from openai import OpenAI

from app.tool.mcp_tool import MCPClients

load_dotenv()

class MCPAgent:

    # Initialize MCP tool collection
    mcp_clients: MCPClients = None

    system_prompt: str ="""
        You are an AI assistant with access to a Model Context Protocol (MCP) server.
You can use the tools provided by the MCP server to complete tasks.
The MCP server will dynamically expose tools that you can use - always check the available tools first.

When using an MCP tool:
1. Choose the appropriate tool based on your task requirements
2. Provide properly formatted arguments as required by the tool
3. Observe the results and use them to determine next steps
4. Tools may change during operation - new tools might appear or existing ones might disappear

Follow these guidelines:
- Call tools with valid parameters as documented in their schemas
- Handle errors gracefully by understanding what went wrong and trying again with corrected parameters
- For multimedia responses (like images), you'll receive a description of the content
- Complete user requests step by step, using the most appropriate tools
- If multiple tools need to be called in sequence, make one call at a time and wait for results

Remember to clearly explain your reasoning and actions to the user.
        """

    def __init__(self):
        self.openai = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"), base_url=os.getenv("OPENAI_BASE_URL")
        )
        self.model = os.getenv("OPENAI_MODEL")
        self.mcp_clients = None

    async def initialize(
        self,
        connection_type: Optional[str] = None,
        server_url: Optional[str] = None,
        command: Optional[str] = None,
        args: Optional[List[str]] = None,
        env: dict[str, str]=None

    ) -> None:
        """Initialize the MCP connection.

        Args:
            env:
            connection_type: Type of connection to use ("stdio" or "sse")
            server_url: URL of the MCP server (for SSE connection)
            command: Command to run (for stdio connection)
            args: Arguments for the command (for stdio connection)
        """
        self.mcp_clients = MCPClients()
        if connection_type:
            self.connection_type = connection_type

        # Connect to the MCP server based on connection type
        if self.connection_type == "sse":
            if not server_url:
                raise ValueError("Server URL is required for SSE connection")
            await self.mcp_clients.connect_sse(server_url=server_url)
        elif self.connection_type == "stdio":
            if not command:
                raise ValueError("Command is required for stdio connection")
            await self.mcp_clients.connect_stdio(command=command, args=args or [],env= env)
        else:
            raise ValueError(f"Unsupported connection type: {self.connection_type}")

        # Set available_tools to our MCP instance
        self.available_tools = self.mcp_clients

        # Store initial tool schemas
        # await self._refresh_tools()

        # Add system message about available tools
        tool_names = list(self.mcp_clients.tool_map.keys())
        tools_info = ", ".join(tool_names)

        # Add system prompt and available tools information
    

    async def get_response(self, messages: list, tools: list = None):
        response = self.openai.chat.completions.create(
            model=self.model,
            max_tokens=1000,
            messages=messages,
            tools=tools,
        )
        return response
   
    async def run(self, query:str)-> str:

        messages = [{"role": "system", "content":self.system_prompt},{"role": "user", "content": query}]
        # 列出可用工具
        available_tools = self.mcp_clients.to_params()
        response =  await self.get_response(messages,available_tools)

        final_text = []
        tool_results = []
        for choice in response.choices:
            message = choice.message
            is_function_call = message.tool_calls
            # 如果不调用工具，则添加到 final_text 中
            if not is_function_call:
                final_text.append(message.content)
            # 如果是工具调用，则获取工具名称和输入
            else:
               
                # 解包tool_calls
                tool_name = message.tool_calls[0].function.name
                tool_args = json.loads(message.tool_calls[0].function.arguments)
                print(f"准备调用工具: {tool_name}")
                print(f"参数: {json.dumps(tool_args, ensure_ascii=False, indent=2)}")
                # 执行工具调用，获取结果
                # result = await self.session.call_tool(tool_name, tool_args)
                result = await self.mcp_clients.session.call_tool(tool_name, tool_args)
                tool_results.append({"call": tool_name, "result": result})
                final_text.append(f"[Calling tool {tool_name} with args {tool_args}]")
                # 继续与工具结果进行对话
                if message.content and hasattr(message.content, "text"):
                    messages.append({"role": "assistant", "content": message.content})
                # 将工具调用结果添加到消息
                messages.append({"role": "user", "content": result.content})
                # 获取下一个LLM响应
                response = self.get_response(messages,available_tools)
                # 将结果添加到 final_text
                if response.choices[0].message.content:
                    final_text.append(response.choices[0].message.content)

        return "\\n".join(final_text)
