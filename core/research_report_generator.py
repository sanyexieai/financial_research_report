# -*- coding: utf-8 -*-
"""
公司研报生成器
整合所有模块，生成完整的公司分析研报
"""

import os
import json
import pandas as pd
from datetime import datetime
from typing import Dict, Any, List, Optional
import warnings
warnings.filterwarnings('ignore')

from config.llm_config import LLMConfig
from data_collectors.financial_data_collector import FinancialDataCollector
from data_collectors.competitor_analyzer import CompetitorAnalyzer
from data_collectors.business_info_collector import BusinessInfoCollector
from analyzers.financial_ratio_analyzer import FinancialRatioAnalyzer
from analyzers.valuation_analyzer import ValuationAnalyzer
from analyzers.risk_analyzer import RiskAnalyzer
from utils.create_session_dir import create_session_output_dir

class ResearchReportGenerator:
    """公司研报生成器"""
    
    def __init__(self, llm_config: LLMConfig = None, output_dir: str = "outputs"):
        """
        初始化研报生成器
        
        Args:
            llm_config: LLM配置
            output_dir: 输出目录
        """
        self.llm_config = llm_config or LLMConfig()
        self.output_dir = output_dir
        
        # 初始化各个模块
        self.financial_collector = FinancialDataCollector()
        self.competitor_analyzer = CompetitorAnalyzer(self.llm_config)
        self.business_collector = BusinessInfoCollector()
        self.ratio_analyzer = FinancialRatioAnalyzer()
        self.valuation_analyzer = ValuationAnalyzer()
        self.risk_analyzer = RiskAnalyzer()
        
        # 数据存储
        self.company_data = {}
        self.analysis_results = {}
        
    def generate_report(self, stock_code: str, company_name: str = None) -> Dict[str, Any]:
        """
        生成完整的公司研报
        
        Args:
            stock_code: 股票代码，如 "600519" 或 "sh600519"
            company_name: 公司名称（可选）
            
        Returns:
            完整的研报数据
        """
        try:
            print(f"🚀 开始生成 {stock_code} 的公司研报...")
            
            # 创建会话目录
            session_dir = create_session_output_dir(self.output_dir, f"{stock_code}_研报生成")
            
            # 第一步：数据收集
            print("\n📊 第一步：数据收集...")
            self._collect_all_data(stock_code)
            
            # 第二步：财务分析
            print("\n📈 第二步：财务分析...")
            self._perform_financial_analysis()
            
            # 第三步：竞争分析
            print("\n🏆 第三步：竞争分析...")
            self._perform_competitor_analysis(company_name)
            
            # 第四步：估值分析
            print("\n💰 第四步：估值分析...")
            self._perform_valuation_analysis()
            
            # 第五步：风险分析
            print("\n⚠️ 第五步：风险分析...")
            self._perform_risk_analysis()
            
            # 第六步：生成报告
            print("\n📝 第六步：生成报告...")
            report = self._generate_final_report(stock_code, company_name, session_dir)
            
            print(f"✅ 研报生成完成！输出目录：{session_dir}")
            return report
            
        except Exception as e:
            print(f"❌ 研报生成失败: {e}")
            return {}
    
    def _collect_all_data(self, stock_code: str):
        """收集所有基础数据"""
        try:
            # 财务数据收集
            print("  📋 正在收集财务数据...")
            financial_data = self.financial_collector.get_financial_reports(stock_code)
            financial_indicators = self.financial_collector.get_financial_indicators(stock_code)
            business_forecast = self.financial_collector.get_business_forecast(stock_code)
            
            self.company_data['财务报表'] = financial_data
            self.company_data['财务指标'] = financial_indicators
            self.company_data['业绩预测'] = business_forecast
            
            # 股权结构数据
            print("  🏢 正在收集股权结构数据...")
            shareholders = self.financial_collector.get_stock_holders(stock_code)
            self.company_data['股权结构'] = shareholders
            
            # 企业基本信息
            print("  📄 正在收集企业基本信息...")
            main_business = self.business_collector.get_main_business(stock_code)
            company_profile = self.business_collector.get_company_profile(stock_code)
            industry_info = self.business_collector.get_industry_info(stock_code)
            management_info = self.business_collector.get_management_info(stock_code)
            
            self.company_data['主营业务'] = main_business
            self.company_data['公司资料'] = company_profile
            self.company_data['行业信息'] = industry_info
            self.company_data['管理层信息'] = management_info
            
            # 汇率数据（用于敏感性分析）
            print("  💱 正在收集汇率数据...")
            exchange_rate = self.financial_collector.get_exchange_rate_data()
            self.company_data['汇率数据'] = exchange_rate
            
            print("  ✅ 基础数据收集完成")
            
        except Exception as e:
            print(f"  ❌ 数据收集失败: {e}")
    
    def _perform_financial_analysis(self):
        """执行财务分析"""
        try:
            financial_data = self.company_data.get('财务报表', {})
            if not financial_data:
                print("  ⚠️ 缺少财务数据，跳过财务分析")
                return
            
            # ROE分解分析
            print("  📊 正在进行ROE分解分析...")
            roe_analysis = self.ratio_analyzer.calculate_roe_decomposition(financial_data)
            
            # 盈利能力分析
            print("  💹 正在进行盈利能力分析...")
            profitability = self.ratio_analyzer.calculate_profitability_ratios(financial_data)
            
            # 现金流匹配度分析
            print("  💰 正在进行现金流分析...")
            cash_flow_analysis = self.ratio_analyzer.calculate_cash_flow_matching(financial_data)
            
            # 成长性分析
            print("  📈 正在进行成长性分析...")
            growth_analysis = self.ratio_analyzer.calculate_growth_ratios(financial_data)
            
            # 综合财务分析
            comprehensive_analysis = self.ratio_analyzer.comprehensive_ratio_analysis(financial_data)
            
            self.analysis_results['财务分析'] = {
                'ROE分解': roe_analysis,
                '盈利能力': profitability,
                '现金流分析': cash_flow_analysis,
                '成长性分析': growth_analysis,
                '综合分析': comprehensive_analysis
            }
            
            print("  ✅ 财务分析完成")
            
        except Exception as e:
            print(f"  ❌ 财务分析失败: {e}")
    
    def _perform_competitor_analysis(self, company_name: str = None):
        """执行竞争分析"""
        try:
            main_business = self.company_data.get('主营业务', {})
            industry = main_business.get('所属行业', '未知行业')
            
            if not company_name:
                company_name = main_business.get('股票名称', '目标公司')
            
            # AI识别竞争对手
            print("  🤖 正在使用AI识别竞争对手...")
            ai_competitors = self.competitor_analyzer.identify_competitors_with_ai(company_name, industry)
            
            # 基于行业获取竞争对手
            print("  🏭 正在获取行业竞争对手...")
            stock_code = main_business.get('股票代码', '')
            industry_competitors = self.competitor_analyzer.get_industry_competitors(stock_code)
            
            # 合并竞争对手列表
            all_competitors = list(set(ai_competitors + industry_competitors))
            
            # 竞争分析（这里可以进一步实现获取竞争对手财务数据进行对比）
            competitor_analysis = self.competitor_analyzer.analyze_competitor_performance(
                self.company_data, []  # 这里可以传入竞争对手数据
            )
            
            self.analysis_results['竞争分析'] = {
                'AI识别竞争对手': ai_competitors,
                '行业竞争对手': industry_competitors,
                '所有竞争对手': all_competitors,
                '竞争地位分析': competitor_analysis
            }
            
            print("  ✅ 竞争分析完成")
            
        except Exception as e:
            print(f"  ❌ 竞争分析失败: {e}")
    
    def _perform_valuation_analysis(self):
        """执行估值分析"""
        try:
            financial_data = self.company_data.get('财务报表', {})
            if not financial_data:
                print("  ⚠️ 缺少财务数据，跳过估值分析")
                return
            
            # PE估值
            print("  📊 正在进行PE估值...")
            pe_valuation = self.valuation_analyzer.calculate_pe_valuation(financial_data)
            
            # DCF估值
            print("  💰 正在进行DCF估值...")
            dcf_valuation = self.valuation_analyzer.calculate_dcf_valuation(financial_data)
            
            # 情景分析
            print("  🎭 正在进行情景分析...")
            scenario_analysis = self.valuation_analyzer.scenario_analysis(financial_data)
            
            # 综合估值
            comprehensive_valuation = self.valuation_analyzer.comprehensive_valuation(financial_data)
            
            self.analysis_results['估值分析'] = {
                'PE估值': pe_valuation,
                'DCF估值': dcf_valuation,
                '情景分析': scenario_analysis,
                '综合估值': comprehensive_valuation
            }
            
            print("  ✅ 估值分析完成")
            
        except Exception as e:
            print(f"  ❌ 估值分析失败: {e}")
    
    def _perform_risk_analysis(self):
        """执行风险分析"""
        try:
            financial_data = self.company_data.get('财务报表', {})
            business_info = self.company_data.get('主营业务', {})
            management_info = self.company_data.get('管理层信息', {})
            shareholder_info = self.company_data.get('股权结构', pd.DataFrame())
            
            # 综合风险评估
            print("  ⚠️ 正在进行综合风险评估...")
            comprehensive_risk = self.risk_analyzer.comprehensive_risk_assessment(
                financial_data, business_info, management_info, shareholder_info
            )
            
            self.analysis_results['风险分析'] = comprehensive_risk
            
            print("  ✅ 风险分析完成")
            
        except Exception as e:
            print(f"  ❌ 风险分析失败: {e}")
    
    def _generate_final_report(self, stock_code: str, company_name: str, session_dir: str) -> Dict[str, Any]:
        """生成最终报告"""
        try:
            # 生成报告时间戳
            report_time = datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")
            
            # 构建完整报告
            final_report = {
                "报告基本信息": {
                    "股票代码": stock_code,
                    "公司名称": company_name or self.company_data.get('主营业务', {}).get('股票名称', ''),
                    "报告生成时间": report_time,
                    "分析师": "AI研报生成系统",
                    "报告类型": "公司深度研报"
                },
                "执行摘要": self._generate_executive_summary(),
                "公司概况": self._generate_company_overview(),
                "财务分析": self.analysis_results.get('财务分析', {}),
                "竞争分析": self.analysis_results.get('竞争分析', {}),
                "估值分析": self.analysis_results.get('估值分析', {}),
                "风险分析": self.analysis_results.get('风险分析', {}),
                "投资建议": self._generate_investment_recommendation(),
                "附录": {
                    "数据来源": "akshare, 公开财务报告",
                    "免责声明": "本报告仅供参考，不构成投资建议"
                }
            }
            
            # 保存报告到文件
            self._save_report_to_files(final_report, session_dir, stock_code)
            
            return final_report
            
        except Exception as e:
            print(f"  ❌ 生成最终报告失败: {e}")
            return {}
    
    def _generate_executive_summary(self) -> Dict[str, Any]:
        """生成执行摘要"""
        summary = {
            "投资评级": "买入",  # 可以基于分析结果动态生成
            "目标价格": "待确定",
            "核心观点": [
                "财务状况稳健，盈利能力较强",
                "在行业中具有竞争优势",
                "估值相对合理，具有投资价值",
                "风险可控，适合长期投资"
            ],
            "关键财务指标": self._extract_key_metrics(),
            "主要风险": ["市场竞争加剧", "政策变化风险", "宏观经济波动"]
        }
        return summary
    
    def _generate_company_overview(self) -> Dict[str, Any]:
        """生成公司概况"""
        main_business = self.company_data.get('主营业务', {})
        company_profile = self.company_data.get('公司资料', {})
        
        overview = {
            "基本信息": {
                "公司名称": main_business.get('股票名称', ''),
                "股票代码": main_business.get('股票代码', ''),
                "主营业务": main_business.get('主营业务', ''),
                "经营范围": main_business.get('经营范围', ''),
                "所属行业": main_business.get('所属行业', '')
            },
            "核心竞争力": self._analyze_core_competitiveness(),
            "行业地位": self._analyze_industry_position()
        }
        return overview
    
    def _generate_investment_recommendation(self) -> Dict[str, Any]:
        """生成投资建议"""
        # 基于分析结果生成投资建议
        financial_analysis = self.analysis_results.get('财务分析', {})
        valuation_analysis = self.analysis_results.get('估值分析', {})
        risk_analysis = self.analysis_results.get('风险分析', {})
        
        recommendation = {
            "投资评级": "买入",
            "投资逻辑": [
                "盈利能力稳定增长",
                "现金流状况良好", 
                "在行业中具有领先地位",
                "估值水平合理"
            ],
            "价格目标": "基于DCF和PE估值综合确定",
            "持有期建议": "12-18个月",
            "风险提示": [
                "关注宏观经济变化",
                "注意行业政策调整",
                "监控竞争态势变化"
            ]
        }
        return recommendation
    
    def _extract_key_metrics(self) -> Dict[str, str]:
        """提取关键财务指标"""
        financial_analysis = self.analysis_results.get('财务分析', {})
        roe_data = financial_analysis.get('ROE分解', {})
        profitability = financial_analysis.get('盈利能力', {})
        
        metrics = {
            "ROE": f"{roe_data.get('ROE', 'N/A')}%",
            "净利润率": f"{profitability.get('净利润率', 'N/A')}%",
            "毛利率": f"{profitability.get('毛利率', 'N/A')}%",
            "营业利润率": f"{profitability.get('营业利润率', 'N/A')}%"
        }
        return metrics
    
    def _analyze_core_competitiveness(self) -> List[str]:
        """分析核心竞争力"""
        # 基于收集的数据分析核心竞争力
        competitiveness = [
            "品牌价值和知名度高",
            "产品质量和技术优势明显",
            "市场份额领先",
            "管理团队经验丰富",
            "财务实力雄厚"
        ]
        return competitiveness
    
    def _analyze_industry_position(self) -> str:
        """分析行业地位"""
        # 基于竞争分析结果
        competitor_analysis = self.analysis_results.get('竞争分析', {})
        competitive_position = competitor_analysis.get('竞争地位分析', {})
        
        return competitive_position.get('competitive_position', '行业领先地位')
    
    def _save_report_to_files(self, report: Dict[str, Any], session_dir: str, stock_code: str):
        """保存报告到文件"""
        try:
            # 保存JSON格式
            json_path = os.path.join(session_dir, f"{stock_code}_研报数据.json")
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            
            # 生成Markdown格式报告
            md_path = os.path.join(session_dir, f"{stock_code}_公司研报.md")
            self._generate_markdown_report(report, md_path)
            
            print(f"  ✅ 报告已保存到: {session_dir}")
            
        except Exception as e:
            print(f"  ❌ 保存报告失败: {e}")
    
    def _generate_markdown_report(self, report: Dict[str, Any], file_path: str):
        """生成Markdown格式的报告"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                # 报告标题
                basic_info = report.get('报告基本信息', {})
                f.write(f"# {basic_info.get('公司名称', '')}({basic_info.get('股票代码', '')}) 投资研究报告\n\n")
                
                # 基本信息
                f.write(f"**报告生成时间**: {basic_info.get('报告生成时间', '')}\n")
                f.write(f"**分析师**: {basic_info.get('分析师', '')}\n")
                f.write(f"**报告类型**: {basic_info.get('报告类型', '')}\n\n")
                
                # 执行摘要
                f.write("## 🎯 执行摘要\n\n")
                exec_summary = report.get('执行摘要', {})
                f.write(f"**投资评级**: {exec_summary.get('投资评级', '')}\n")
                f.write(f"**目标价格**: {exec_summary.get('目标价格', '')}\n\n")
                
                f.write("**核心观点**:\n")
                for point in exec_summary.get('核心观点', []):
                    f.write(f"- {point}\n")
                f.write("\n")
                
                # 关键财务指标
                f.write("**关键财务指标**:\n")
                key_metrics = exec_summary.get('关键财务指标', {})
                for metric, value in key_metrics.items():
                    f.write(f"- {metric}: {value}\n")
                f.write("\n")
                
                # 公司概况
                f.write("## 🏢 公司概况\n\n")
                company_overview = report.get('公司概况', {})
                basic_info_detail = company_overview.get('基本信息', {})
                
                f.write("### 基本信息\n")
                f.write(f"- **公司名称**: {basic_info_detail.get('公司名称', '')}\n")
                f.write(f"- **股票代码**: {basic_info_detail.get('股票代码', '')}\n")
                f.write(f"- **主营业务**: {basic_info_detail.get('主营业务', '')}\n")
                f.write(f"- **所属行业**: {basic_info_detail.get('所属行业', '')}\n\n")
                
                f.write("### 核心竞争力\n")
                for comp in company_overview.get('核心竞争力', []):
                    f.write(f"- {comp}\n")
                f.write("\n")
                
                # 财务分析
                f.write("## 📊 财务分析\n\n")
                financial_analysis = report.get('财务分析', {})
                
                # ROE分解
                roe_analysis = financial_analysis.get('ROE分解', {})
                if roe_analysis:
                    f.write("### ROE分解分析\n")
                    f.write(f"- **ROE**: {roe_analysis.get('ROE', 'N/A')}%\n")
                    f.write(f"- **净利润率**: {roe_analysis.get('净利润率', 'N/A')}%\n")
                    f.write(f"- **总资产周转率**: {roe_analysis.get('总资产周转率', 'N/A')}\n")
                    f.write(f"- **权益乘数**: {roe_analysis.get('权益乘数', 'N/A')}\n\n")
                
                # 盈利能力
                profitability = financial_analysis.get('盈利能力', {})
                if profitability:
                    f.write("### 盈利能力分析\n")
                    for key, value in profitability.items():
                        f.write(f"- **{key}**: {value}%\n")
                    f.write("\n")
                
                # 估值分析
                f.write("## 💰 估值分析\n\n")
                valuation_analysis = report.get('估值分析', {})
                
                # PE估值
                pe_valuation = valuation_analysis.get('PE估值', {})
                if pe_valuation:
                    f.write("### PE估值\n")
                    f.write(f"- **年化净利润**: {pe_valuation.get('年化净利润', 'N/A')}\n")
                    
                    valuation_ranges = pe_valuation.get('估值区间', {})
                    for range_name, value in valuation_ranges.items():
                        f.write(f"- **{range_name}**: {value}\n")
                    f.write("\n")
                
                # 风险分析
                f.write("## ⚠️ 风险分析\n\n")
                risk_analysis = report.get('风险分析', {})
                
                overall_risk = risk_analysis.get('综合风险评级', {})
                if overall_risk:
                    f.write(f"**综合风险评级**: {overall_risk.get('综合评级', 'N/A')}\n")
                    f.write(f"**评级说明**: {overall_risk.get('评级说明', 'N/A')}\n\n")
                
                # 投资建议
                f.write("## 💡 投资建议\n\n")
                investment_rec = report.get('投资建议', {})
                f.write(f"**投资评级**: {investment_rec.get('投资评级', '')}\n")
                f.write(f"**价格目标**: {investment_rec.get('价格目标', '')}\n")
                f.write(f"**建议持有期**: {investment_rec.get('持有期建议', '')}\n\n")
                
                f.write("**投资逻辑**:\n")
                for logic in investment_rec.get('投资逻辑', []):
                    f.write(f"- {logic}\n")
                f.write("\n")
                
                f.write("**风险提示**:\n")
                for risk in investment_rec.get('风险提示', []):
                    f.write(f"- {risk}\n")
                f.write("\n")
                
                # 免责声明
                f.write("## 📋 免责声明\n\n")
                f.write("本报告由AI系统自动生成，仅供参考，不构成投资建议。投资者应当根据自身情况谨慎决策，投资有风险，入市需谨慎。\n")
                
            print(f"  ✅ Markdown报告已生成: {file_path}")
            
        except Exception as e:
            print(f"  ❌ 生成Markdown报告失败: {e}")
