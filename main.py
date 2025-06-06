# -*- coding: utf-8 -*-
"""
公司研报生成系统主入口
"""

import os
import sys
import argparse
import asyncio
from datetime import datetime
from typing import Dict, Any

from config.llm_config import LLMConfig
from core.research_report_generator import ResearchReportGenerator
from utils.llm_helper import LLMHelper

def create_output_dir(company_name: str) -> str:
    """创建输出目录"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = f"reports/{company_name}_{timestamp}"
    os.makedirs(output_dir, exist_ok=True)
    return output_dir

async def generate_report(
    company_name: str,
    stock_code: str = None,
    output_dir: str = None,
    config_file: str = None
) -> Dict[str, Any]:
    """
    生成公司研报
    
    Args:
        company_name: 公司名称
        stock_code: 股票代码 (可选)
        output_dir: 输出目录 (可选)
        config_file: 配置文件路径 (可选)
    
    Returns:
        生成结果
    """
    try:
        # 加载配置
        if config_file and os.path.exists(config_file):
            config = LLMConfig.from_file(config_file)
        else:
            config = LLMConfig()
        
        # 创建输出目录
        if not output_dir:
            output_dir = create_output_dir(company_name)
        
        print(f"开始生成 {company_name} 的研报...")
        print(f"输出目录: {output_dir}")
        
        # 初始化研报生成器
        generator = ResearchReportGenerator(config)
        
        # 生成研报
        result = await generator.generate_report(
            company_name=company_name,
            stock_code=stock_code,
            output_dir=output_dir
        )
        
        if result['success']:
            print(f"\n✅ 研报生成成功!")
            print(f"📄 JSON报告: {result['json_file']}")
            print(f"📝 Markdown报告: {result['markdown_file']}")
            
            # 打印报告摘要
            if 'report_data' in result:
                report_data = result['report_data']
                print(f"\n📊 报告摘要:")
                print(f"- 公司名称: {report_data.get('company_info', {}).get('company_name', '未知')}")
                print(f"- 主营业务: {report_data.get('company_info', {}).get('main_business', '未知')}")
                print(f"- 投资评级: {report_data.get('investment_recommendation', {}).get('rating', '未评级')}")
                print(f"- 目标价格: {report_data.get('investment_recommendation', {}).get('target_price', '未设定')}")
        else:
            print(f"❌ 研报生成失败: {result.get('error', '未知错误')}")
        
        return result
        
    except Exception as e:
        error_msg = f"生成研报时发生错误: {str(e)}"
        print(f"❌ {error_msg}")
        return {
            'success': False,
            'error': error_msg
        }

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="公司研报生成系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  python main.py --company "平安银行"
  python main.py --company "平安银行" --stock-code "000001.SZ"
  python main.py --company "平安银行" --output-dir "./my_reports"
  python main.py --company "平安银行" --config "./my_config.yaml"
        """
    )
    
    parser.add_argument(
        "--company", "-c",
        required=True,
        help="公司名称 (必需)"
    )
    
    parser.add_argument(
        "--stock-code", "-s",
        help="股票代码 (可选，如: 000001.SZ)"
    )
    
    parser.add_argument(
        "--output-dir", "-o",
        help="输出目录 (可选，默认为 reports/公司名_时间戳)"
    )
    
    parser.add_argument(
        "--config", "-cfg",
        help="配置文件路径 (可选，默认使用环境变量)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="显示详细输出"
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        import logging
        logging.basicConfig(level=logging.INFO)
    
    # 运行异步任务
    result = asyncio.run(generate_report(
        company_name=args.company,
        stock_code=args.stock_code,
        output_dir=args.output_dir,
        config_file=args.config
    ))
    
    # 返回适当的退出码
    sys.exit(0 if result['success'] else 1)

if __name__ == "__main__":
    main()
