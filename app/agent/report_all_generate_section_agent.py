import yaml

from typing import Optional,List, Any, Mapping, Dict
from app.report_info import ReportInfo
from app.schema import Message
from app.tool import MCPClients


class ReportAllGenerateSectionAgent:
    role: str = """你是一位顶级金融分析师和研报撰写资深研究员"""
    system_prompt: str = """
    "你是一位顶级金融分析师和研报撰写资深研究员，专门生成完整可用的研报内容。输出必须是完整的研报正文，无需用户修改。严格禁止输出分隔符、建议性语言或虚构内容。只允许引用真实存在于【财务研报汇总内容】中的图片地址，严禁虚构、猜测、改编图片路径。如引用了不存在的图片，将被判为错误输出。"
    """
    messages: list[Mapping[str, Any]]

    def __init__(self, logger, llm):
        self.logger = logger
        self.llm = llm
        self.messages = []  # 初始化 messages 列表
        self.tools =[],
        self.messages.append(
            Message.system_message(
                self.system_prompt
            ).to_dict()
        )
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
    def clean_user_message(self):
        """清理用户输入的message"""
        self.messages = []  # 初始化 messages 列表
        self.messages.append(
            Message.system_message(
                self.system_prompt
            ).to_dict()
        )

    def generate_section(self, report_info: ReportInfo,full_report:str,  section_text_opinion):
        # 从数据库获取相关上下文
        section_prompt = f"""
        你是一位顶级金融分析师和研报撰写资深研究员。基于修改意见{section_text_opinion}直接修改"{full_report}"研报内容。
        **重要要求：**
        1. 直接输出完整可用的研报内容，
        2. 在正文中引用数据、事实等信息时，适当位置插入参考资料符号（如[1][2][3]）
        3. **图片引用要求（务必严格遵守）：**
           - 只允许引用【财务研报汇总内容】中真实存在的图片地址（格式如：./images/图片名字.png），必须与原文完全一致。
           - 禁止虚构、杜撰、改编、猜测图片地址，未在【财务研报汇总内容】中出现的图片一律不得引用。
           - 如需插入图片，必须先在【财务研报汇总内容】中查找，未找到则不插入图片，绝不编造图片。
           - 如引用了不存在的图片，将被判为错误输出。
        4. 不要输出任何【xxx开始】【xxx结束】等分隔符
        5. 不要输出\"建议补充\"、\"需要添加\"等提示性语言
        6. 不要编造图片地址或数据
        7. 内容要详实、专业，可直接使用
        8. 若用户提供批评反馈，需基于之前的尝试生成修改版本。    
        """
        self.messages.append(
            Message.user_message(
                section_prompt
            ).to_dict()
        )

        outline_list = self.llm.ask(
            self.messages,
            max_tokens=4096,
            temperature=0.3
        )

        return outline_list
