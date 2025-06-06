# -*- coding: utf-8 -*-
"""
系统测试脚本
"""

import asyncio
import os
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config.llm_config import LLMConfig
from data_collectors.financial_data_collector import FinancialDataCollector
from data_collectors.business_info_collector import BusinessInfoCollector
from analyzers.financial_ratio_analyzer import FinancialRatioAnalyzer

async def test_configuration():
    """测试配置模块"""
    print("🔧 测试配置模块...")
    try:
        config = LLMConfig()
        print(f"✅ 配置加载成功")
        print(f"   模型: {config.model}")
        print(f"   最大token: {config.max_tokens}")
        return True
    except Exception as e:
        print(f"❌ 配置测试失败: {e}")
        return False

async def test_data_collection():
    """测试数据收集模块"""
    print("\n📊 测试数据收集模块...")
    try:
        # 测试财务数据收集器
        financial_collector = FinancialDataCollector()
        
        # 尝试获取平安银行的基本信息（不依赖API）
        test_data = {
            'company_name': '平安银行',
            'stock_code': '000001.SZ'
        }
        
        print(f"✅ 财务数据收集器初始化成功")
        
        # 测试企业信息收集器
        business_collector = BusinessInfoCollector()
        print(f"✅ 企业信息收集器初始化成功")
        
        return True
    except Exception as e:
        print(f"❌ 数据收集测试失败: {e}")
        return False

async def test_analysis_modules():
    """测试分析模块"""
    print("\n📈 测试分析模块...")
    try:
        # 测试财务比率分析器
        ratio_analyzer = FinancialRatioAnalyzer()
        
        # 创建模拟财务数据
        mock_financial_data = {
            'income_statement': {
                '2023': {'营业收入': 100000, '净利润': 10000},
                '2022': {'营业收入': 90000, '净利润': 9000},
                '2021': {'营业收入': 80000, '净利润': 8000}
            },
            'balance_sheet': {
                '2023': {'总资产': 500000, '净资产': 50000},
                '2022': {'总资产': 450000, '净资产': 45000},
                '2021': {'总资产': 400000, '净资产': 40000}
            },
            'cash_flow': {
                '2023': {'经营现金流': 12000},
                '2022': {'经营现金流': 11000},
                '2021': {'经营现金流': 10000}
            }
        }
        
        # 测试ROE分析
        roe_analysis = ratio_analyzer.calculate_roe_decomposition(mock_financial_data)
        print(f"✅ ROE分解分析完成")
        
        # 测试增长率分析
        growth_analysis = ratio_analyzer.calculate_growth_ratios(mock_financial_data)
        print(f"✅ 增长率分析完成")
        
        return True
    except Exception as e:
        print(f"❌ 分析模块测试失败: {e}")
        return False

async def test_output_directory():
    """测试输出目录创建"""
    print("\n📁 测试输出目录...")
    try:
        test_dir = "test_reports"
        os.makedirs(test_dir, exist_ok=True)
        
        if os.path.exists(test_dir):
            print(f"✅ 输出目录创建成功: {test_dir}")
            # 清理测试目录
            os.rmdir(test_dir)
            return True
        else:
            print(f"❌ 输出目录创建失败")
            return False
    except Exception as e:
        print(f"❌ 输出目录测试失败: {e}")
        return False

async def run_system_test():
    """运行系统测试"""
    print("🚀 开始系统测试...\n")
    
    tests = [
        ("配置模块", test_configuration),
        ("数据收集模块", test_data_collection), 
        ("分析模块", test_analysis_modules),
        ("输出目录", test_output_directory)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name}测试异常: {e}")
            results.append((test_name, False))
    
    # 输出测试结果
    print(f"\n📋 测试结果汇总:")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print("=" * 50)
    print(f"总计: {passed}/{len(results)} 项测试通过")
    
    if passed == len(results):
        print("\n🎉 所有测试通过！系统就绪。")
        print("\n📚 使用说明:")
        print("1. 配置环境变量: cp .env.example .env 并填入API密钥")
        print("2. 运行生成研报: python main.py --company '平安银行'")
    else:
        print(f"\n⚠️ 有 {len(results) - passed} 项测试失败，请检查系统配置")
    
    return passed == len(results)

if __name__ == "__main__":
    success = asyncio.run(run_system_test())
    sys.exit(0 if success else 1)
