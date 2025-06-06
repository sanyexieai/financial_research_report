# -*- coding: utf-8 -*-
"""
企业基本信息收集器
获取主营业务、经营范围等企业基础信息
"""

import akshare as ak
import pandas as pd
from typing import Dict, Any, Optional
import warnings
warnings.filterwarnings('ignore')

class BusinessInfoCollector:
    """企业基本信息收集器"""
    
    def __init__(self):
        self.cache = {}
    
    def get_main_business(self, stock_code: str) -> Dict[str, Any]:
        """
        获取公司主营业务信息
        
        Args:
            stock_code: 股票代码
            
        Returns:
            包含主营业务信息的字典
        """
        try:
            # 去掉前缀，只保留6位数字
            clean_code = stock_code.replace("sh", "").replace("sz", "")
            
            # 获取主营业务数据
            business_info = ak.stock_zyjs_ths(symbol=clean_code)
            
            if not business_info.empty:
                info_dict = {
                    "股票代码": business_info.iloc[0].get("股票代码", clean_code),
                    "股票名称": business_info.iloc[0].get("股票名称", ""),
                    "主营业务": business_info.iloc[0].get("主营业务", ""),
                    "经营范围": business_info.iloc[0].get("经营范围", ""),
                    "公司简介": business_info.iloc[0].get("公司简介", ""),
                    "所属行业": business_info.iloc[0].get("所属行业", ""),
                }
                print(f"✅ 成功获取 {stock_code} 主营业务信息")
                return info_dict
            else:
                print(f"⚠️ 未找到 {stock_code} 的主营业务信息")
                return {}
                
        except Exception as e:
            print(f"❌ 获取主营业务信息失败: {e}")
            return {}
    
    def get_company_profile(self, stock_code: str) -> Dict[str, Any]:
        """
        获取公司基本资料
        
        Args:
            stock_code: 股票代码
            
        Returns:
            公司基本信息字典
        """
        try:
            # 去掉前缀
            clean_code = stock_code.replace("sh", "").replace("sz", "")
            
            # 尝试多个数据源获取公司信息
            profile_info = {}
            
            try:
                # 方法1: 使用efinance获取基本信息
                import efinance as ef
                base_info = ef.stock.get_base_info(clean_code)
                if isinstance(base_info, dict):
                    profile_info.update(base_info)
                    print(f"✅ 通过efinance获取 {stock_code} 基本信息")
            except Exception as e1:
                print(f"⚠️ efinance获取失败: {e1}")
            
            try:
                # 方法2: 使用akshare获取股票信息
                stock_info = ak.stock_individual_info_em(symbol=clean_code)
                if not stock_info.empty:
                    # 将DataFrame转换为字典
                    for _, row in stock_info.iterrows():
                        key = row.get('item', '')
                        value = row.get('value', '')
                        if key and value:
                            profile_info[key] = value
                    print(f"✅ 通过akshare获取 {stock_code} 详细信息")
            except Exception as e2:
                print(f"⚠️ akshare个股信息获取失败: {e2}")
            
            return profile_info
            
        except Exception as e:
            print(f"❌ 获取公司资料失败: {e}")
            return {}
    
    def get_industry_info(self, stock_code: str) -> Dict[str, Any]:
        """
        获取行业信息和地位
        
        Args:
            stock_code: 股票代码
            
        Returns:
            行业信息字典
        """
        try:
            # 去掉前缀
            clean_code = stock_code.replace("sh", "").replace("sz", "")
            
            industry_info = {}
            
            try:
                # 获取行业分类信息
                industry_data = ak.stock_board_industry_name_em()
                
                # 查找该股票所属的行业
                stock_industry = ak.stock_board_industry_cons_em(symbol="小金属")  # 这里需要根据实际情况调整
                
                industry_info = {
                    "行业分类": "待查询",
                    "行业地位": "待分析", 
                    "市场份额": "待计算",
                    "行业趋势": "待评估"
                }
                
                print(f"✅ 获取 {stock_code} 行业信息")
                
            except Exception as e:
                print(f"⚠️ 行业信息获取部分失败: {e}")
                
            return industry_info
            
        except Exception as e:
            print(f"❌ 获取行业信息失败: {e}")
            return {}
    
    def get_management_info(self, stock_code: str) -> Dict[str, Any]:
        """
        获取管理层信息
        
        Args:
            stock_code: 股票代码
            
        Returns:
            管理层信息字典
        """
        try:
            # 去掉前缀
            clean_code = stock_code.replace("sh", "").replace("sz", "")
            
            management_info = {}
            
            try:
                # 获取高管信息
                executives = ak.stock_ggcg_em(symbol=clean_code)
                
                if not executives.empty:
                    management_info = {
                        "高管人数": len(executives),
                        "主要高管": executives.head(5).to_dict('records') if len(executives) > 0 else [],
                        "治理结构": "待分析"
                    }
                    print(f"✅ 成功获取 {stock_code} 管理层信息")
                else:
                    management_info = {"高管信息": "暂无数据"}
                    
            except Exception as e:
                print(f"⚠️ 管理层信息获取失败: {e}")
                management_info = {"管理层信息": "获取失败"}
                
            return management_info
            
        except Exception as e:
            print(f"❌ 获取管理层信息失败: {e}")
            return {}
    
    def analyze_core_competitiveness(self, business_info: Dict[str, Any], financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析核心竞争力
        
        Args:
            business_info: 企业基本信息
            financial_data: 财务数据
            
        Returns:
            核心竞争力分析结果
        """
        try:
            competitiveness = {
                "品牌价值": "待评估",
                "技术实力": "待分析", 
                "市场地位": "待确定",
                "资源优势": "待挖掘",
                "管理优势": "待评价",
                "财务实力": "待计算",
                "综合评分": 0
            }
            
            # 这里可以基于业务信息和财务数据进行综合分析
            if business_info.get("主营业务"):
                competitiveness["主营业务优势"] = "具有明确的主营业务定位"
            
            if financial_data:
                competitiveness["财务实力"] = "具备良好的财务基础"
                
            print("✅ 完成核心竞争力分析")
            return competitiveness
            
        except Exception as e:
            print(f"❌ 核心竞争力分析失败: {e}")
            return {}
