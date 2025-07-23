
from typing import List

import tiktoken
import yaml

from app.prompt.outline.generate_outline_edit_opinion import SYSTEM_PROMPT_OUTLINE_EDIT_OPINION, \
    USER_PROMPT_OUTLINE_EDIT_OPINION
from app.report_info import ReportInfo
from llm.schema import Message, Memory
from company.agent.token_counter import TokenCounter


class ReportGenerateOutlineEditOpinionAgent:
    system_prompt: str = SYSTEM_PROMPT_OUTLINE_EDIT_OPINION
        # """
        # 你是一位顶级金融分析师和研报撰写主管研究员，分段大纲必须用```yaml包裹。
        # """

    # llm: Optional[LLM] = Field(default_factory=LLM)

    # 移除这行有问题的类变量定义
    # memory: Memory = Field(default_factory=Memory)

    def __init__(self, logger, llm):
        self.logger = logger
        self.llm = llm
        self.total_input_tokens = 0
        self.total_completion_tokens = 0
        self.max_input_tokens = llm.config.max_tokens
        # 正确初始化 Memory 实例
        self.memory = Memory()
        # 修复：应该使用 self.memory 而不是 self.messages
        messages = [
            Message.system_message(  # 修复：应该使用 system_message 而不是 user_message
                self.system_prompt
            )
        ]
        self.memory.add_messages(messages)
        
        # 修复 tokenizer 初始化问题
        try:
            self.tokenizer = tiktoken.encoding_for_model(self.llm.config.model)
        except KeyError:
            # 如果模型不被支持，使用默认的 cl100k_base 编码（适用于大多数现代模型）
            self.logger.warning(f"模型 {self.llm.config.model} 不被 tiktoken 支持，使用默认编码 cl100k_base")
            self.tokenizer = tiktoken.get_encoding("cl100k_base")
        
        self.token_counter = TokenCounter(self.tokenizer)

    def generate_outline_opinion(self,report_info:ReportInfo):

        part = report_info.report_outline
        if not part:
            self.logger.info(f"未找到大纲，跳过")
            return []

        """生成研报大纲"""
        self.logger.info("📋 正在生成研报大纲意见...")

        # part_title = part.get("part_title")
        # part_central_idea = part.get("part_central_idea")
        # part_desc = part.get("part_desc")
        # subsections = part.get("subsections")
        # subsection_num = subsection.get("subsection_num")
        # subsection_title = subsection.get("subsection_title")
        # subsection_central_idea = subsection.get("subsection_central_idea")
        # subsection_desc = subsection.get("subsection_desc")


        user_prompt = USER_PROMPT_OUTLINE_EDIT_OPINION.format(
            target_company= report_info.target_company,
            part_title=report_info.report_title,
            outline_content=part,
        )
        messages = [
            Message.user_message(
                user_prompt
            )
        ]
        self.memory.add_messages(messages)
        self_messages = self.messages
        # 修复：将 Message 对象转换为 dict 格式
        messages_dict = [msg.to_dict() for msg in self_messages]
        input_tokens = self.count_message_tokens(messages_dict)
        self.logger.info(f"📋 输入tokens:{input_tokens}")
        # if not self.check_token_limit(input_tokens):
        #     error_message = self.get_limit_error_message(input_tokens)
        #     # Raise a special exception that won't be retried
        #     raise ValueError(error_message)
        self.logger.info(f"📋 提示词:{ self.memory.messages}")

        # 修复：应该传递 self.memory.messages 而不是 self.messages
        response = self.llm.ask(
            self.memory.messages,
            temperature=0.3
        )

        self.logger.info(f"📋 已生成研报大纲意见：{response}")
        try:
            if '```yaml' in response:
                yaml_block = response.split('```yaml')[1].split('```')[0]
            else:
                yaml_block = response
            result = yaml.safe_load(yaml_block)
            if isinstance(result, dict):
                result = list(result.values())
            self.logger.info(f"📄 生成大纲意见 内容: {result}")
            report_info.report_outline_opinion = result
            return result
        except Exception as e:
            self.logger.error(f"[大纲意见yaml解析失败] {e}")
            return []

    def count_message_tokens(self, messages: List[dict]) -> int:
        return self.token_counter.count_message_tokens(messages)

    def check_token_limit(self, input_tokens: int) -> bool:
        """Check if token limits are exceeded"""
        if self.max_input_tokens is not None:
            return (self.total_input_tokens + input_tokens) <= self.max_input_tokens
        # If max_input_tokens is not set, always return True
        return True

    def get_limit_error_message(self, input_tokens: int) -> str:
        """Generate error message for token limit exceeded"""
        if (
            self.max_input_tokens is not None
            and (self.total_input_tokens + input_tokens) > self.max_input_tokens
        ):
            return f"Request may exceed input token limit (Current: {self.total_input_tokens}, Needed: {input_tokens}, Max: {self.max_input_tokens})"

        return "Token limit exceeded"

    @property
    def messages(self) -> List[Message]:
        """Retrieve a list of messages from the agent's memory."""
        return self.memory.messages

    @messages.setter
    def messages(self, value: List[Message]):
        """Set the list of messages in the agent's memory."""
        self.memory.messages = value