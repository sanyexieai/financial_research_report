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

    OTHER= """
    1 在研究公司之前，我们应先研究该公司所处的行业。该行业处于怎样一个发展历程中。举个例子，普通钢铁水泥很显然处于产能过剩中，在这种可能衰退的行业中寻找投资标的很难，当然也不是不可以。市场普遍对这种衰退行业给的估值不高，且如果衰退趋势有加速，给的估值会进一步下降。

再比如和资本市场关系密切的强周期行业券商$中信证券(hk06030)$ ，牛市时双击，熊市双杀，这是不以人为转移的，所以投资这类强周期行业的个股，要特别注意目前所处的节点，是周期顶端，周期中，还是周期末端。如果判断错周期节点，很可能蒙受巨大损失。

再比如弱周期行业医药，医药有很多细分子行业，增速不一样，可能普通化药，原料药发展速度停滞了，但是医疗器械，生物药，生物检测增速还很快。当然资本市场给的估值也不同。

一般来说弱周期行业增速很快的细分子行业易出黑马，强周期行业判断对周期，也可能获得超额收益（比如猪周期），衰退行业中的沙漠之花，市场份额不断上升，费用率因规模经济不断下降，业绩持续增长的公司也可能走出慢牛行情。

2 研究完行业目前所处情况，我们还必须进行合理大胆的预测将来的行业趋势。想要预测正确，最好方法就是研究国外比我们走的早几步国家，和我国国情类似，行业所处情况类似阶段他们的资本市场相关个股的表现，之后几年十几年行业的趋势变化最需要研究，一般来说，就是日本韩国，美国，欧洲一些国家，有时候这部分资料可呢很难走到，这就是考验分析师能力的地方了，有的需要请教相关国家老一辈生活过的人，甚至需要亲自去现场去海外相关上市公司调研咨询，不是每个人都有这个条件的。

3 行业研究完了，进入下一步公司研究。

（1）首先我们要研究的是招股说明书，这里面学问大了。我们要研究这个公司的历史，它上市募集资金的用途，以及是否像书中所说的那样把钱花到相关项目中，还是仅仅做个样子，想上市圈钱，这个区别非常大。一般来说，真正的成长股黑马一定是继续募集资金发展主业，如果你看到募集自己用来高管发工资挥霍，用途不明，甚至买理财产品，这里面问题就大了。书中还有该公司所处行业竞争力分析，主要竞争对手的数据，大部分还是真实的，如果时间不长久（2年之内）有一定参考价值。然后我们可以比比上市之前公司主要竞争对手情况和上市以后，该公司在行业中的排名是否上升，如果你募集资金以后还没有很快增长，甚至比那些没上市的还发展速度慢，那毫无疑问不是啥好票。书中还有所投项目，市场变化很快，可能有的公司会转型成其他主业或者直接收购进入其他行业。但是如果一个公司一直作为壳存在，不停注入不停更换主业和管理层，我觉得应该不是能长线持有的公司。比如$海虹控股(sz000503)$   。

（2）其次研究的是管理层，我个人认为人  才是企业不断发展的原动力。一个伟大的公司必定有伟大的管理层。如果管理层对公司事务不管不问，大肆挥霍，有造假前科，没有任何行业经验，这样的公司绝不能投。理想的高管（董事长）最好在35-45之间，有丰富的相关行业经验，对公司有决定权，股权集中，甚至待企业如自己孩子一样。脾气不能够太暴躁，也不能太温柔，最好还有一个性格互补的拍档，比如芒格和巴菲特，这样企业经营才能平稳安定。最忌讳那种好大喜功，急火攻心，哪个行业火投哪里的管理层。

（3 ）第三才研究企业报表，估计很多人最看重的吧。我个人觉得企业报表一定要看，但绝对不是最重要的。中国公司报表内幕很多，可以信但不能全信。比如一个公司行业第五，居然净利润和净利率比第一还高。A股经常出现这类造假，必须提高警惕！还有些通过关连交易，通过不断上下游压货造成业绩虚高，里面的水分也需要我们仔细甄别。一般人看不出，没关系，多关注一些细分小行业龙头，很多年报表相差不太大（毕竟连续很多年造假也很难），市场关注度不高的这些公司反而机会更大些。很多人过分关注PEG，关注一季度半年的增速，这是不对的，其实30%和40%增速是差不多的，有时候只是修饰了一下报表。再看看同行业其他公司报表，仔细比对，发现不同。探寻该公司在该行业中增速情况，估值高低情况。再比较一下和其他行业的估值差距，找出理由。如果不是合理，要小心了。我们更应该关注的是公司是不是变得更加强大，在上下游的控制力和议价权是否更强，这才是以后我们长期投资最需要关注的。

（4）企业战略.最最忌讳一种管理层朝令夕改，看到哪个行业火去哪里。比如上半年最火的互联网加，是个企业如果不和互联网沾上点关系，都不好意思和别人说我是上市公司。这其实是企业战略模糊的表现，真正的战略应该正视自己的优势和劣势，采取积极的心态主动调整，相当于田忌赛马，取长补短。把每一分钱都用在刀刃上，我们投资最害怕企业脑子一热，董事长一拍板说投就投还是大手笔，没有经过严密的审核和考虑。很多企业都是死在扩张而不是死于自己做减法。相反，砍去那些负担重，前景不好的子公司，轻装上阵反而能获得不错的企业生命力。

（5）重视员工权利和股东权利。爱民如子，珍视股东权利，这样的公司才值得长期持有。企业发展关键还是靠人，我 宁可你多拿点钱出来给员工，也不希望你挥霍随意投资项目。重视分红，给投资者发表意见并听取合理采纳的公司值得密切关注。

（6）重视主业，不随意乱扩张。重视和ZF关系，重视生态环境和周边居民关系。很多企业被曝光居民闹事，环境污染问题给企业蒙羞。

（7）舍得花钱研发，技术进步企业才能获得更好的竞争力。我们也要把研发投入纳入考核指标，并重视研发产出比。

（8）根据公司公告和各季度报告，不断更新自己的判断。每个公司都不是一成不变的，我们需要不断更新数据，甚至需要亲自去公司调研，寻找更好的投资标的，不能因循守旧，固执己见。
        
    """


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

    def selected_topic(self):
        """生成研报大纲"""
        self.logger.info("📋 生成选题...")

        # 从数据库获取相关上下文
        # rag_context = self.rag_helper.get_context_for_llm(
        #     f"{self.target_company} 公司分析 财务数据 行业地位 竞争分析",
        #     max_tokens=4000
        # )

        outline_prompt = f"""
    你是一位顶级金融分析师和研报撰写首席专家。请基于数据库中的相关信息，对{self.target_company}公司研报的选题：
    - 以yaml格式输出，务必用```yaml和```包裹整个yaml内容
    - 每一项为一个主要部分，每部分需包含：
      - selected_title: 研究问题（必须有公司名称）
      - selected_desc: 数据支持

    【数据库相关信息】
    {self.rag_context}
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


    def again_generate_outline(self,outline_prompt):
        """生成研报大纲"""
        self.logger.info("📋 生成研报大纲...")

        # 从数据库获取相关上下文
        # rag_context = self.rag_helper.get_context_for_llm(
        #     f"{self.target_company} 公司分析 财务数据 行业地位 竞争分析",
        #     max_tokens=4000
        # )

        outline_prompt = f"""
    你是一位顶级金融分析师和研报撰写首席专家。请基于编写的研报大纲内容，修改一份详尽的《{self.target_company}公司研报》分段大纲，要求：
    - 以yaml格式输出，务必用```yaml和```包裹整个yaml内容
    - 每一项为一个主要部分，每部分需包含：
      - part_title: 章节标题
      - part_desc: 本部分内容简介
    - 章节需覆盖公司基本面、财务分析、行业对比、估值与预测、治理结构、投资建议、风险提示等
    {self.OTHER}

    【数据库相关信息】
   {self.rag_context}
    【大纲】
    {outline_prompt}
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

    def generate_outline(self,select_parts):
        """生成研报大纲"""
        self.logger.info("📋 生成研报大纲...")
        
        # 从数据库获取相关上下文
        # rag_context = self.rag_helper.get_context_for_llm(
        #     f"{self.target_company} 公司分析 财务数据 行业地位 竞争分析",
        #     max_tokens=4000
        # )
        
        outline_prompt = f"""
你是一位顶级金融分析师和研报撰写专家。提供相关研报选题，从中选择这个题目。请基于数据库中的相关信息，生成一份详尽的《{self.target_company}公司研报》分段大纲，要求：
- 以yaml格式输出，务必用```yaml和```包裹整个yaml内容
- 每一项为一个主要部分，每部分需包含：
  - part_title: 章节标题
  - part_desc: 本部分内容简介
- 章节需覆盖公司基本面、财务分析、行业对比、估值与预测、治理结构、投资建议、风险提示等
{self.OTHER}
【研报选题】
{select_parts}
【数据库相关信息】
  {self.rag_context}
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
    
    def generate_section(self, part_title, prev_content, is_last,section_text_opinion, generated_names=None):
        """生成单个章节"""
        if generated_names is None:
            generated_names = []
        
        # 从数据库获取相关上下文
        rag_context = self.rag_helper.get_context_for_llm(
            f"{part_title} {self.target_company}",
            max_tokens=4000
        )
        
        section_prompt = f"""
