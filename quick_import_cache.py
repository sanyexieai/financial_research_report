#!/usr/bin/env python3
"""
快速导入搜索缓存脚本
简化版本，用于快速测试
"""

import os
import json
import glob
from datetime import datetime
from dotenv import load_dotenv

# 导入RAG组件
from utils.rag_postgres import RAGPostgresHelper
from config.database_config import db_config

# 加载环境变量
load_dotenv()

def quick_import_cache():
    """快速导入缓存"""
    print("开始快速导入搜索缓存...")
    
    # 初始化RAG助手
    try:
        rag_helper = RAGPostgresHelper(
            db_config=db_config.get_postgres_config(),
            model_name=db_config.get_rag_config()['model_name'],
            vector_dim=db_config.get_rag_config()['vector_dim']
        )
        print("✅ PostgreSQL RAG助手初始化成功")
    except Exception as e:
        print(f"❌ PostgreSQL RAG助手初始化失败: {e}")
        return False
    
    # 查找缓存文件
    cache_dir = "search_cache"
    if not os.path.exists(cache_dir):
        print(f"❌ 缓存目录不存在: {cache_dir}")
        return False
    
    cache_files = glob.glob(os.path.join(cache_dir, "*.json"))
    print(f"找到 {len(cache_files)} 个缓存文件")
    
    if not cache_files:
        print("没有找到缓存文件")
        return False
    
    # 统计信息
    total_files = len(cache_files)
    processed_files = 0
    added_documents = 0
    
    # 处理前5个文件作为测试
    test_files = cache_files[:5]
    print(f"测试导入前 {len(test_files)} 个文件...")
    
    for i, filepath in enumerate(test_files, 1):
        filename = os.path.basename(filepath)
        print(f"处理 {i}/{len(test_files)}: {filename}")
        
        try:
            # 读取缓存文件
            with open(filepath, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # 提取搜索关键词
            search_keywords = cache_data.get('search_keywords', '')
            if not search_keywords:
                # 从文件名推断
                search_keywords = filename.replace('.json', '').replace('_', ' ')
            
            # 转换搜索结果
            results = []
            for result in cache_data.get('results', []):
                search_result = {
                    'title': result.get('title', ''),
                    'description': result.get('description', ''),
                    'url': result.get('url', ''),
                    'engine': result.get('engine', [])
                }
                results.append(search_result)
            
            if results:
                # 添加到知识库
                added_count = rag_helper.add_search_results(results, search_keywords)
                if added_count > 0:
                    print(f"  ✅ 导入 {added_count} 个文档块，关键词: {search_keywords}")
                    added_documents += added_count
                else:
                    print(f"  ⚠️  无新文档，可能已存在")
                
                processed_files += 1
            else:
                print(f"  ⚠️  无有效结果")
                
        except Exception as e:
            print(f"  ❌ 处理失败: {e}")
    
    # 显示结果
    print("\n" + "="*50)
    print("导入完成！")
    print(f"处理文件: {processed_files}/{len(test_files)}")
    print(f"新增文档块: {added_documents}")
    
    # 显示知识库统计
    try:
        stats = rag_helper.get_statistics()
        print(f"知识库统计: {stats['total_documents']} 个文档, {stats['total_chunks']} 个块")
        print(f"最新更新: {stats.get('last_updated', '未知')}")
    except Exception as e:
        print(f"获取统计失败: {e}")
    
    print("="*50)
    return True

if __name__ == "__main__":
    success = quick_import_cache()
    if success:
        print("✅ 快速导入测试成功！")
        print("如需导入全部缓存，请运行: python import_search_cache.py")
    else:
        print("❌ 快速导入测试失败！") 