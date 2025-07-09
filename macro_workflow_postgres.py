import os
import time
import yaml
import openai
from duckduckgo_search import DDGS
from pocketflow import Node, Flow
from dotenv import load_dotenv
from data_analysis_agent.utils.llm_helper import LLMHelper
from data_analysis_agent.config.llm_config import LLMConfig

from utils.markdown_tools import format_markdown
from utils.search_engine import SearchEngine
from utils.rag_postgres import RAGPostgresHelper
from config.database_config import db_config
import logging

logger = logging.getLogger('MacroResearchPostgres')

# 加载环境变量
load_dotenv()

# 从环境变量中初始化 OpenAI API 密钥
openai.api_key = os.getenv("OPENAI_API_KEY")
openai.api_base = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")

# 初始化 LLMHelper 实例（全局唯一）
llm = LLMHelper(
    LLMConfig(
        api_key=os.environ.get("OPENAI_API_KEY"),
        base_url=os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1"),
        model=os.environ.get("OPENAI_MODEL", "gpt-4")
    )
)

# 初始化 PostgreSQL RAG 助手（全局唯一）
try:
    print('当前RAG配置:', db_config.get_rag_config())  # 调试用，打印当前RAG配置
    rag_helper = RAGPostgresHelper(
        db_config=db_config.get_postgres_config(),
        rag_config=db_config.get_rag_config()
    )
    logger.info("PostgreSQL RAG助手初始化成功")
except Exception as e:
    logger.error(f"PostgreSQL RAG助手初始化失败: {e}")
    logger.info("将使用内存RAG助手作为备选方案")
    from utils.rag_helper import RAGHelper
    rag_helper = RAGHelper()

