# -*- coding: utf-8 -*-
"""
财务比率分析器
计算ROE分解、毛利率、现金流匹配度等关键财务比率
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
import warnings
warnings.filterwarnings('ignore')

class FinancialRatioAnalyzer:
    """财务比率分析器"""
    
    def __init__(self):
        self.ratios = {}
    
    def calculate_roe_decomposition(self, financial_data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """
        计算ROE分解（杜邦分析法）
        ROE = 净利润率 × 总资产周转率 × 权益乘数
        
        Args:
            financial_data: 财务数据字典，包含利润表和资产负债表
            
        Returns:
            ROE分解结果
        """
        try:
            roe_analysis = {}
            
            # 获取利润表数据
            income_statement = financial_data.get('利润表', pd.DataFrame())
            balance_sheet = financial_data.get('资产负债表', pd.DataFrame())
            
            if income_statement.empty or balance_sheet.empty:
                print("⚠️ 缺少必要的财务数据进行ROE分析")
                return {}
            
            # 获取最新期数据
            latest_income = income_statement.iloc[0] if not income_statement.empty else {}
            latest_balance = balance_sheet.iloc[0] if not balance_sheet.empty else {}
            
            # 提取关键指标
            net_profit = self._safe_get_value(latest_income, ['净利润', '归属于母公司所有者的净利润'])
            revenue = self._safe_get_value(latest_income, ['营业收入', '营业总收入'])
            total_assets = self._safe_get_value(latest_balance, ['资产总计', '总资产'])
            shareholders_equity = self._safe_get_value(latest_balance, ['所有者权益合计', '股东权益合计', '归属于母公司所有者权益合计'])
            
            if all([net_profit, revenue, total_assets, shareholders_equity]):
                # 计算ROE组成部分
                net_profit_margin = (net_profit / revenue) * 100  # 净利润率
                asset_turnover = revenue / total_assets  # 总资产周转率
                equity_multiplier = total_assets / shareholders_equity  # 权益乘数
                roe = (net_profit / shareholders_equity) * 100  # ROE
                
                roe_analysis = {
                    "ROE": round(roe, 2),
                    "净利润率": round(net_profit_margin, 2),
                    "总资产周转率": round(asset_turnover, 2),
                    "权益乘数": round(equity_multiplier, 2),
                    "计算公式": "ROE = 净利润率 × 总资产周转率 × 权益乘数",
                    "验证": round(net_profit_margin * asset_turnover * equity_multiplier / 100, 2),
                    "分析": self._analyze_roe_components(net_profit_margin, asset_turnover, equity_multiplier)
                }
                
                print(f"✅ ROE分解计算完成: ROE={roe:.2f}%")
            else:
                print("⚠️ 缺少ROE计算所需的关键数据")
                
            return roe_analysis
            
        except Exception as e:
            print(f"❌ ROE分解计算失败: {e}")
            return {}
    
    def calculate_profitability_ratios(self, financial_data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """
        计算盈利能力比率
        
        Args:
            financial_data: 财务数据
            
        Returns:
            盈利能力比率
        """
        try:
            profitability = {}
            
            income_statement = financial_data.get('利润表', pd.DataFrame())
            if income_statement.empty:
                return {}
            
            latest_data = income_statement.iloc[0]
            
            # 提取数据
            revenue = self._safe_get_value(latest_data, ['营业收入', '营业总收入'])
            operating_cost = self._safe_get_value(latest_data, ['营业成本'])
            operating_profit = self._safe_get_value(latest_data, ['营业利润'])
            net_profit = self._safe_get_value(latest_data, ['净利润', '归属于母公司所有者的净利润'])
            
            if revenue:
                # 毛利率
                if operating_cost is not None:
                    gross_profit = revenue - operating_cost
                    gross_margin = (gross_profit / revenue) * 100
                    profitability["毛利率"] = round(gross_margin, 2)
                
                # 营业利润率
                if operating_profit:
                    operating_margin = (operating_profit / revenue) * 100
                    profitability["营业利润率"] = round(operating_margin, 2)
                
                # 净利润率
                if net_profit:
                    net_margin = (net_profit / revenue) * 100
                    profitability["净利润率"] = round(net_margin, 2)
            
            print("✅ 盈利能力比率计算完成")
            return profitability
            
        except Exception as e:
            print(f"❌ 盈利能力比率计算失败: {e}")
            return {}
    
    def calculate_cash_flow_matching(self, financial_data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """
        计算现金流匹配度
        
        Args:
            financial_data: 包含现金流量表的财务数据
            
        Returns:
            现金流匹配度分析
        """
        try:
            cash_flow_analysis = {}
            
            income_statement = financial_data.get('利润表', pd.DataFrame())
            cash_flow_statement = financial_data.get('现金流量表', pd.DataFrame())
            
            if income_statement.empty or cash_flow_statement.empty:
                print("⚠️ 缺少现金流匹配度分析所需数据")
                return {}
            
            # 获取最新数据
            latest_income = income_statement.iloc[0]
            latest_cash_flow = cash_flow_statement.iloc[0]
            
            # 提取关键数据
            net_profit = self._safe_get_value(latest_income, ['净利润', '归属于母公司所有者的净利润'])
            operating_cash_flow = self._safe_get_value(latest_cash_flow, ['经营活动产生的现金流量净额', '经营性现金流净额'])
            
            if net_profit and operating_cash_flow:
                # 现金流净利润比
                cash_to_profit_ratio = operating_cash_flow / net_profit
                
                cash_flow_analysis = {
                    "净利润": f"{net_profit/100000000:.2f}亿元",
                    "经营性现金流": f"{operating_cash_flow/100000000:.2f}亿元", 
                    "现金流净利润比": round(cash_to_profit_ratio, 2),
                    "现金流质量": self._evaluate_cash_flow_quality(cash_to_profit_ratio),
                    "匹配度评价": self._evaluate_cash_flow_matching(cash_to_profit_ratio)
                }
                
                print("✅ 现金流匹配度计算完成")
            
            return cash_flow_analysis
            
        except Exception as e:
            print(f"❌ 现金流匹配度计算失败: {e}")
            return {}
    
    def calculate_growth_ratios(self, financial_data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """
        计算成长性比率
        
        Args:
            financial_data: 财务数据
            
        Returns:
            成长性分析
        """
        try:
            growth_analysis = {}
            
            income_statement = financial_data.get('利润表', pd.DataFrame())
            if len(income_statement) < 2:
                print("⚠️ 需要至少两期数据计算成长性")
                return {}
            
            # 获取最近两期数据
            current_period = income_statement.iloc[0]
            previous_period = income_statement.iloc[1]
            
            # 计算收入增长率
            current_revenue = self._safe_get_value(current_period, ['营业收入', '营业总收入'])
            previous_revenue = self._safe_get_value(previous_period, ['营业收入', '营业总收入'])
            
            if current_revenue and previous_revenue:
                revenue_growth = ((current_revenue - previous_revenue) / previous_revenue) * 100
                growth_analysis["营业收入增长率"] = round(revenue_growth, 2)
            
            # 计算净利润增长率
            current_profit = self._safe_get_value(current_period, ['净利润', '归属于母公司所有者的净利润'])
            previous_profit = self._safe_get_value(previous_period, ['净利润', '归属于母公司所有者的净利润'])
            
            if current_profit and previous_profit:
                profit_growth = ((current_profit - previous_profit) / previous_profit) * 100
                growth_analysis["净利润增长率"] = round(profit_growth, 2)
            
            print("✅ 成长性比率计算完成")
            return growth_analysis
            
        except Exception as e:
            print(f"❌ 成长性比率计算失败: {e}")
            return {}
    
    def comprehensive_ratio_analysis(self, financial_data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """
        综合财务比率分析
        
        Args:
            financial_data: 完整财务数据
            
        Returns:
            综合分析结果
        """
        try:
            comprehensive_analysis = {
                "ROE分解": self.calculate_roe_decomposition(financial_data),
                "盈利能力": self.calculate_profitability_ratios(financial_data),
                "现金流匹配度": self.calculate_cash_flow_matching(financial_data),
                "成长性分析": self.calculate_growth_ratios(financial_data)
            }
            
            # 添加综合评价
            comprehensive_analysis["综合评价"] = self._generate_comprehensive_evaluation(comprehensive_analysis)
            
            print("✅ 综合财务比率分析完成")
            return comprehensive_analysis
            
        except Exception as e:
            print(f"❌ 综合财务比率分析失败: {e}")
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
    
    def _analyze_roe_components(self, net_margin, asset_turnover, equity_multiplier):
        """分析ROE组成部分"""
        analysis = []
        
        if net_margin > 20:
            analysis.append("净利润率表现优秀")
        elif net_margin > 10:
            analysis.append("净利润率表现良好")
        else:
            analysis.append("净利润率有待提升")
            
        if asset_turnover > 1:
            analysis.append("资产周转效率较高")
        else:
            analysis.append("资产周转效率偏低")
            
        if equity_multiplier > 3:
            analysis.append("财务杠杆较高，需关注财务风险")
        elif equity_multiplier > 2:
            analysis.append("财务杠杆适中")
        else:
            analysis.append("财务杠杆较低，偏保守")
            
        return "；".join(analysis)
    
    def _evaluate_cash_flow_quality(self, ratio):
        """评估现金流质量"""
        if ratio >= 1.2:
            return "优秀"
        elif ratio >= 0.8:
            return "良好"
        elif ratio >= 0.5:
            return "一般"
        else:
            return "较差"
    
    def _evaluate_cash_flow_matching(self, ratio):
        """评估现金流匹配度"""
        if ratio >= 1.2:
            return "现金流与利润高度匹配，盈利质量优秀"
        elif ratio >= 0.8:
            return "现金流与利润匹配良好，盈利质量可靠"
        elif ratio >= 0.5:
            return "现金流与利润匹配一般，需关注应收账款等"
        else:
            return "现金流与利润匹配度较低，需关注盈利质量"
    
    def _generate_comprehensive_evaluation(self, analysis_results):
        """生成综合评价"""
        evaluations = []
        
        # ROE评价
        roe_data = analysis_results.get("ROE分解", {})
        if roe_data.get("ROE", 0) > 15:
            evaluations.append("ROE表现优秀")
        
        # 盈利能力评价
        profitability = analysis_results.get("盈利能力", {})
        if profitability.get("毛利率", 0) > 30:
            evaluations.append("盈利能力强")
        
        # 现金流评价
        cash_flow = analysis_results.get("现金流匹配度", {})
        if cash_flow.get("现金流净利润比", 0) > 1:
            evaluations.append("现金流质量优秀")
        
        if not evaluations:
            evaluations.append("财务表现需要进一步分析")
        
        return "；".join(evaluations)