你是一位顶级金融分析师和研报撰写资深研究员。请基于数据库中的相关信息，直接输出"{part_title}"这一部分的完整研报内容。

【已生成章节】：{list(generated_names)}

**重要要求：**
1. 直接输出完整可用的研报内容，以"## {part_title}"开头
2. 在正文中引用数据、事实等信息时，适当位置插入参考资料符号（如[1][2][3]）
3. 不要输出任何分隔符或建议性语言
4. 内容要详实、专业，可直接使用
4. 若用户提供批评反馈，需基于之前的尝试生成修改版本。
【本次任务】
{part_title}

【已生成前文】
{prev_content}

【数据库相关信息】
{rag_context}
【意见】
{section_text_opinion}

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

    def generate_opinion(self, part_title, prev_content, is_last, section_text, generated_names=None):
        """生成单个章节"""
        if generated_names is None:
            generated_names = []

        # 从数据库获取相关上下文
        rag_context = self.rag_helper.get_context_for_llm(
            f"{part_title} {self.target_company}",
            max_tokens=4000
        )

        section_prompt = f"""
你是一位顶级金融分析师和研报撰写首席研究员。请基于数据库中的相关信息，直接输出"{part_title}"这一部分的完整研报内容修改意见。

【已生成章节】：{list(generated_names)}

**重要要求：**
1. 直接输出完整可用的研报内容，以"## {part_title}"开头
2. 要求为用户提交的作文生成批评和建议
3. 需提供详细建议，涵盖篇幅长度、内容深度、写作风格等维度
4. 内容要详实、专业，可直接使用
- 以yaml格式输出，务必用```yaml和```包裹整个yaml内容
- 每一项为一个主要部分，每部分需包含：
  - opinion_title: 批评和建议章节标题
  - opinion_desc: 批评和建议的内容
【本次任务】
{part_title}

【已生成前文】
{prev_content}
【本次要修改的文案】
{section_text}
【数据库相关信息】
{rag_context}
如果不需要修改，请直接输出"无"
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
        self.rag_context = self.rag_helper.get_context_for_llm(
            f"{self.target_company} 公司分析 财务数据 行业地位 竞争分析",
            max_tokens=4000
        )
        try:

            select_parts = self.selected_topic()
            self.logger.info(f"📄 parts 内容: {select_parts}")
            # 1. 生成大纲
            parts = self.generate_outline(select_parts)
            self.logger.info(f"📄 parts 内容: {parts}")

            parts = self.again_generate_outline(parts)
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

                section_text_completed = True
                section_text_opinion = ""
                section_text = ""
                section_text_count = 0
                while section_text_count<3:
                    section_text = self.generate_section(
                        part_title, prev_content, is_last,section_text_opinion, list(generated_names)
                    )
                    section_text_opinion = self.generate_opinion(
                        part_title, prev_content, is_last, section_text, list(generated_names)
                    )
                    section_text_count += 1
                    if section_text_opinion =="无":
                        break

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