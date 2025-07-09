#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主控制脚本
可以单独运行各个流程或完整流程
"""

import os
import sys
import logging
from datetime import datetime

# 导入各个流程
from data_collection_pipeline import DataCollectionPipeline
from report_generation_pipeline import ReportGenerationPipeline
from document_conversion_pipeline import DocumentConversionPipeline

def setup_logging():
    """配置主控制脚本的日志"""
    os.makedirs("logs", exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_filename = f"logs/main_pipeline_{timestamp}.log"
    
    logger = logging.getLogger('MainPipeline')
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    
    file_handler = logging.FileHandler(log_filename, encoding='utf-8')
    console_handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def run_data_collection(company="商汤科技", code="00020", market="HK", search_engine="all"):
    """运行数据收集流程"""
    logger = logging.getLogger('MainPipeline')
    logger.info("\n" + "="*100)
    logger.info("🎯 开始数据收集流程")
    logger.info("="*100)
    
    try:
        pipeline = DataCollectionPipeline(
            target_company=company,
            target_company_code=code,
            target_company_market=market,
            search_engine=search_engine
        )
        
        success = pipeline.run_data_collection()
        
        if success:
            logger.info("✅ 数据收集流程完成")
            return True
        else:
            logger.error("❌ 数据收集流程失败")
            return False
            
    except Exception as e:
        logger.error(f"❌ 数据收集流程异常: {e}")
        return False

def run_report_generation(company="商汤科技", code="00020", market="HK"):
    """运行研报生成流程"""
    logger = logging.getLogger('MainPipeline')
    logger.info("\n" + "="*100)
    logger.info("🎯 开始研报生成流程")
    logger.info("="*100)
    
    try:
        pipeline = ReportGenerationPipeline(
            target_company=company,
            target_company_code=code,
            target_company_market=market
        )
        
        output_file = pipeline.generate_report()
        
        if output_file:
            logger.info(f"✅ 研报生成流程完成: {output_file}")
            return output_file
        else:
            logger.error("❌ 研报生成流程失败")
            return None
            
    except Exception as e:
        logger.error(f"❌ 研报生成流程异常: {e}")
        return None

def run_document_conversion(md_path=None):
    """运行文档转换流程"""
    logger = logging.getLogger('MainPipeline')
    logger.info("\n" + "="*100)
    logger.info("🎯 开始文档转换流程")
    logger.info("="*100)
    
    try:
        pipeline = DocumentConversionPipeline()
        
        result = pipeline.run_conversion(md_path)
        
        if result:
            logger.info("✅ 文档转换流程完成")
            return result
        else:
            logger.error("❌ 文档转换流程失败")
            return None
            
    except Exception as e:
        logger.error(f"❌ 文档转换流程异常: {e}")
        return None

def run_full_pipeline(company="商汤科技", code="00020", market="HK", search_engine="all"):
    """运行完整流程"""
    logger = logging.getLogger('MainPipeline')
    logger.info("\n" + "="*100)
    logger.info("🎯 开始完整研报生成流程")
    logger.info("="*100)
    
    try:
        # 1. 数据收集
        logger.info("📊 第一阶段：数据收集")
        if not run_data_collection(company, code, market, search_engine):
            logger.error("❌ 数据收集失败，终止流程")
            return False
        
        # 2. 研报生成
        logger.info("📋 第二阶段：研报生成")
        md_file = run_report_generation(company, code, market)
        if not md_file:
            logger.error("❌ 研报生成失败，终止流程")
            return False
        
        # 3. 文档转换
        logger.info("📄 第三阶段：文档转换")
        conversion_result = run_document_conversion(md_file)
        if not conversion_result:
            logger.error("❌ 文档转换失败")
            return False
        
        # 4. 输出结果
        logger.info("\n" + "="*100)
        logger.info("🎉 完整流程执行完毕！")
        logger.info(f"📊 数据收集: 完成")
        logger.info(f"📋 研报生成: {md_file}")
        logger.info(f"📄 文档转换: {conversion_result['docx']}")
        logger.info("="*100)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 完整流程异常: {e}")
        return False

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='金融研报生成主控制脚本')
    parser.add_argument('--stage', choices=['1', '2', '3', 'all'], default='all',
                       help='执行阶段: 1(数据收集), 2(研报生成), 3(文档转换), all(完整流程)')
    parser.add_argument('--company', default='商汤科技', help='目标公司名称')
    parser.add_argument('--code', default='00020', help='股票代码')
    parser.add_argument('--market', default='HK', help='市场代码')
    parser.add_argument('--search-engine', choices=['ddg', 'sogou', 'all'], default='all',
                       help='搜索引擎选择')
    parser.add_argument('--input', help='输入文件路径（用于阶段2或3）')
    
    args = parser.parse_args()
    
    # 设置日志
    logger = setup_logging()
    
    # 根据阶段执行不同的流程
    if args.stage == '1':
        # 仅执行数据收集
        logger.info("🚀 仅执行数据收集流程")
        success = run_data_collection(args.company, args.code, args.market, args.search_engine)
        if success:
            print("\n🎉 数据收集流程执行完毕！")
        else:
            print("\n❌ 数据收集流程执行失败！")
            
    elif args.stage == '2':
        # 仅执行研报生成
        logger.info("🚀 仅执行研报生成流程")
        md_file = run_report_generation(args.company, args.code, args.market)
        if md_file:
            print(f"\n🎉 研报生成流程执行完毕！")
            print(f"📋 研报文件: {md_file}")
        else:
            print("\n❌ 研报生成流程执行失败！")
            
    elif args.stage == '3':
        # 仅执行文档转换
        logger.info("🚀 仅执行文档转换流程")
        result = run_document_conversion(args.input)
        if result:
            print(f"\n🎉 文档转换流程执行完毕！")
            print(f"📄 原始文件: {result['original_md']}")
            print(f"📝 处理后文件: {result['processed_md']}")
            print(f"📋 Word文档: {result['docx']}")
        else:
            print("\n❌ 文档转换流程执行失败！")
            
    else:
        # 执行完整流程
        logger.info("🚀 执行完整研报生成流程")
        success = run_full_pipeline(args.company, args.code, args.market, args.search_engine)
        if success:
            print("\n🎉 完整流程执行完毕！")
        else:
            print("\n❌ 完整流程执行失败！")

if __name__ == "__main__":
    main() 