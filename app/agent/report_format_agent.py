import yaml

from typing import Optional, Any, Mapping, Dict
from app.report_info import ReportInfo
from app.schema import Message


class ReportFormatAgent:
    system_prompt: str = """
    你是一位顶级金融分析师和研报撰写专家，分段大纲必须用```yaml包裹。
    """
    messages: list[Mapping[str, Any]]
    def __init__(self, logger,llm):
        self.logger = logger
        self.llm = llm
        self.messages = []  # 初始化 messages 列表
        self.messages.append(
            Message.system_message(
                self.system_prompt
            ).to_dict()
        )

    def format_check(self,report_info:ReportInfo,report):
        """生成生成选题"""
        self.logger.info("📋 生成选题...")
        outline_prompt = f"""
    你是一位顶级金融分析师和研报撰写首席专家。要对{report_info.report_format}公司研报格式检查，按照格式要求修改报告内容
     【研报内容】
     {report}
     {report_info.report_format}
    """
        self.messages.append(
            Message.user_message(
                outline_prompt
            ).to_dict()
        )

        response = self.llm.ask(
            self.messages,
            max_tokens=4096,
            temperature=0.3
        )
        return response
