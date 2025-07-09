#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
列出可用的 Qwen 嵌入模型
"""

def list_qwen_models():
    """列出可用的 Qwen 嵌入模型"""
    print("可用的 Qwen 嵌入模型:")
    print()
    
    models = [
        "Qwen/Qwen-Embedding",
        "Qwen/Qwen-Embedding-4B", 
        "Qwen/Qwen-Embedding-2B",
        "Qwen/Qwen-Embedding-1B",
        "Qwen/Qwen-Embedding-512B",
        "Qwen/Qwen-Embedding-256B",
        "Qwen/Qwen-Embedding-128B",
        "Qwen/Qwen-Embedding-64B",
        "Qwen/Qwen-Embedding-32B",
        "Qwen/Qwen-Embedding-16B",
        "Qwen/Qwen-Embedding-8B",
        "Qwen/Qwen-Embedding-4B",
        "Qwen/Qwen-Embedding-2B",
        "Qwen/Qwen-Embedding-1B",
        "Qwen/Qwen-Embedding-512M",
        "Qwen/Qwen-Embedding-256M",
        "Qwen/Qwen-Embedding-128M",
        "Qwen/Qwen-Embedding-64M",
        "Qwen/Qwen-Embedding-32M",
        "Qwen/Qwen-Embedding-16M",
        "Qwen/Qwen-Embedding-8M",
        "Qwen/Qwen-Embedding-4M",
        "Qwen/Qwen-Embedding-2M",
        "Qwen/Qwen-Embedding-1M",
    ]
    
    print("建议尝试的模型（按大小排序）:")
    for model in models:
        print(f"  - {model}")
    
    print()
    print("或者使用通用的嵌入模型:")
    print("  - all-MiniLM-L6-v2 (384维)")
    print("  - all-mpnet-base-v2 (768维)")
    print("  - text-embedding-ada-002 (1536维)")

if __name__ == "__main__":
    list_qwen_models() 