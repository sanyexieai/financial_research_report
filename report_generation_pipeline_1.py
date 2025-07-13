#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
研报生成流程
基于PostgreSQL数据库中的数据，生成深度研报并输出为markdown格式
"""

import os
import glob
import time
import json
import yaml
import logging
from datetime import datetime
from dotenv import load_dotenv

from app.agent.report_all_lead_again_opinion_agent import ReportAllLeadAgainOpinionAgent
from app.agent.report_format_agent import ReportFormatAgent
from app.agent.report_generate_outline_modify_agent import GenerateOutlineModifyAgent
from app.agent.report_generate_section_modify_agent import ReportGenerateSectionModifyAgent
from app.agent.report_lead_again_generate_outline_agent import AgainGenerateOutlineAgent
from app.agent.report_lead_generate_opinion_agent import AgainGenerateOpinionAgent
from app.agent.report_generate_outline_agent import GenerateOutlineAgent
from app.agent.report_generate_section_agent import GenerateSectionAgent
from app.agent.report_lead_selected_topic_agent import SelectedTopicAgent
from app.report_info import ReportInfo
from data_analysis_agent import quick_analysis
from data_analysis_agent.config.llm_config import LLMConfig
from data_analysis_agent.utils.llm_helper import LLMHelper
from utils.rag_postgres import RAGPostgresHelper
from config.database_config import db_config

class ReportGenerationPipeline:
    """研报生成流程类"""
    report_info: ReportInfo

    def __init__(self, target_company="商汤科技", target_company_code="00020", target_company_market="HK"):
        # 配置日志记录
        self.setup_logging()
        
        # 环境变量与全局配置
        load_dotenv()
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4")
        
        self.logger.info(f"🔧 使用的模型: {self.model}")
        self.target_company = target_company
        self.target_company_code = target_company_code
        self.target_company_market = target_company_market
        
        # 目录配置
        self.data_dir = "./download_financial_statement_files"
        
        # LLM配置
        self.llm_config = LLMConfig(
            api_key=self.api_key,
            base_url=self.base_url,
            model=self.model,
            temperature=0.7,
            max_tokens=8192,
        )
        self.llm = LLMHelper(self.llm_config)

        # 初始化PostgreSQL RAG助手
        try:
            self.logger.info("🔗 初始化PostgreSQL RAG助手...")
            self.rag_helper = RAGPostgresHelper(
                db_config=db_config.get_postgres_config(),
                rag_config=db_config.get_rag_config()
            )
            self.logger.info("✅ PostgreSQL RAG助手初始化成功")
        except Exception as e:
            self.logger.error(f"❌ PostgreSQL RAG助手初始化失败: {e}")
            raise
    
    def setup_logging(self):
        """配置日志记录"""
        os.makedirs("logs", exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_filename = f"logs/report_generation_{timestamp}.log"
        
        self.logger = logging.getLogger('ReportGeneration')
        self.logger.setLevel(logging.INFO)
        self.logger.handlers.clear()
        
        file_handler = logging.FileHandler(log_filename, encoding='utf-8')
        console_handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        self.logger.info(f"📝 日志记录已启动，日志文件: {log_filename}")


    def do_generate_outline(self):
        # 1. 生成选题
        # select_topic = SelectedTopicAgent(self.logger, self.llm).selected_topic(self.report_info)
        # self.logger.info(f"📄 select_parts 内容: {select_topic}")
        # first_select_topic = select_topic[0]
        #
        # self.logger.info(f"📄 选题 内容: {first_select_topic.get('report_title')}")
        # self.report_info.report_title = first_select_topic.get('report_title')

        # 1. 讨论大纲内容
        generate_outline_agent = GenerateOutlineAgent(self.logger, self.llm)
        generate_outline_modify_agent = GenerateOutlineModifyAgent(self.logger, self.llm)

        again_generate_outline_agent = AgainGenerateOutlineAgent(self.logger, self.llm)
        parts_count = 0
        parts = generate_outline_agent.generate_outline(
                self.report_info, ""
            )
        self.logger.info(f"📄 初始 parts 内容: {parts}")
        # parts_opinion = []
        # while parts_count < 1:
        #     parts =generate_outline_modify_agent.generate_outline_modify(self.report_info, parts, parts_opinion)
        #     parts_opinion = again_generate_outline_agent.generate_outline_opinion(self.report_info, parts)
        #     self.report_info.outline_info = parts
        #     parts_count += 1

        self.logger.info(f"📄 最终 parts 内容: {parts}")
        if not parts:
            self.logger.error("❌ 大纲生成失败")
            return None
        return  parts

    def modify_generate_report(self,final_report):

        # 3. 修改深度研报
        generated_names = set()
        modify_opinion_agent = ReportAllLeadAgainOpinionAgent(self.logger, self.llm)
        modify_report_opinion = modify_opinion_agent.generate_report_opinion(self.report_info, final_report)
        report_generate_section_modify_agent = ReportGenerateSectionModifyAgent(self.logger, self.llm, self.rag_helper)

        modify_report_opinion_map = {item["opinion_report_title"]: item for item in modify_report_opinion}

        modify_full_report = [f"# {self.report_info.report_title}\n"]
        modify_prev_content = ''
        for idx, part in enumerate(self.report_info.report_parts):
            part_title = part.get('part_title', f'部分{idx + 1}')
            part_num = part.get('part_num', f'部分{idx + 1}')
            part_content = part.get('part_content', f'部分{idx + 1}')
            self.logger.info(f"\n  正在生成修改后：{part_num} ,{part_title}")
            is_last = (idx == len(self.report_info.report_parts) - 1)
            modify_opinion = modify_report_opinion_map.get(part_title)
            if modify_opinion:
                section_text = report_generate_section_modify_agent.generate_section(self.report_info, part,
                                                                                     modify_prev_content, is_last,
                                                                                     modify_opinion,
                                                                                     list(generated_names))
                modify_full_report.append(section_text)
                self.logger.info(f"  ✅ 已完成：{part_num} ,{part_title}")
            else:
                self.logger.info(f"  ✅ 无需修改：{part_num} ,{part_title}")
        # 3. 保存最终报告
        modify_final_report = '\n\n'.join(modify_full_report)
        modify_output_file = f"{self.target_company}深度研报_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(modify_output_file, 'w', encoding='utf-8') as f:
            f.write(modify_final_report)

        # report_format_agent = ReportFormatAgent(self.logger, self.llm)
        # check_report = report_format_agent.format_check(report_info, final_report)
        # output_check_file = f"{self.target_company}深度研报格式_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        # with open(output_check_file, 'w', encoding='utf-8') as f:
        #     f.write(check_report)

        self.logger.info(f"\n✅ 研报生成完成！文件已保存到: {modify_output_file}")

    def generate_report(self):
        """生成完整研报"""
        self.logger.info("\n" + "="*80)
        self.logger.info("🚀 开始研报生成流程")
        self.logger.info("="*80)
        rag_context = self.rag_helper.get_context_for_llm(
            f"{self.target_company} 公司分析 财务数据 行业地位 竞争分析",
            max_tokens=4000, top_k=20
        )
        rag_company = self.rag_helper.get_context_for_llm(
            f"{self.target_company}竞争对手分析",
            max_tokens=4000, top_k=10
        )

        try:
            self.report_info = ReportInfo(self.target_company,rag_context,rag_company)
            # 1. 生成大纲
            parts = self.do_generate_outline()
            self.report_info.report_parts = parts

            # 2. 分段生成深度研报
            self.logger.info("\n✍️ 开始分段生成深度研报...")
            prev_content = ''
            generated_names = set()
            generate_section_agent = GenerateSectionAgent(self.logger, self.llm, self.rag_helper )
            report_generate_section_modify_agent = ReportGenerateSectionModifyAgent(self.logger, self.llm, self.rag_helper)
            again_generate_opinionAgent = AgainGenerateOpinionAgent(self.logger, self.llm)

            full_report_init = [f"# {self.report_info.report_title}\n"]
            for idx, part in enumerate(parts):

                part_title = part.get('part_title', f'部分{idx+1}')
                part_num = part.get('part_num', f'部分{idx+1}')
                if part_title in generated_names:
                    self.logger.warning(f"章节 {part_title} 已生成，跳过")
                    continue
                self.logger.info(f"\n  正在生成：{part_num} ,{part_title}")
                is_last = (idx == len(parts) - 1)

                self.report_info.part_rag_context = self.rag_helper.get_context_for_llm(
                    f"{part_title} {self.report_info.target_company}",
                    max_tokens=4000, top_k=20
                )
                section_text = generate_section_agent.generate_section(self.report_info, part, prev_content, is_last, list(generated_names))
                generate_section_agent.clean_user_message()
                self.logger.info(f"📄 编写 内容: {section_text}")

                section_text_count = 0

                while section_text_count<1:

                    section_text_opinion = again_generate_opinionAgent.generate_opinion(self.report_info, part,
                                                                                        prev_content,
                                                                                        is_last, section_text,
                                                                                        list(generated_names))
                    self.logger.info(f"📄 修改意见 内容: {section_text_opinion}")

                    section_text = report_generate_section_modify_agent.generate_section(self.report_info, part, prev_content, is_last, section_text, section_text_opinion, list(generated_names))
                    self.logger.info(f"📄 编写修改 内容: {section_text}")

                    section_text_count += 1
                    if section_text_opinion =="无":
                        break

                part["part_content"] = section_text
                report_generate_section_modify_agent.clean_user_message()
                again_generate_opinionAgent.clean_user_message()
                full_report_init.append(section_text)
                self.logger.info(f"  ✅ 已完成：{part_num} ,{part_title}")
                prev_content = '\n'.join(full_report_init)
                generated_names.add(part_title)
                # 3. 保存最终报告
            final_report = '\n\n'.join(full_report_init)
            output_file = f"{self.target_company}深度研报_init_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(final_report)

            self.logger.info(f"\n✅ 研报初始版生成完成！文件已保存到: {output_file}")
            self.modify_generate_report(final_report)
            return output_file

        except Exception as e:
            self.logger.error(f"❌ 研报生成失败: {e}")
            return None


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='研报生成流程')
    parser.add_argument('--company', default='商汤科技', help='目标公司名称')
    parser.add_argument('--code', default='00020', help='股票代码')
    parser.add_argument('--market', default='HK', help='市场代码')
    
    args = parser.parse_args()
    
    # 创建研报生成实例
    pipeline = ReportGenerationPipeline(
        target_company=args.company,
        target_company_code=args.code,
        target_company_market=args.market
    )
    
    # 运行研报生成流程
    output_file = pipeline.generate_report()

    if output_file:
        print(f"\n🎉 研报生成流程执行完毕！")
        print(f"📋 研报文件: {output_file}")
    else:
        print("\n❌ 研报生成流程执行失败！")


if __name__ == "__main__":
    main() 