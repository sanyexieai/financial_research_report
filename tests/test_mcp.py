import os
import asyncio
from typing import Optional
from contextlib import AsyncExitStack
import json
import sys
from urllib.parse import urlparse

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.sse import sse_client

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class MCPClient:
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.openai = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"), base_url=os.getenv("OPENAI_BASE_URL")
        )
        self.model = os.getenv("OPENAI_MODEL")

    def get_response(self, messages: list, tools: list):
        response = self.openai.chat.completions.create(
            model=self.model,
            max_tokens=1000,
            messages=messages,
            tools=tools,
        )
        return response

    async def get_tools(self):
        response = await self.session.list_tools()
        available_tools = [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema,
                },
            }
            for tool in response.tools
        ]

        return available_tools

    async def connect_to_server(self, server_path: str = None):
        """连接到 MCP 服务器
        参数:
            server_path: 可以是以下三种形式之一:
                1. HTTP(S) URL - 使用 SSE 客户端连接
                2. 服务器脚本路径 (.py 或 .js)
                3. None - 使用默认的 mcp_server_fetch
        """
        try:
            if server_path and urlparse(server_path).scheme in ("http", "https"):
                print(f"正在连接到 SSE 服务器: {server_path}")
                sse_transport = await self.exit_stack.enter_async_context(
                    sse_client(server_path)
                )
                self.stdio, self.write = sse_transport

            else:
                if server_path:
                    is_python = server_path.endswith(".py")
                    is_js = server_path.endswith(".js")
                    if not (is_python or is_js):
                        raise ValueError("服务器脚本必须是 .py 或 .js 文件")

                    command = "python" if is_python else "node"
                    print(f"正在启动服务器: {command} {server_path}")
                    server_params = StdioServerParameters(
                        command=command, args=[server_path], env=None
                    )
                else:
                    print("正在启动默认 MCP 服务器…")
                    server_params = StdioServerParameters(
                        # command="npx",
                        # args=["/exports/git/tavily-mcp/build/index.js"],
                        # env={"TAVILY_API_KEY": "tvly-dev-xxx"}
                        #
                        # command="python",
                        # args=["-m", "mcp_server_fetch"],
                        # command="uvx",
                        # args=["mcp-server-fetch"],
                        #
                        command="uv",
                        args=[
                             "--directory",
                            "/Users/mac/Documents/ai/akshare-one-mcp/akshare-one-mcp/src/akshare_one_mcp",
                            "run",
                            "akshare-one-mcp"
                        ],
                        env={"BAIDU_MAPS_API_KEY": "xxx"},
                    )

                stdio_transport = await self.exit_stack.enter_async_context(
                    stdio_client(server_params)
                )
                self.stdio, self.write = stdio_transport

            self.session = await self.exit_stack.enter_async_context(
                ClientSession(self.stdio, self.write)
            )
            await self.session.initialize()

            response = await self.session.list_tools()
            tools = response.tools
            print("\n连接到服务器，工具列表:", [tool.name for tool in tools])
            print("服务器初始化完成")

        except Exception as e:
            print(f"连接服务器时出错: {str(e)}")
            raise

    async def process_query(self, query: str) -> str:
        """使用 OpenAI 和可用工具处理查询"""
        sys_content = """
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
        # 创建消息列表
        messages = [{"role": "system", "content": sys_content},{"role": "user", "content": query}]

        # 列出可用工具
        available_tools = await self.get_tools()
        # 处理消息
        response = self.get_response(messages, available_tools)

        # 处理LLM响应和工具调用
        tool_results = []
        final_text = []
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
                result = await self.session.call_tool(tool_name, tool_args)
                tool_results.append({"call": tool_name, "result": result})
                final_text.append(f"[Calling tool {tool_name} with args {tool_args}]")
                # 继续与工具结果进行对话
                if message.content and hasattr(message.content, "text"):
                    messages.append({"role": "assistant", "content": message.content})
                # 将工具调用结果添加到消息
                messages.append({"role": "user", "content": result.content})
                # 获取下一个LLM响应
                response = self.get_response(messages, available_tools)
                # 将结果添加到 final_text
                if response.choices[0].message.content:
                    final_text.append(response.choices[0].message.content)

        return "\\n".join(final_text)

    async def chat_loop(self):
        """运行交互式聊天循环（没有记忆）"""
        print("\\nMCP Client 启动!")
        print("输入您的查询或 'quit' 退出.")

        while True:
            try:
                query = input("\\nQuery: ").strip()

                if query.lower() == "quit":
                    break

                response = await self.process_query(query)
                print("\\n" + response)

            except Exception as e:
                import traceback

                traceback.print_exc()
                print(f"\\n错误: {str(e)}")

    async def cleanup(self):
        """清理资源"""
        await self.exit_stack.aclose()

async def main():
    """
    主函数：初始化并运行 MCP 客户端
    支持三种模式：
    1. python client.py <url>                    # 使用 SSE 连接
    2. python client.py <path_to_server_script>  # 使用自定义服务器脚本
    3. python client.py                          # 使用默认服务器
    """
    client = MCPClient()
    try:
        server_path = sys.argv[1] if len(sys.argv) > 1 else None
        await client.connect_to_server(server_path)
        await client.chat_loop()
    finally:
        await client.cleanup()

if __name__ == "__main__":
    asyncio.run(main())