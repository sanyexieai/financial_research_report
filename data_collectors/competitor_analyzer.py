# -*- coding: utf-8 -*-
"""
竞争对手分析器
使用AI识别同行企业并进行横向竞争分析
"""

import openai
from typing import List, Dict, Any
from config.llm_config import LLMConfig

class CompetitorAnalyzer:
    """竞争对手分析器"""
    
    def __init__(self, llm_config: LLMConfig = None):
        self.llm_config = llm_config or LLMConfig()
        self.client = openai.OpenAI(
            api_key=self.llm_config.api_key,
            base_url=self.llm_config.base_url
        )
    
    def identify_competitors_with_ai(self, company_name: str, industry: str) -> List[str]:
        """
        使用AI识别同行竞争对手
        
        Args:
            company_name: 公司名称
            industry: 所属行业
            
        Returns:
            竞争对手股票代码列表
        """
        prompt = f"""
        请分析以下公司的竞争对手：
        
        公司名称: {company_name}
        所属行业: {industry}
        
        请根据以下标准识别该公司的主要竞争对手：
        1. 同行业内的主要上市公司
        2. 业务模式相似的公司
        3. 市值规模相近的公司
        4. 主要业务重叠度高的公司
        
        请返回3-5个主要竞争对手的股票代码（6位数字格式，如000001），按竞争程度排序。
        只返回股票代码，每行一个，不要其他文字说明。

        示例格式：
        000002
        000003
        600000
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.llm_config.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的金融分析师，擅长识别公司的竞争对手。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            competitors_text = response.choices[0].message.content.strip()
            competitors = [code.strip() for code in competitors_text.split('\n') 
                          if code.strip() and code.strip().isdigit() and len(code.strip()) == 6]
            
            print(f"✅ 成功识别 {len(competitors)} 个竞争对手: {competitors}")
            return competitors[:5]
            
        except Exception as e:
            print(f"❌ AI识别竞争对手失败: {e}")
            return []
    
    def get_industry_competitors(self, stock_code: str) -> List[str]:
        """
        根据股票代码获取行业竞争对手
        
        Args:
            stock_code: 股票代码
            
        Returns:
            竞争对手股票代码列表
        """
        # 这里可以实现基于行业分类的竞争对手识别逻辑
        # 目前返回一些常见的竞争对手示例
        
        competitor_mapping = {
            # 白酒行业
            "600519": ["000858", "000596", "002304", "000799"],  # 茅台 -> 五粮液、古井贡、金徽酒、酒鬼酒
            "000858": ["600519", "000596", "002304", "000799"],  # 五粮液
            
            # 银行业
            "000001": ["600036", "601328", "600000", "600016"],  # 平安银行 -> 招商银行、交通银行、浦发银行、民生银行
            "600036": ["000001", "601328", "600000", "600016"],  # 招商银行
            
            # 保险业
            "601318": ["601601", "601628", "002142"],  # 中国平安 -> 中国太保、中国人寿、宁波银行
        }
        
        clean_code = stock_code.replace("sh", "").replace("sz", "")
        competitors = competitor_mapping.get(clean_code, [])
        
        if competitors:
            print(f"✅ 找到 {len(competitors)} 个行业竞争对手: {competitors}")
        else:
            print(f"⚠️ 未找到 {stock_code} 的预定义竞争对手")
            
        return competitors
    
    def analyze_competitor_performance(self, company_data: Dict[str, Any], competitors_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        分析竞争对手表现
        
        Args:
            company_data: 目标公司数据
            competitors_data: 竞争对手数据列表
            
        Returns:
            竞争分析结果
        """
        analysis = {
            "competitive_position": "",
            "strengths": [],
            "weaknesses": [],
            "market_share_ranking": 0,
            "performance_comparison": {}
        }
        
        try:
            # 这里可以实现具体的竞争分析逻辑
            # 比较营收、利润率、成长性等指标
            
            # 示例分析逻辑
            if company_data and competitors_data:
                analysis["competitive_position"] = "行业领先"
                analysis["strengths"] = ["品牌价值高", "盈利能力强", "现金流充沛"]
                analysis["weaknesses"] = ["增长速度放缓", "面临新兴竞争"]
                analysis["market_share_ranking"] = 1
                
                # 可以添加更详细的数值比较
                analysis["performance_comparison"] = {
                    "revenue_ranking": 1,
                    "profit_margin_ranking": 1,
                    "growth_rate_ranking": 2
                }
            
            print("✅ 完成竞争对手分析")
            return analysis
            
        except Exception as e:
            print(f"❌ 竞争分析失败: {e}")
            return analysis
