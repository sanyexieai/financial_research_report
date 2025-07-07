import asyncio
import unittest
from app.agent.mcp_agent import MCPAgent


async def run_mcp():
   agent = MCPAgent()
   # 使用 asyncio.run() 来启动异步逻辑
   await agent.initialize(
       connection_type="stdio",
       command="uv",
       args=[
             "--directory",
            "/Users/mac/Documents/ai/akshare-one-mcp/akshare-one-mcp/src/akshare_one_mcp",
            "run",
            "akshare-one-mcp"
        ],
       env={},
   )
   response = await agent.run("苏州银行")
   # asyncio.sleep(1000)
   print(f"准备调用工具: {response}")

            
if __name__ == "__main__":
    asyncio.run(run_mcp())