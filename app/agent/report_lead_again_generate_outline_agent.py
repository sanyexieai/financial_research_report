
import yaml

from typing import Optional, Any, Mapping, Dict
from app.report_info import ReportInfo
from app.schema import Message

class AgainGenerateOutlineAgent:
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

    def generate_outline_opinion(self,report_info:ReportInfo,parts):
        """生成研报大纲"""
        self.logger.info("📋 生成研报大纲意见...")

        outline_prompt = f"""
           {self.role}。基于研究员编写的研报大纲内容，修改一份详尽的《{report_info.target_company}》公司研报分段大纲，可以添加、删除、修改部分内容，要求：
           
           {report_info.outline_info_content_format}
            【大纲】
            {parts}
            【背景说明开始】
            {report_info.background}
            【竞品公司相关信息】
            {report_info.rag_company}  
            【数据库相关信息】
            {report_info.rag_context}
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

            self.logger.info(f"📄 生成研报大纲意见 内容: {parts}")
            return parts
        except Exception as e:
            self.logger.error(f"[生成研报大纲意见yaml解析失败] {e}")
            return []