
import yaml

from typing import Optional, Any, Mapping, Dict
from app.report_info import ReportInfo
from app.schema import Message

class AgainGenerateOpinionAgent:
    role: str = """你是一位顶级金融分析师和研报撰写首席研究员"""
    system_prompt: str = """你是一位顶级金融分析师和研报撰写首席研究员，专门对可用的研报内容章节做出批评和建议。"""
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

    def clean_user_message(self):
        """清理用户输入的message"""
        self.messages = []  # 初始化 messages 列表
        self.messages.append(
            Message.system_message(
                self.system_prompt
            ).to_dict()
        )

    def generate_opinion(self,report_info:ReportInfo, part, prev_content, is_last, section_text, generated_names=None):
        part_title = part.get("part_title")
        if generated_names is None:
            generated_names = []
        user_prompt = f"""
        {self.role}。基于数据库中的相关信息，直接输出"{part_title}"这一部分的完整研报内容修改意见。
        【已生成章节】：{list(generated_names)}
        **重要要求：**
        1. 直接输出完整可用的研报内容，以"## {part_title}"开头
        2. 要求为用户提交的研报生成批评和建议
        3. 需提供详细建议，涵盖篇幅长度、内容深度、写作 风格等维度
        4. 内容要详实、专业，可直接使用
        5、不要重复之前问过的问题
        - 以yaml格式输出，务必用```yaml和```包裹整个yaml内容
        - 每一项为一个主要部分，每部分需包含：
          - opinion_title: 批评和建议章节标题
          - opinion_desc: 批评和建议的内容
         {report_info.report_evaluation_criteria}
        【本次任务】
        {part}
        【已生成前文】
        {prev_content}
        【本次要修改的文案】
        {section_text}
        【竞品公司相关信息】
        {report_info.rag_company}
        【数据库相关信息】
        {report_info.part_rag_context}
        如果不需要修改，请直接输出"无"
        """
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
        return outline_list
