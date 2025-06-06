# -*- coding: utf-8 -*-
"""
财务数据收集器
整合akshare API获取公司财务数据
"""

import akshare as ak
import pandas as pd
from typing import Dict, Any, List, Optional
import warnings
warnings.filterwarnings('ignore')

class FinancialDataCollector:
    """财务数据收集器"""
    
    def __init__(self):
        self.cache = {}
    
    def get_financial_reports(self, stock_code: str) -> Dict[str, pd.DataFrame]:
        """
        获取公司财务三大表
        
        Args:
            stock_code: 股票代码，如 "sh600519" 或 "000001"
            
        Returns:
            包含三大财务报表的字典
        """
        try:
            # 标准化股票代码
            stock_code = self._normalize_stock_code(stock_code)
            
            financial_data = {}
            
            # 获取利润表
            try:
                profit_statement = ak.stock_financial_report_sina(stock=stock_code, symbol="利润表")
                financial_data['利润表'] = profit_statement
                print(f"✅ 成功获取 {stock_code} 利润表数据")
            except Exception as e:
                print(f"❌ 获取利润表失败: {e}")
                financial_data['利润表'] = pd.DataFrame()
            
            # 获取资产负债表
            try:
                balance_sheet = ak.stock_financial_report_sina(stock=stock_code, symbol="资产负债表")
                financial_data['资产负债表'] = balance_sheet
                print(f"✅ 成功获取 {stock_code} 资产负债表数据")
            except Exception as e:
                print(f"❌ 获取资产负债表失败: {e}")
                financial_data['资产负债表'] = pd.DataFrame()
            
            # 获取现金流量表
            try:
                cash_flow = ak.stock_financial_report_sina(stock=stock_code, symbol="现金流量表")
                financial_data['现金流量表'] = cash_flow
                print(f"✅ 成功获取 {stock_code} 现金流量表数据")
            except Exception as e:
                print(f"❌ 获取现金流量表失败: {e}")
                financial_data['现金流量表'] = pd.DataFrame()
                
            return financial_data
            
        except Exception as e:
            print(f"❌ 获取财务数据失败: {e}")
            return {}
    
    def get_financial_indicators(self, stock_code: str) -> pd.DataFrame:
        """
        获取财务指标数据（用于ROE分解等）
        
        Args:
            stock_code: 股票代码
            
        Returns:
            财务指标DataFrame
        """
        try:
            # 去掉前缀，只保留6位数字
            clean_code = stock_code.replace("sh", "").replace("sz", "")
            
            # 尝试多个API获取财务指标
            try:
                # 方法1: akshare财务分析指标
                indicators = ak.stock_financial_analysis_indicator(symbol=clean_code)
                print(f"✅ 成功获取 {stock_code} 财务指标数据")
                return indicators
            except Exception as e1:
                print(f"⚠️ 方法1失败: {e1}")
                
                try:
                    # 方法2: 财务摘要数据
                    abstract_data = ak.stock_financial_abstract_ths(symbol=clean_code, indicator="20240331")
                    print(f"✅ 成功获取 {stock_code} 财务摘要数据")
                    return abstract_data
                except Exception as e2:
                    print(f"⚠️ 方法2失败: {e2}")
                    return pd.DataFrame()
                    
        except Exception as e:
            print(f"❌ 获取财务指标失败: {e}")
            return pd.DataFrame()
    
    def get_stock_holders(self, stock_code: str) -> pd.DataFrame:
        """
        获取股权结构信息
        
        Args:
            stock_code: 股票代码
            
        Returns:
            股东信息DataFrame
        """
        try:
            # 去掉前缀
            clean_code = stock_code.replace("sh", "").replace("sz", "")
            
            # 获取股东信息
            shareholders = ak.stock_zh_a_gdhs_detail_em(symbol=clean_code)
            print(f"✅ 成功获取 {stock_code} 股权结构数据")
            return shareholders
            
        except Exception as e:
            print(f"❌ 获取股权结构失败: {e}")
            return pd.DataFrame()
    
    def get_business_forecast(self, stock_code: str) -> pd.DataFrame:
        """
        获取业绩预测数据
        
        Args:
            stock_code: 股票代码
            
        Returns:
            业绩预测DataFrame
        """
        try:
            # 标准化股票代码
            stock_code = self._normalize_stock_code(stock_code)
            
            # 获取业绩预测
            forecast = ak.stock_profit_forecast_ths(indicator="业绩预测详表-详细指标预测", symbol=stock_code)
            print(f"✅ 成功获取 {stock_code} 业绩预测数据")
            return forecast
            
        except Exception as e:
            print(f"❌ 获取业绩预测失败: {e}")
            return pd.DataFrame()
    
    def get_exchange_rate_data(self) -> pd.DataFrame:
        """获取汇率数据"""
        try:
            exchange_rate = ak.stock_sgt_settlement_exchange_rate_szse()
            print("✅ 成功获取汇率数据")
            return exchange_rate
        except Exception as e:
            print(f"❌ 获取汇率数据失败: {e}")
            return pd.DataFrame()
    
    def _normalize_stock_code(self, stock_code: str) -> str:
        """标准化股票代码为akshare格式"""
        # 去掉所有非数字字符
        clean_code = ''.join(filter(str.isdigit, stock_code))
        
        # 如果是6位数字，添加前缀
        if len(clean_code) == 6:
            if clean_code.startswith('6'):
                return f"sh{clean_code}"
            elif clean_code.startswith(('0', '3')):
                return f"sz{clean_code}"
        
        # 如果已经有前缀，直接返回
        if stock_code.startswith(('sh', 'sz')):
            return stock_code
            
        return clean_code
    
    def save_data_to_csv(self, data: Dict[str, pd.DataFrame], output_dir: str, stock_code: str):
        """将数据保存为CSV文件"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        for data_type, df in data.items():
            if not df.empty:
                filename = f"{stock_code}_{data_type}.csv"
                filepath = os.path.join(output_dir, filename)
                df.to_csv(filepath, encoding='utf-8-sig', index=False)
                print(f"✅ 已保存 {data_type} 到 {filepath}")
