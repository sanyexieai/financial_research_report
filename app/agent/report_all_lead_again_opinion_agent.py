
import yaml

from typing import Optional, Any, Mapping, Dict
from app.report_info import ReportInfo
from app.schema import Message

class ReportAllLeadAgainOpinionAgent:
    role: str = """你是一位顶级金融分析师和研报撰写首席研究员"""
    system_prompt: str = """你是一位顶级金融分析师和研报撰写首席研究员，分段大纲必须用```yaml包裹。"""
    messages: list[Mapping[str, Any]]

    def __init__(self, logger, llm):
        self.logger = logger
        self.llm = llm
        self.messages = []  # 初始化 messages 列表
        self.messages.append(
            Message.system_message(
                self.system_prompt
            ).to_dict()
        )

    def generate_report_opinion(self,report_info:ReportInfo,full_report:str):
        """生成研报大纲"""
        self.logger.info("📋 生成研报整体意见...")

        outline_prompt = f"""
           {self.role}。基于"{full_report}"研报内容，对每个章节给出修改意见。
           {report_info.outline_opinion}
            **重要要求：**
            1. 直接输出完整可用的研报内容
            2. 要求为用户提交的作文生成批评和建议
            3. 需提供详细建议，涵盖篇幅长度、内容深度、写作 风格等维度
            4. 内容要详实、专业，可直接使用
            5、不要重复之前问过的问题
            - 以yaml格式输出，务必用```yaml和```包裹整个yaml内容
            - 每一项为一个主要部分，每部分需包含：
                - opinion_report_title: 报告的章节标题
                - opinion_title: 批评和建议章节标题
                - opinion_desc: 批评和建议的内容
           """
        self.messages.append(
            Message.user_message(
                outline_prompt
            ).to_dict()
        )

        outline_list = self.llm.ask(
            self.messages,
            max_tokens=4096,
            temperature=0.3
        )

        try:
            if '```yaml' in outline_list:
                yaml_block = outline_list.split('```yaml')[1].split('```')[0]
            else:
                yaml_block = outline_list
            parts = yaml.safe_load(yaml_block)
            if isinstance(parts, dict):
                parts = list(parts.values())

            self.logger.info(f"📄 生成研报整体意见 内容: {parts}")
            return parts
        except Exception as e:
            self.logger.error(f"[生成研报整体意见yaml解析失败] {e}")
            return []