
import yaml

from typing import Optional, Any, Mapping, Dict
from app.report_info import ReportInfo
from app.schema import Message

class GenerateOutlineAgent:
    system_prompt: str = """
        你是一位顶级金融分析师和研报撰写主管研究员，分段大纲必须用```yaml包裹。
        """
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

    def generate_outline(self,report_info:ReportInfo, first_select_topic):
        """生成研报大纲"""
        self.logger.info("📋 生成研报大纲...")

        user_prompt = f"""
    【背景说明开始】
    {report_info.background}
    你是一位顶级金融分析师和研报撰写专家。提供相关研报选题，从中选择这个题目。请基于数据库中的相关信息和修改意见，生成一份详尽的《{report_info.report_title}》公司研报分段大纲，要求：
    {report_info.outline_info_content_format}
    {report_info.report_evaluation_criteria}
    {report_info.requirement}
    {report_info.outline}
    【研报选题】
    {first_select_topic}
    【竞品公司相关信息】
     {report_info.rag_company}
    【数据库相关信息】
      {report_info.rag_context}
    """
        self.logger.info(f"📋 修改研报提示词{user_prompt}")
        self.messages.append(
            Message.user_message(
                user_prompt
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
            self.logger.info(f"📄 生成研报大纲 内容: {parts}")
            return parts
        except Exception as e:
            self.logger.error(f"[大纲yaml解析失败] {e}")
            return []