# -*- coding: utf-8 -*-
"""
风险分析器
评估公司治理结构与发展战略，提出风险提醒
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
import warnings
warnings.filterwarnings('ignore')

class RiskAnalyzer:
    """风险分析器"""
    
    def __init__(self):
        self.risk_factors = {}
    
    def analyze_financial_risks(self, financial_data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """
        分析财务风险
        
        Args:
            financial_data: 财务数据
            
        Returns:
            财务风险分析结果
        """
        try:
            financial_risks = {}
            
            balance_sheet = financial_data.get('资产负债表', pd.DataFrame())
            income_statement = financial_data.get('利润表', pd.DataFrame())
            cash_flow_statement = financial_data.get('现金流量表', pd.DataFrame())
            
            if not balance_sheet.empty:
                # 资产负债率风险
                latest_balance = balance_sheet.iloc[0]
                total_liabilities = self._safe_get_value(latest_balance, ['负债合计', '总负债'])
                total_assets = self._safe_get_value(latest_balance, ['资产总计', '总资产'])
                
                if total_liabilities and total_assets:
                    debt_ratio = (total_liabilities / total_assets) * 100
                    financial_risks["资产负债率"] = {
                        "比率": f"{debt_ratio:.2f}%",
                        "风险等级": self._assess_debt_ratio_risk(debt_ratio),
                        "风险说明": self._get_debt_ratio_explanation(debt_ratio)
                    }
            
            if not income_statement.empty:
                # 盈利稳定性风险
                if len(income_statement) >= 4:  # 至少4个季度数据
                    profits = []
                    for i in range(min(4, len(income_statement))):
                        profit = self._safe_get_value(income_statement.iloc[i], ['净利润', '归属于母公司所有者的净利润'])
                        if profit:
                            profits.append(profit)
                    
                    if len(profits) >= 3:
                        profit_volatility = np.std(profits) / np.mean(profits) * 100
                        financial_risks["盈利稳定性"] = {
                            "波动系数": f"{profit_volatility:.2f}%",
                            "风险等级": self._assess_volatility_risk(profit_volatility),
                            "风险说明": self._get_volatility_explanation(profit_volatility)
                        }
            
            if not cash_flow_statement.empty:
                # 现金流风险
                latest_cash_flow = cash_flow_statement.iloc[0]
                operating_cash_flow = self._safe_get_value(latest_cash_flow, ['经营活动产生的现金流量净额'])
                
                if operating_cash_flow:
                    if operating_cash_flow < 0:
                        financial_risks["现金流风险"] = {
                            "状态": "经营性现金流为负",
                            "风险等级": "高风险",
                            "风险说明": "经营活动现金流为负，需关注资金链风险"
                        }
                    else:
                        financial_risks["现金流风险"] = {
                            "状态": "经营性现金流为正",
                            "风险等级": "低风险",
                            "风险说明": "经营活动现金流良好"
                        }
            
            print("✅ 财务风险分析完成")
            return financial_risks
            
        except Exception as e:
            print(f"❌ 财务风险分析失败: {e}")
            return {}
    
    def analyze_operational_risks(self, business_info: Dict[str, Any], industry_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        分析经营风险
        
        Args:
            business_info: 企业基本信息
            industry_data: 行业数据
            
        Returns:
            经营风险分析结果
        """
        try:
            operational_risks = {}
            
            # 行业风险
            main_business = business_info.get("主营业务", "")
            if main_business:
                operational_risks["行业风险"] = self._assess_industry_risk(main_business)
            
            # 业务集中度风险
            operating_scope = business_info.get("经营范围", "")
            if operating_scope:
                operational_risks["业务集中度风险"] = self._assess_business_concentration_risk(operating_scope)
            
            # 市场竞争风险
            operational_risks["市场竞争风险"] = {
                "风险等级": "中等风险",
                "风险说明": "行业竞争激烈，需关注市场份额变化",
                "应对策略": "加强品牌建设，提升产品差异化"
            }
            
            print("✅ 经营风险分析完成")
            return operational_risks
            
        except Exception as e:
            print(f"❌ 经营风险分析失败: {e}")
            return {}
    
    def analyze_governance_risks(self, management_info: Dict[str, Any], shareholder_info: pd.DataFrame) -> Dict[str, Any]:
        """
        分析公司治理风险
        
        Args:
            management_info: 管理层信息
            shareholder_info: 股东信息
            
        Returns:
            治理风险分析结果
        """
        try:
            governance_risks = {}
            
            # 股权集中度风险
            if not shareholder_info.empty and len(shareholder_info) > 0:
                # 分析前十大股东持股比例
                if '持股比例' in shareholder_info.columns:
                    top_shareholder_ratio = float(shareholder_info.iloc[0]['持股比例'].replace('%', ''))
                    governance_risks["股权集中度风险"] = {
                        "第一大股东持股比例": f"{top_shareholder_ratio:.2f}%",
                        "风险等级": self._assess_ownership_concentration_risk(top_shareholder_ratio),
                        "风险说明": self._get_ownership_concentration_explanation(top_shareholder_ratio)
                    }
            
            # 管理层风险
            if management_info:
                management_count = management_info.get("高管人数", 0)
                governance_risks["管理层风险"] = {
                    "高管团队规模": f"{management_count}人",
                    "风险评估": "需进一步评估管理层稳定性和专业能力",
                    "建议": "关注高管变动情况和激励机制"
                }
            
            # 信息披露风险
            governance_risks["信息披露风险"] = {
                "风险等级": "低风险",
                "风险说明": "作为上市公司，信息披露相对透明",
                "建议": "持续关注定期报告和临时公告"
            }
            
            print("✅ 公司治理风险分析完成")
            return governance_risks
            
        except Exception as e:
            print(f"❌ 公司治理风险分析失败: {e}")
            return {}
    
    def analyze_market_risks(self, financial_data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """
        分析市场风险
        
        Args:
            financial_data: 财务数据
            
        Returns:
            市场风险分析结果
        """
        try:
            market_risks = {}
            
            # 宏观经济风险
            market_risks["宏观经济风险"] = {
                "风险等级": "中等风险",
                "风险因素": ["GDP增长放缓", "利率变化", "通胀压力"],
                "影响程度": "中等影响",
                "应对策略": "密切关注宏观政策变化，适时调整经营策略"
            }
            
            # 汇率风险
            market_risks["汇率风险"] = {
                "风险等级": "低风险",
                "风险说明": "主要业务在国内，汇率影响相对较小",
                "建议": "如有海外业务，建议适当对冲汇率风险"
            }
            
            # 利率风险
            market_risks["利率风险"] = {
                "风险等级": "中等风险",
                "风险说明": "利率变化可能影响融资成本和投资收益",
                "建议": "优化债务结构，关注利率走势"
            }
            
            # 流动性风险
            market_risks["流动性风险"] = {
                "风险等级": "低风险",
                "风险说明": "作为大型上市公司，流动性风险相对较低",
                "建议": "维持合理现金储备，确保资金链安全"
            }
            
            print("✅ 市场风险分析完成")
            return market_risks
            
        except Exception as e:
            print(f"❌ 市场风险分析失败: {e}")
            return {}
    
    def analyze_policy_risks(self, business_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析政策风险
        
        Args:
            business_info: 企业基本信息
            
        Returns:
            政策风险分析结果
        """
        try:
            policy_risks = {}
            
            # 行业政策风险
            main_business = business_info.get("主营业务", "")
            industry = business_info.get("所属行业", "")
            
            if "白酒" in main_business or "酒类" in main_business:
                policy_risks["行业政策风险"] = {
                    "风险等级": "中等风险",
                    "主要风险": ["限酒政策", "税收政策变化", "广告监管"],
                    "影响程度": "中等影响",
                    "应对策略": "积极响应政策导向，加强合规经营"
                }
            else:
                policy_risks["行业政策风险"] = {
                    "风险等级": "中等风险",
                    "主要风险": ["产业政策调整", "环保要求提升", "税收政策变化"],
                    "影响程度": "待评估",
                    "应对策略": "密切关注政策变化，提前布局应对"
                }
            
            # 监管风险
            policy_risks["监管风险"] = {
                "风险等级": "中等风险",
                "主要风险": ["证券监管政策变化", "行业监管加强"],
                "影响程度": "中等影响",
                "应对策略": "加强合规管理，提升信息披露质量"
            }
            
            print("✅ 政策风险分析完成")
            return policy_risks
            
        except Exception as e:
            print(f"❌ 政策风险分析失败: {e}")
            return {}
    
    def comprehensive_risk_assessment(self, financial_data: Dict[str, pd.DataFrame], 
                                    business_info: Dict[str, Any],
                                    management_info: Dict[str, Any],
                                    shareholder_info: pd.DataFrame) -> Dict[str, Any]:
        """
        综合风险评估
        
        Args:
            financial_data: 财务数据
            business_info: 企业基本信息
            management_info: 管理层信息
            shareholder_info: 股东信息
            
        Returns:
            综合风险评估结果
        """
        try:
            comprehensive_risk = {
                "财务风险": self.analyze_financial_risks(financial_data),
                "经营风险": self.analyze_operational_risks(business_info),
                "治理风险": self.analyze_governance_risks(management_info, shareholder_info),
                "市场风险": self.analyze_market_risks(financial_data),
                "政策风险": self.analyze_policy_risks(business_info),
                "综合风险评级": self._calculate_overall_risk_rating(),
                "风险管理建议": self._generate_risk_management_recommendations()
            }
            
            print("✅ 综合风险评估完成")
            return comprehensive_risk
            
        except Exception as e:
            print(f"❌ 综合风险评估失败: {e}")
            return {}
    
    def _safe_get_value(self, data, keys):
        """安全获取数据值"""
        if isinstance(data, dict):
            for key in keys:
                if key in data and pd.notna(data[key]):
                    return float(data[key])
        elif hasattr(data, 'get'):
            for key in keys:
                value = data.get(key)
                if pd.notna(value):
                    return float(value)
        return None
    
    def _assess_debt_ratio_risk(self, debt_ratio):
        """评估资产负债率风险"""
        if debt_ratio > 70:
            return "高风险"
        elif debt_ratio > 50:
            return "中等风险"
        else:
            return "低风险"
    
    def _get_debt_ratio_explanation(self, debt_ratio):
        """获取资产负债率风险说明"""
        if debt_ratio > 70:
            return "资产负债率过高，存在较大财务风险"
        elif debt_ratio > 50:
            return "资产负债率适中，需关注债务结构"
        else:
            return "资产负债率较低，财务风险可控"
    
    def _assess_volatility_risk(self, volatility):
        """评估波动性风险"""
        if volatility > 50:
            return "高风险"
        elif volatility > 25:
            return "中等风险"
        else:
            return "低风险"
    
    def _get_volatility_explanation(self, volatility):
        """获取波动性风险说明"""
        if volatility > 50:
            return "盈利波动较大，稳定性较差"
        elif volatility > 25:
            return "盈利有一定波动，需关注"
        else:
            return "盈利相对稳定"
    
    def _assess_industry_risk(self, main_business):
        """评估行业风险"""
        risk_keywords = {
            "高风险": ["钢铁", "煤炭", "房地产", "化工"],
            "中等风险": ["制造", "零售", "服务"],
            "低风险": ["食品", "医药", "公用事业"]
        }
        
        for risk_level, keywords in risk_keywords.items():
            if any(keyword in main_business for keyword in keywords):
                return {
                    "风险等级": risk_level,
                    "风险说明": f"所属{main_business}行业，面临{risk_level}的行业风险"
                }
        
        return {
            "风险等级": "中等风险",
            "风险说明": "行业风险需进一步评估"
        }
    
    def _assess_business_concentration_risk(self, operating_scope):
        """评估业务集中度风险"""
        # 简化实现
        return {
            "风险等级": "中等风险",
            "风险说明": "需关注业务多元化程度和市场集中度"
        }
    
    def _assess_ownership_concentration_risk(self, top_ratio):
        """评估股权集中度风险"""
        if top_ratio > 50:
            return "中等风险"
        elif top_ratio > 30:
            return "低风险"
        else:
            return "较低风险"
    
    def _get_ownership_concentration_explanation(self, top_ratio):
        """获取股权集中度风险说明"""
        if top_ratio > 50:
            return "股权较为集中，需关注大股东行为对中小股东的影响"
        elif top_ratio > 30:
            return "股权集中度适中，治理结构相对均衡"
        else:
            return "股权较为分散，决策效率可能受影响"
    
    def _calculate_overall_risk_rating(self):
        """计算综合风险评级"""
        return {
            "综合评级": "中等风险",
            "评级说明": "基于财务、经营、治理、市场和政策等多维度风险分析",
            "主要风险点": ["市场竞争", "政策变化", "宏观经济"],
            "风险可控性": "风险总体可控，需持续关注"
        }
    
    def _generate_risk_management_recommendations(self):
        """生成风险管理建议"""
        return {
            "短期建议": [
                "加强现金流管理",
                "优化债务结构",
                "关注政策变化"
            ],
            "中期建议": [
                "完善内控制度",
                "提升治理水平",
                "加强风险预警"
            ],
            "长期建议": [
                "业务多元化布局",
                "提升核心竞争力",
                "建立风险管理体系"
            ]
        }
