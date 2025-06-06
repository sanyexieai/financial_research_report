# -*- coding: utf-8 -*-
"""
公司研报生成系统使用示例
"""

import asyncio
import os
from pathlib import Path

from config.llm_config import LLMConfig
from core.research_report_generator import ResearchReportGenerator

async def example_basic_usage():
    """基本使用示例"""
    print("📊 基本使用示例：生成平安银行研报")
    print("=" * 50)
    
    try:
        # 初始化配置
        config = LLMConfig()
        
        # 创建研报生成器
        generator = ResearchReportGenerator(config)
        
        # 生成研报
        result = await generator.generate_report(
            company_name="平安银行",
            stock_code="000001.SZ",
            output_dir="./example_reports"
        )
        
        if result['success']:
            print("✅ 研报生成成功！")
            print(f"📄 JSON报告: {result['json_file']}")
            print(f"📝 Markdown报告: {result['markdown_file']}")
            
            # 展示部分结果
            if 'report_data' in result:
                report_data = result['report_data']
                print(f"\n📋 报告预览:")
                print(f"公司名称: {report_data.get('company_info', {}).get('company_name', '未知')}")
                print(f"行业: {report_data.get('company_info', {}).get('industry', '未知')}")
                print(f"投资评级: {report_data.get('investment_recommendation', {}).get('rating', '未评级')}")
        else:
            print(f"❌ 研报生成失败: {result.get('error', '未知错误')}")
            
    except Exception as e:
        print(f"❌ 示例运行失败: {e}")

async def example_batch_generation():
    """批量生成示例"""
    print("\n📊 批量生成示例：生成多家银行研报")
    print("=" * 50)
    
    # 银行股票列表
    banks = [
        {"name": "平安银行", "code": "000001.SZ"},
        {"name": "招商银行", "code": "600036.SH"},
        {"name": "兴业银行", "code": "601166.SH"}
    ]
    
    try:
        config = LLMConfig()
        generator = ResearchReportGenerator(config)
        
        results = []
        for bank in banks:
            print(f"\n正在生成 {bank['name']} 研报...")
            
            result = await generator.generate_report(
                company_name=bank['name'],
                stock_code=bank['code'],
                output_dir=f"./batch_reports/{bank['name']}"
            )
            
            results.append({
                'company': bank['name'],
                'success': result['success'],
                'files': result.get('json_file', '') if result['success'] else '',
                'error': result.get('error', '') if not result['success'] else ''
            })
        
        # 汇总结果
        print(f"\n📋 批量生成结果汇总:")
        for result in results:
            status = "✅ 成功" if result['success'] else "❌ 失败"
            print(f"{result['company']}: {status}")
            if not result['success']:
                print(f"  错误: {result['error']}")
                
    except Exception as e:
        print(f"❌ 批量生成失败: {e}")

async def example_custom_analysis():
    """自定义分析示例"""
    print("\n📊 自定义分析示例：深度财务分析")
    print("=" * 50)
    
    try:
        from data_collectors.financial_data_collector import FinancialDataCollector
        from analyzers.financial_ratio_analyzer import FinancialRatioAnalyzer
        from analyzers.valuation_analyzer import ValuationAnalyzer
        
        # 收集财务数据
        collector = FinancialDataCollector()
        financial_data = await collector.collect_financial_data("平安银行", "000001.SZ")
        
        if financial_data:
            print("✅ 财务数据收集完成")
            
            # 财务比率分析
            ratio_analyzer = FinancialRatioAnalyzer()
            
            # ROE分解
            roe_analysis = ratio_analyzer.calculate_roe_decomposition(financial_data)
            print(f"📊 ROE分解分析: {len(roe_analysis)} 个指标")
            
            # 盈利能力分析
            profitability = ratio_analyzer.calculate_profitability_ratios(financial_data)
            print(f"📊 盈利能力分析: {len(profitability)} 个指标")
            
            # 估值分析
            config = LLMConfig()
            valuation_analyzer = ValuationAnalyzer(config)
            valuation_result = await valuation_analyzer.perform_valuation_analysis(
                financial_data, {"company_name": "平安银行"}
            )
            print(f"💰 估值分析完成")
            
        else:
            print("❌ 财务数据收集失败")
            
    except Exception as e:
        print(f"❌ 自定义分析失败: {e}")

async def example_with_config_file():
    """使用配置文件示例"""
    print("\n📊 配置文件使用示例")
    print("=" * 50)
    
    try:
        # 创建示例配置文件
        config_content = """
llm:
  model: "gpt-3.5-turbo"
  max_tokens: 3000
  temperature: 0.5

analysis:
  valuation_methods: ["PE"]
  scenario_analysis: false
  analysis_years: 2

output:
  detailed_analysis: false
  include_charts: false
"""
        
        config_file = "example_config.yaml"
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(config_content)
        
        # 使用配置文件
        config = LLMConfig.from_file(config_file)
        generator = ResearchReportGenerator(config)
        
        result = await generator.generate_report(
            company_name="平安银行",
            output_dir="./config_example_reports"
        )
        
        if result['success']:
            print("✅ 使用自定义配置生成研报成功！")
        else:
            print(f"❌ 生成失败: {result.get('error')}")
        
        # 清理配置文件
        if os.path.exists(config_file):
            os.remove(config_file)
            
    except Exception as e:
        print(f"❌ 配置文件示例失败: {e}")

async def main():
    """主函数"""
    print("🚀 公司研报生成系统使用示例")
    print("=" * 60)
    
    examples = [
        ("基本使用", example_basic_usage),
        ("批量生成", example_batch_generation),
        ("自定义分析", example_custom_analysis),
        ("配置文件使用", example_with_config_file)
    ]
    
    for name, example_func in examples:
        try:
            await example_func()
            await asyncio.sleep(1)  # 避免API调用过快
        except Exception as e:
            print(f"❌ {name} 示例执行失败: {e}")
    
    print(f"\n🎉 所有示例执行完成！")
    print(f"\n📚 更多使用方法请参考:")
    print(f"1. README.md - 详细文档")
    print(f"2. python main.py --help - 命令行帮助")
    print(f"3. python test_system.py - 系统测试")

if __name__ == "__main__":
    asyncio.run(main())