class IndustryResearchFlow(Node):  # 研报生成的决策节点
    def prep(self, shared):
        context = shared.get("context", [])
        context_str = yaml.dump(context, allow_unicode=True)
        industry = shared["industry"]  # 行业名称
        focus_areas = shared.get("focus_areas", [])
        generated_sections = shared.get("generated_sections", [])
        generated_names = [section.get('name', '') for section in generated_sections]
        # 动态维护目标章节清单
        target_sections = shared.get('target_sections', [])
        return industry, context_str, focus_areas, generated_names, target_sections

    def exec(self, inputs):
        industry, context, focus_areas, generated_names, target_sections = inputs
        print(f"\n正在分析{industry}研究进度...")
        
        # 使用RAG获取相关背景信息
        rag_context = rag_helper.get_context_for_llm(
            f"宏观经济研究 {industry} {', '.join(focus_areas)}"
        )
        
        # 检查数据库中是否有足够的相关信息
        # 先尝试从数据库获取相关上下文
        relevant_context = rag_helper.get_context_for_llm(
            f"宏观经济研究 {industry} {', '.join(focus_areas)}",
            max_tokens=2000  # 限制token数量来评估信息丰富度
        )
        
        # 基于相关上下文的长度来判断信息是否充足
        context_length = len(relevant_context)
        has_sufficient_data = context_length > 500  # 如果相关上下文超过500字符，认为有足够数据
        
        if not has_sufficient_data:
            print(f"数据库相关信息不足（相关上下文长度: {context_length}字符），建议先搜索更多信息")
        else:
            print(f"数据库中有充足的相关信息（相关上下文长度: {context_length}字符），可以基于现有信息进行分析")
        
        while True:
            prompt = f"""
针对宏观经济研究，基于已有信息：{context}

【RAG增强背景信息】：
{rag_context}

【数据库信息评估】：
- 相关信息充足度：{'充足' if has_sufficient_data else '不足'}
- 相关上下文长度：{context_length}字符
- 建议：{'可以基于现有信息进行分析' if has_sufficient_data else '需要搜索更多相关信息'}

关注指标：{', '.join(focus_areas)}

【已生成章节（严禁重复！）】：
{generated_names}

【极其重要的警告】：
- 下方列表中的章节已生成，**严禁**在YAML输出中再次出现这些章节名！
- 如果输出了已生成章节，系统会自动忽略并要求你重新决策，请务必只输出未生成章节。
- YAML输出时，section.name字段必须是未生成章节，否则无效。

请分析并判断下一步行动：
1) search - 搜索更多信息（当缺少关键数据或背景信息时）
2) generate - 开始生成某个章节内容（当有足够信息且章节未生成时）
3) complete - 完成研报生成（当所有必要章节都已生成时）

要特别关注：
- 核心经济指标数据（GDP、CPI、利率、汇率）的最新数据和趋势
- 重要政策文件与解读（如货币政策、财政政策等）
- 区域经济对比数据与分析
- 全球经济形势与联动影响
- 潜在风险因素与预警信号

请以 YAML 格式输出：
```yaml
action: search/generate/complete  # search表示继续搜索，generate表示生成章节，complete表示完成
reason: 做出此判断的原因，**并自查你输出的章节名是否在已生成章节列表中，确认没有重复**
search_terms: # 如果是search，列出要搜索的关键词列表
  - 关键词1 
  - 关键词2
section: # 如果是generate，指定要生成的章节名称（必须是未生成的章节，否则无效）
  name: 章节名称 # 如：宏观经济概况/政策解读/风险分析等
  focus: 重点关注内容 # 具体要分析的要点
```"""
            resp = llm.call(prompt)
            yaml_str = resp.split("```yaml")[1].split("```", 1)[0].strip()
            result = yaml.safe_load(yaml_str)
            # 动态维护目标章节清单
            if result['action'] == 'generate':
                section = result.get('section', {})
                if isinstance(section, dict) and 'name' in section:
                    if 'target_sections' not in locals():
                        target_sections = []
                    if section['name'] not in target_sections:
                        target_sections.append(section['name'])
                    # 检查是否已生成
                    if section['name'] in generated_names:
                        print(f"章节 {section['name']} 已生成，跳过，重新决策...")
                        # 重新决策，继续while循环
                        continue
            break
        # 打印决策结果
        print(f"决策结果: {result['action']}")
        print(f"决策原因: {result['reason']}")
        if result['action'] == 'search':
            print("需要搜索的关键词:", result['search_terms'])
        elif result['action'] == 'generate':
            print(f"即将生成章节: {result['section']['name']}")
        # 更新shared的target_sections
        shared = self.shared if hasattr(self, 'shared') else None
        if shared is not None:
            shared['target_sections'] = target_sections
        return result

    def post(self, shared, prep_res, exec_res):
        action = exec_res.get("action")
        # 取已生成章节
        generated_names = [s.get('name', '') for s in shared.get("generated_sections", [])]
        # 取目标章节
        target_sections = shared.get('target_sections', [])
        # 判断是否全部完成
        if target_sections and set(target_sections).issubset(set(generated_names)):
            print("所有目标章节都已生成，流程结束")
            return "complete"
        if action == "search":
            shared["search_terms"] = exec_res.get("search_terms", [])
            print("\n=== 开始信息搜索阶段 ===")
        elif action == "generate":
            section = exec_res.get("section", {})
            if isinstance(section, dict) and 'name' in section:
                if section['name'] in generated_names:
                    print(f"章节 {section['name']} 已生成，跳过")
                    return "continue"
                shared["current_section"] = section
                print("\n=== 开始章节生成阶段 ===")
            else:
                print(f"章节信息格式错误: {section}")
                return "complete"
        elif action == "complete":
            print("\n=== 开始完成研报阶段 ===")
        return action

class SearchInfo(Node):  # 信息搜索节点
    def prep(self, shared):
        return shared.get("search_terms", [])

    def exec(self, search_terms):
        all_results = []
        total = len(search_terms)
        for i, term in enumerate(search_terms, 1):
            print(f"\n搜索关键词 ({i}/{total}): {term}")
            results = search_web(term)
            print(f"找到 {len(list(results))} 条相关信息")
            all_results.append({"term": term, "results": results})
            time.sleep(5)  # 避免请求过快
        return all_results

    def post(self, shared, prep_res, exec_res):
        context_list = shared.get("context", [])
        context_list.extend(exec_res)
        shared["context"] = context_list
        
        # 将搜索结果添加到PostgreSQL RAG知识库
        total_added = 0
        for search_item in exec_res:
            search_term = search_item.get("term", "")
            results = search_item.get("results", [])
            if results:
                added_count = rag_helper.add_search_results(results, search_term)
                total_added += added_count
        
        print(f"\n信息搜索完成，返回决策节点...")
        print(f"PostgreSQL RAG知识库新增 {total_added} 个文档块")
        
        # 显示知识库统计
        stats = rag_helper.get_statistics()
        print(f"知识库统计: {stats['total_documents']} 个文档, {stats['total_chunks']} 个块")
        
        return "search_done"

