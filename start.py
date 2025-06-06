#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速启动脚本
提供交互式界面来使用公司研报生成系统
"""

import os
import sys
import asyncio
from pathlib import Path

def print_banner():
    """打印系统横幅"""
    banner = """
╔══════════════════════════════════════════╗
║        公司研报生成系统 v1.0               ║
║    Company Research Report Generator      ║
╠══════════════════════════════════════════╣
║  AI驱动的智能化企业研究报告生成平台         ║
╚══════════════════════════════════════════╝
"""
    print(banner)

def check_environment():
    """检查运行环境"""
    print("🔧 检查运行环境...")
    
    # 检查Python版本
    if sys.version_info < (3, 9):
        print("❌ 需要Python 3.9+版本")
        return False
    
    # 检查必要文件
    required_files = [
        ".env.example",
        "requirements.txt",
        "main.py",
        "config/llm_config.py"
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ 缺少必要文件: {', '.join(missing_files)}")
        return False
    
    # 检查环境变量文件
    if not os.path.exists(".env"):
        print("⚠️ 未找到.env文件，请配置API密钥")
        print("   1. 复制 .env.example 为 .env")
        print("   2. 编辑 .env 文件，填入你的API密钥")
        return False
    
    print("✅ 环境检查通过")
    return True

def show_menu():
    """显示主菜单"""
    menu = """
🎯 请选择操作:

1. 生成单个公司研报
2. 批量生成研报
3. 运行系统测试  
4. 查看使用示例
5. 查看帮助文档
0. 退出系统

请输入选项编号: """
    return input(menu).strip()

async def generate_single_report():
    """生成单个公司研报"""
    print("\n📊 生成单个公司研报")
    print("=" * 30)
    
    company_name = input("请输入公司名称 (如: 平安银行): ").strip()
    if not company_name:
        print("❌ 公司名称不能为空")
        return
    
    stock_code = input("请输入股票代码 (可选, 如: 000001.SZ): ").strip()
    
    output_dir = input("请输入输出目录 (可选, 默认自动生成): ").strip()
    
    # 构建命令
    cmd_parts = ["python", "main.py", "--company", f'"{company_name}"']
    
    if stock_code:
        cmd_parts.extend(["--stock-code", stock_code])
    
    if output_dir:
        cmd_parts.extend(["--output-dir", f'"{output_dir}"'])
    
    cmd_parts.append("--verbose")
    
    command = " ".join(cmd_parts)
    print(f"\n🚀 执行命令: {command}")
    print("\n" + "=" * 50)
    
    # 执行命令
    os.system(command)

async def batch_generate_reports():
    """批量生成研报"""
    print("\n📊 批量生成研报")
    print("=" * 30)
    
    print("请输入公司列表 (每行一个，格式: 公司名称,股票代码)")
    print("例如:")
    print("平安银行,000001.SZ")
    print("招商银行,600036.SH")
    print("输入完成后按Enter，然后输入空行结束:")
    
    companies = []
    while True:
        line = input().strip()
        if not line:
            break
        
        parts = line.split(',')
        if len(parts) >= 1:
            company_name = parts[0].strip()
            stock_code = parts[1].strip() if len(parts) > 1 else ""
            companies.append((company_name, stock_code))
    
    if not companies:
        print("❌ 未输入有效的公司信息")
        return
    
    print(f"\n将生成 {len(companies)} 家公司的研报:")
    for i, (name, code) in enumerate(companies, 1):
        print(f"{i}. {name} ({code if code else '无股票代码'})")
    
    confirm = input("\n确认执行? (y/N): ").strip().lower()
    if confirm != 'y':
        print("❌ 已取消")
        return
    
    # 执行批量生成
    for company_name, stock_code in companies:
        cmd_parts = ["python", "main.py", "--company", f'"{company_name}"']
        if stock_code:
            cmd_parts.extend(["--stock-code", stock_code])
        
        command = " ".join(cmd_parts)
        print(f"\n🚀 正在生成 {company_name} 研报...")
        os.system(command)

def run_system_test():
    """运行系统测试"""
    print("\n🔧 运行系统测试")
    print("=" * 30)
    os.system("python test_system.py")

def show_examples():
    """显示使用示例"""
    print("\n📚 查看使用示例")
    print("=" * 30)
    os.system("python examples.py")

def show_help():
    """显示帮助文档"""
    print("\n📖 帮助文档")
    print("=" * 30)
    
    help_text = """
📋 使用指南:

1. 环境配置:
   - 复制 .env.example 为 .env
   - 编辑 .env 文件，配置API密钥
   - 安装依赖: pip install -r requirements.txt

2. 命令行使用:
   python main.py --company "公司名称"
   python main.py --company "平安银行" --stock-code "000001.SZ"

3. 配置文件:
   - 复制 config.yaml.example 为 config.yaml
   - 修改配置参数

4. 输出文件:
   - JSON格式: 结构化数据
   - Markdown格式: 可读性报告

5. 支持的功能:
   - 财务数据分析
   - 竞争对手分析  
   - 估值建模
   - 风险评估
   - 投资建议

📞 获取支持:
   - 查看 README.md 详细文档
   - GitHub Issues 反馈问题
   - 运行 test_system.py 诊断问题
"""
    print(help_text)

async def main():
    """主函数"""
    print_banner()
    
    if not check_environment():
        print("\n❌ 环境检查失败，请先完成环境配置")
        sys.exit(1)
    
    while True:
        try:
            choice = show_menu()
            
            if choice == '0':
                print("\n👋 感谢使用公司研报生成系统！")
                break
            elif choice == '1':
                await generate_single_report()
            elif choice == '2':
                await batch_generate_reports()
            elif choice == '3':
                run_system_test()
            elif choice == '4':
                show_examples()
            elif choice == '5':
                show_help()
            else:
                print("❌ 无效选项，请重新选择")
            
            input("\n按Enter键继续...")
            
        except KeyboardInterrupt:
            print("\n\n👋 程序已退出")
            break
        except Exception as e:
            print(f"\n❌ 发生错误: {e}")
            input("按Enter键继续...")

if __name__ == "__main__":
    asyncio.run(main())
