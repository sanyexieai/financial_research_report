import yaml

from typing import Optional, Any, Mapping, Dict
from app.report_info import ReportInfo
from app.schema import Message


class SelectedTopicAgent:

    role: str = """你是一位顶级金融分析师和研报撰写首席研究员"""
    system_prompt: str = """你是一位顶级金融分析师和研报撰写首席研究员，分段大纲必须用```yaml包裹。"""
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

    def selected_topic(self,report_info:ReportInfo):
        """生成生成选题"""
        self.logger.info("📋 生成选题...")
        outline_prompt = f"""
    {self.role}。基于数据库中的相关信息，对{report_info.target_company}公司研报的选题：
    证券研究报告的基本要素包括：宏观经济、行业或上市公司的基本面分析;上市公司盈利预测、法规解读、估值及投资评级;相关信息披露和风险提示。其中，投资评级是基于基本面分析而作出的估值定价建议，不是具体的操作性买卖建议。
    - 以yaml格式输出，务必用```yaml和```包裹整个yaml内容
    - 每一项为一个主要部分，每部分需包含：
      - report_title: 研究问题（必须有公司名称）   
      - report_target: 研究目标
      - report_reason: 研究原因
      - report_desc: 数据支持
    【背景说明开始】
    {report_info.background}
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
            return parts
        except Exception as e:
            self.logger.error(f"[选题yaml解析失败] {e}")
            return []