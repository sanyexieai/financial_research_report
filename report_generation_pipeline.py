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

from data_analysis_agent import quick_analysis
from data_analysis_agent.config.llm_config import LLMConfig
from data_analysis_agent.utils.llm_helper import LLMHelper
from utils.rag_postgres import RAGPostgresHelper
from config.database_config import db_config

class ReportGenerationPipeline:
    """研报生成流程类"""
    
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
    
    def generate_outline(self):
        """生成研报大纲"""
        self.logger.info("📋 生成研报大纲...")
        
        # 从数据库获取相关上下文
        rag_context = self.rag_helper.get_context_for_llm(
            f"{self.target_company} 公司分析 财务数据 行业地位 竞争分析",
            max_tokens=4000
        )
        
        outline_prompt = f"""
你是一位顶级金融分析师和研报撰写专家。请基于数据库中的相关信息，生成一份详尽的《{self.target_company}公司研报》分段大纲，要求：
- 以yaml格式输出，务必用```yaml和```包裹整个yaml内容
- 每一项为一个主要部分，每部分需包含：
  - part_title: 章节标题
  - part_desc: 本部分内容简介
- 章节需覆盖公司基本面、财务分析、行业对比、估值与预测、治理结构、投资建议、风险提示等

【数据库相关信息】
{rag_context}
"""
        outline_list = self.llm.call(
            outline_prompt,
            system_prompt="你是一位顶级金融分析师和研报撰写专家，分段大纲必须用```yaml包裹。",
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
            self.logger.error(f"[大纲yaml解析失败] {e}")
            return []
    
    def generate_section(self, part_title, prev_content, is_last, generated_names=None):
        """生成单个章节"""
        if generated_names is None:
            generated_names = []
        
        # 从数据库获取相关上下文
        rag_context = self.rag_helper.get_context_for_llm(
            f"{part_title} {self.target_company}",
            max_tokens=4000
        )
        
        section_prompt = f"""
你是一位顶级金融分析师和研报撰写专家。请基于数据库中的相关信息，直接输出"{part_title}"这一部分的完整研报内容。

【已生成章节】：{list(generated_names)}

**重要要求：**
1. 直接输出完整可用的研报内容，以"## {part_title}"开头
2. 在正文中引用数据、事实等信息时，适当位置插入参考资料符号（如[1][2][3]）
3. 不要输出任何分隔符或建议性语言
4. 内容要详实、专业，可直接使用

【本次任务】
{part_title}

【已生成前文】
{prev_content}

【数据库相关信息】
{rag_context}
"""
        if is_last:
            section_prompt += """
请在本节最后以"引用文献"格式，列出所有正文中用到的参考资料。
"""
        
        section_text = self.llm.call(
            section_prompt,
            system_prompt="你是顶级金融分析师，专门生成完整可用的研报内容。",
            max_tokens=8192,
            temperature=0.5
        )
        return section_text
    
    def generate_report(self):
        """生成完整研报"""
        self.logger.info("\n" + "="*80)
        self.logger.info("🚀 开始研报生成流程")
        self.logger.info("="*80)
        
        try:
            # 1. 生成大纲
            parts = self.generate_outline()
            
            if not parts:
                self.logger.error("❌ 大纲生成失败")
                return None
            
            # 2. 分段生成深度研报
            self.logger.info("\n✍️ 开始分段生成深度研报...")
            full_report = [f'# {self.target_company}公司研报\n']
            prev_content = ''
            generated_names = set()
            
            for idx, part in enumerate(parts):
                part_title = part.get('part_title', f'部分{idx+1}')
                if part_title in generated_names:
                    self.logger.warning(f"章节 {part_title} 已生成，跳过")
                    continue
                
                self.logger.info(f"\n  正在生成：{part_title}")
                is_last = (idx == len(parts) - 1)
                section_text = self.generate_section(
                    part_title, prev_content, is_last, list(generated_names)
                )
                full_report.append(section_text)
                self.logger.info(f"  ✅ 已完成：{part_title}")
                prev_content = '\n'.join(full_report)
                generated_names.add(part_title)
            
            # 3. 保存最终报告
            final_report = '\n\n'.join(full_report)
            output_file = f"{self.target_company}深度研报_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(final_report)
            
            self.logger.info(f"\n✅ 研报生成完成！文件已保存到: {output_file}")
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