class GenerateSection(Node):  # 章节生成节点
    def prep(self, shared):
        return (
            shared.get("industry"),
            shared.get("current_section", {}),
            shared.get("context", []),
            shared.get("focus_areas", [])
        )

    def exec(self, inputs):
        industry, section, context, focus_areas = inputs
        print(f"\n开始生成 {section['name']} 章节...")
        context_str = yaml.dump(context, allow_unicode=True)
        
        # 使用RAG获取相关背景信息
        rag_context = rag_helper.get_context_for_llm(
            f"{section['name']} {section['focus']} {industry} {', '.join(focus_areas)}"
        )
        
        prompt = f"""
研究主题：{industry}
章节名称：{section['name']}
重点关注：{section['focus']}
核心指标：{', '.join(focus_areas)}

【RAG增强背景信息】：
{rag_context}

【原始参考资料】：
{context_str}

请生成一个专业、详实的宏观经济研报章节。要求：
1. 数据支撑充分
   - 提供最新的经济指标数据
   - 使用权威来源的统计数据
   - 展示关键数据的历史趋势

2. 逻辑严谨
   - 建立清晰的因果关系
   - 解释政策传导机制
   - 分析各指标间的相互影响

3. 分析深入
   - 挖掘数据背后的原因
   - 评估政策效果
   - 预测未来趋势

4. 结构清晰
   - 层次分明
   - 重点突出
   - 观点明确

5. 专业视角
   - 使用专业术语
   - 多维度分析
   - 提供具体建议

如果涉及风险分析，请特别关注：
- 潜在的系统性风险
- 外部冲击因素
- 政策调整风险
- 区域性风险
- 具体防范建议
"""
        content = llm.call(prompt)
        print(f"章节 {section['name']} 生成完成!")
        print(f"内容长度: {len(content)} 字符")
        print(f"内容预览: {content[:100]}...")
        return {
            "name": section["name"],
            "content": content
        }
        

    def post(self, shared, prep_res, exec_res):
        sections = shared.get("generated_sections", [])
        sections.append(exec_res)
        shared["generated_sections"] = sections
        print("\n返回决策节点，继续分析下一步...")
        return "continue"

class CompleteReport(Node):  # 研报完成节点
    def prep(self, shared):
        return (
            shared.get("industry"),
            shared.get("generated_sections", [])
        )

    def exec(self, inputs):
        industry, sections = inputs
        print(f"\n=== 开始整合最终研报 ===")
        # 整合所有章节内容
        content = f"# {industry}行业研究报告\n\n"
        for section in sections:
            print(f"添加章节: {section['name']}")
            content += f"\n## {section['name']}\n\n{section['content']}\n"
        return content

    def post(self, shared, prep_res, exec_res):
        print(f"\n=== 研报生成完成！===")
        print(f"研报已保存到 '研报_postgres.md' 文件中")
        
        # 显示最终的知识库统计
        stats = rag_helper.get_statistics()
        print(f"最终知识库统计: {stats['total_documents']} 个文档, {stats['total_chunks']} 个块")
        print(f"最新更新时间: {stats.get('last_updated', '未知')}")
        
        shared["report"] = exec_res
        return None

def search_web(term: str):
    # with DDGS() as ddgs:
    #     results = ddgs.text(keywords=term, region="cn-zh", max_results=20)
    multi_engine = SearchEngine()
    results = multi_engine.search(term, max_results=10)
    return results

"""
示例用法
"""
if __name__ == "__main__":
    # 显示配置信息
    print("=== PostgreSQL RAG配置 ===")
    db_config.print_config()
    print()
    
    # 构建工作流
    research = IndustryResearchFlow()
    search = SearchInfo()
    generate = GenerateSection()
    complete = CompleteReport()
    
    # 设置转换关系
    research - "search" >> search
    research - "generate" >> generate
    research - "complete" >> complete
    search - "search_done" >> research
    generate - "continue" >> research
    
    # 运行工作流
    flow = Flow(start=research)
    shared_state = {
        "industry": "生成式AI基建与算力投资趋势（2023-2026）",
        "focus_areas": ["GDP", "CPI", "利率", "汇率"],
        "analysis_type": "macro_economic"
    }
    result = flow.run(shared_state)
    
    output_filename = "研报_postgres.md"
    # 保存结果
    if result:
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write(result)

    format_markdown(output_filename, "Macro_Research_Report_Postgres.docx")
    logger.info(f"研报已转换为docx格式") 