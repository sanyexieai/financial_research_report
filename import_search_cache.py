#!/usr/bin/env python3
"""
搜索缓存导入脚本
将search_cache目录下的搜索记录导入到PostgreSQL知识库
"""

import os
import json
import glob
import logging
from datetime import datetime
from typing import List, Dict, Any
from dotenv import load_dotenv

# 导入RAG组件
from utils.rag_postgres import RAGPostgresHelper
from config.database_config import db_config

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/import_cache_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('ImportCache')

# 加载环境变量
load_dotenv()

class SearchCacheImporter:
    """搜索缓存导入器"""
    
    def __init__(self):
        """初始化导入器"""
        self.cache_dir = "search_cache"
        self.rag_helper = None
        self.stats = {
            'total_files': 0,
            'processed_files': 0,
            'failed_files': 0,
            'total_documents': 0,
            'added_documents': 0,
            'skipped_documents': 0
        }
    
    def init_rag_helper(self):
        """初始化RAG助手"""
        try:
            self.rag_helper = RAGPostgresHelper(
                db_config=db_config.get_postgres_config(),
                rag_config=db_config.get_rag_config()
            )
            logger.info("PostgreSQL RAG助手初始化成功")
            return True
        except Exception as e:
            logger.error(f"PostgreSQL RAG助手初始化失败: {e}")
            return False
    
    def get_cache_files(self) -> List[str]:
        """获取所有缓存文件"""
        if not os.path.exists(self.cache_dir):
            logger.warning(f"缓存目录不存在: {self.cache_dir}")
            return []
        
        # 查找所有JSON缓存文件
        pattern = os.path.join(self.cache_dir, "*.json")
        cache_files = glob.glob(pattern)
        
        logger.info(f"找到 {len(cache_files)} 个缓存文件")
        return cache_files
    
    def parse_cache_file(self, filepath: str) -> Dict[str, Any]:
        """解析缓存文件"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 提取文件信息
            filename = os.path.basename(filepath)
            file_info = {
                'filepath': filepath,
                'filename': filename,
                'data': data,
                'search_keywords': data.get('search_keywords', ''),
                'max_results': data.get('max_results', 0),
                'timestamp': data.get('timestamp', ''),
                'results': data.get('results', [])
            }
            
            return file_info
            
        except Exception as e:
            logger.error(f"解析缓存文件失败 {filepath}: {e}")
            return None
    
    def convert_to_search_results(self, cache_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """将缓存数据转换为搜索结果格式"""
        results = []
        
        for result in cache_data.get('results', []):
            # 标准化结果格式
            search_result = {
                'title': result.get('title', ''),
                'description': result.get('description', ''),
                'url': result.get('url', ''),
                'engine': result.get('engine', [])
            }
            results.append(search_result)
        
        return results
    
    def import_cache_file(self, filepath: str) -> bool:
        """导入单个缓存文件"""
        try:
            logger.info(f"处理缓存文件: {os.path.basename(filepath)}")
            
            # 解析缓存文件
            cache_data = self.parse_cache_file(filepath)
            if not cache_data:
                self.stats['failed_files'] += 1
                return False
            
            # 获取搜索关键词
            search_keywords = cache_data['search_keywords']
            if not search_keywords:
                # 尝试从文件名推断关键词
                filename = cache_data['filename']
                search_keywords = filename.replace('.json', '').replace('_', ' ')
            
            # 转换搜索结果格式
            search_results = self.convert_to_search_results(cache_data)
            
            if not search_results:
                logger.warning(f"缓存文件无有效结果: {filepath}")
                self.stats['skipped_documents'] += 1
                return False
            
            # 添加到知识库
            added_count = self.rag_helper.add_search_results(search_results, search_keywords)
            
            if added_count > 0:
                logger.info(f"成功导入 {added_count} 个文档块，关键词: {search_keywords}")
                self.stats['added_documents'] += added_count
                self.stats['total_documents'] += len(search_results)
                return True
            else:
                logger.warning(f"无新文档添加，可能已存在，关键词: {search_keywords}")
                self.stats['skipped_documents'] += len(search_results)
                return True
                
        except Exception as e:
            logger.error(f"导入缓存文件失败 {filepath}: {e}")
            self.stats['failed_files'] += 1
            return False
    
    def import_all_cache(self, limit: int = None) -> bool:
        """导入所有缓存文件"""
        logger.info("开始导入搜索缓存...")
        
        # 初始化RAG助手
        if not self.init_rag_helper():
            return False
        
        # 获取缓存文件
        cache_files = self.get_cache_files()
        if not cache_files:
            logger.warning("没有找到缓存文件")
            return False
        
        # 限制处理文件数量
        if limit:
            cache_files = cache_files[:limit]
            logger.info(f"限制处理 {limit} 个文件")
        
        self.stats['total_files'] = len(cache_files)
        
        # 处理每个缓存文件
        for i, filepath in enumerate(cache_files, 1):
            logger.info(f"处理进度: {i}/{len(cache_files)}")
            
            if self.import_cache_file(filepath):
                self.stats['processed_files'] += 1
            
            # 每处理10个文件显示一次统计
            if i % 10 == 0:
                self.print_stats()
        
        # 最终统计
        self.print_final_stats()
        return True
    
    def print_stats(self):
        """打印当前统计信息"""
        logger.info(f"当前统计: 处理 {self.stats['processed_files']}/{self.stats['total_files']} 文件, "
                   f"添加 {self.stats['added_documents']} 个文档块, "
                   f"跳过 {self.stats['skipped_documents']} 个文档")
    
    def print_final_stats(self):
        """打印最终统计信息"""
        logger.info("=" * 50)
        logger.info("导入完成！最终统计:")
        logger.info(f"总文件数: {self.stats['total_files']}")
        logger.info(f"成功处理: {self.stats['processed_files']}")
        logger.info(f"处理失败: {self.stats['failed_files']}")
        logger.info(f"总文档数: {self.stats['total_documents']}")
        logger.info(f"新增文档块: {self.stats['added_documents']}")
        logger.info(f"跳过文档: {self.stats['skipped_documents']}")
        logger.info("=" * 50)
        
        # 显示知识库统计
        if self.rag_helper:
            try:
                db_stats = self.rag_helper.get_statistics()
                logger.info(f"知识库统计: {db_stats['total_documents']} 个文档, {db_stats['total_chunks']} 个块")
                logger.info(f"最新更新: {db_stats.get('last_updated', '未知')}")
            except Exception as e:
                logger.error(f"获取知识库统计失败: {e}")
    
    def export_import_log(self, filepath: str = None):
        """导出导入日志"""
        if filepath is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filepath = f"import_log_{timestamp}.json"
        
        log_data = {
            'import_time': datetime.now().isoformat(),
            'stats': self.stats,
            'cache_dir': self.cache_dir
        }
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, ensure_ascii=False, indent=2)
            logger.info(f"导入日志已保存到: {filepath}")
        except Exception as e:
            logger.error(f"保存导入日志失败: {e}")

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='导入搜索缓存到PostgreSQL知识库')
    parser.add_argument('--limit', type=int, help='限制处理的文件数量')
    parser.add_argument('--cache-dir', default='search_cache', help='缓存目录路径')
    parser.add_argument('--export-log', action='store_true', help='导出导入日志')
    
    args = parser.parse_args()
    
    # 创建日志目录
    os.makedirs("logs", exist_ok=True)
    
    logger.info("开始搜索缓存导入任务")
    
    # 创建导入器
    importer = SearchCacheImporter()
    if args.cache_dir != 'search_cache':
        importer.cache_dir = args.cache_dir
    
    # 执行导入
    success = importer.import_all_cache(limit=args.limit)
    
    # 导出日志
    if args.export_log:
        importer.export_import_log()
    
    if success:
        logger.info("导入任务完成")
        return 0
    else:
        logger.error("导入任务失败")
        return 1

if __name__ == "__main__":
    exit(main()) 