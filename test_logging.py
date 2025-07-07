#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试日志记录功能
"""

from integrated_research_report_generator import IntegratedResearchReportGenerator

def test_logging():
    """测试日志记录功能"""
    print("开始测试日志记录功能...")
    
    # 创建生成器实例（会初始化日志）
    generator = IntegratedResearchReportGenerator(
        target_company="测试公司",
        target_company_code="00001",
        target_company_market="HK"
    )
    
    # 测试不同类型的日志
    generator.logger.info("这是一条信息日志")
    generator.logger.warning("这是一条警告日志")
    generator.logger.error("这是一条错误日志")
    
    print("日志测试完成！请检查 logs 目录下的日志文件。")

if __name__ == "__main__":
    test_logging() 