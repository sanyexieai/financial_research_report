# 公司研报生成系统

一个基于 AI 的综合性公司研报自动生成系统，支持财务数据提取、竞争分析、估值建模、风险评估等全方位企业研究功能。

## 🚀 功能特性

### 📊 财务数据分析
- **三大财务报表**：自动获取资产负债表、利润表、现金流量表
- **财务比率计算**：ROE分解、盈利能力、偿债能力、营运能力分析
- **现金流匹配**：经营现金流与净利润匹配分析
- **增长性分析**：营收、利润、资产增长率计算

### 🏢 企业基本面研究
- **主营业务分析**：业务结构、收入构成、核心竞争力
- **行业地位评估**：市场份额、竞争优势、行业排名
- **治理结构评价**：股权结构、管理层背景、公司治理

### 🔍 竞争分析
- **竞争对手识别**：AI智能识别同行业竞争企业
- **横向对比分析**：财务指标、业务模式、市场表现对比
- **竞争优劣势**：SWOT分析、竞争护城河评估

### 💰 估值建模
- **PE估值模型**：基于行业PE倍数的相对估值
- **DCF估值模型**：现金流折现绝对估值
- **情景分析**：多种假设条件下的估值敏感性分析
- **目标价格预测**：综合估值方法给出价格区间

### ⚠️ 风险评估
- **财务风险**：偿债能力、盈利稳定性、现金流风险
- **经营风险**：业务模式、市场环境、竞争风险
- **治理风险**：管理层稳定性、内控制度、信息披露
- **市场风险**：系统性风险、流动性风险
- **政策风险**：行业政策、监管变化影响

### 📈 投资建议
- **评级体系**：买入/增持/中性/减持/卖出五级评级
- **目标价格**：12个月目标价格预测
- **投资逻辑**：核心投资要点和风险提示
- **配置建议**：适合的投资者类型和配置比例

## 🛠️ 技术架构

```
company_research_report/
├── config/                 # 配置模块
│   ├── __init__.py
│   └── llm_config.py      # LLM配置管理
├── data_collectors/        # 数据收集模块
│   ├── __init__.py
│   ├── financial_data_collector.py    # 财务数据收集
│   ├── business_info_collector.py     # 企业信息收集
│   └── competitor_analyzer.py         # 竞争对手分析
├── analyzers/             # 分析模块
│   ├── __init__.py
│   ├── financial_ratio_analyzer.py    # 财务比率分析
│   ├── valuation_analyzer.py          # 估值分析
│   └── risk_analyzer.py               # 风险分析
├── core/                  # 核心模块
│   ├── __init__.py
│   └── research_report_generator.py   # 报告生成器
├── utils/                 # 工具模块
│   ├── __init__.py
│   ├── llm_helper.py                  # LLM调用辅助
│   ├── code_executor.py               # 代码执行器
│   └── fallback_openai_client.py      # 容错API客户端
├── main.py               # 主入口脚本
├── requirements.txt      # 依赖文件
├── .env.example         # 环境变量示例
└── README.md           # 说明文档
```

## 📦 安装部署

### 1. 环境要求
- Python 3.9+
- OpenAI API Key 或兼容的 API 服务

### 2. 安装依赖
```bash
# 克隆或下载项目
cd company_research_report

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置环境变量
```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，填入你的 API 密钥
nano .env
```

环境变量说明：
```bash
# 火山引擎配置
OPENAI_API_KEY=
OPENAI_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
# 文本模型
OPENAI_MODEL=deepseek-v3-250324
# OPENAI_MODEL=deepseek-r1-250528
```

## 🚀 快速开始

### 基本用法
```bash
# 生成平安银行的研报
python main.py --company "平安银行"

# 指定股票代码
python main.py --company "平安银行" --stock-code "000001.SZ"

# 自定义输出目录
python main.py --company "平安银行" --output-dir "./my_reports"

# 使用自定义配置文件
python main.py --company "平安银行" --config "./my_config.yaml"

# 显示详细输出
python main.py --company "平安银行" --verbose
```

### 编程接口使用
```python
import asyncio
from config.llm_config import LLMConfig
from core.research_report_generator import ResearchReportGenerator

async def generate_report_example():
    # 初始化配置
    config = LLMConfig()
    
    # 创建研报生成器
    generator = ResearchReportGenerator(config)
    
    # 生成研报
    result = await generator.generate_report(
        company_name="平安银行",
        stock_code="000001.SZ",
        output_dir="./reports"
    )
    
    if result['success']:
        print(f"研报生成成功: {result['markdown_file']}")
    else:
        print(f"生成失败: {result['error']}")

# 运行示例
asyncio.run(generate_report_example())
```

## 📋 输出格式

系统会生成两种格式的研报：

### 1. JSON 格式 (结构化数据)
```json
{
  "company_info": {
    "company_name": "平安银行股份有限公司",
    "stock_code": "000001.SZ",
    "main_business": "商业银行业务",
    "industry": "银行业",
    "market_cap": 1000000000
  },
  "financial_analysis": {
    "financial_statements": {...},
    "financial_ratios": {...},
    "growth_analysis": {...}
  },
  "competitor_analysis": {...},
  "valuation_analysis": {...},
  "risk_analysis": {...},
  "investment_recommendation": {
    "rating": "买入",
    "target_price": 15.50,
    "reasoning": "..."
  }
}
```

### 2. Markdown 格式 (可读性报告)
标准的研报格式，包含：
- 执行摘要
- 公司概况
- 财务分析
- 竞争分析
- 估值分析
- 风险评估
- 投资建议

## 🔧 高级配置

### 自定义配置文件
创建 `config.yaml` 文件：
```yaml
llm:
  api_key: "your_api_key"
  base_url: "https://api.openai.com/v1"
  model: "gpt-4"
  max_tokens: 4000
  temperature: 0.7

analysis:
  valuation_methods: ["PE", "DCF"]
  scenario_analysis: true
  peer_comparison: true
  
output:
  include_charts: true
  detailed_analysis: true
```

### 扩展开发
系统采用模块化设计，可以轻松扩展：

1. **添加新的数据源**：在 `data_collectors/` 中实现新的收集器
2. **扩展分析方法**：在 `analyzers/` 中添加新的分析器
3. **自定义输出格式**：修改 `core/research_report_generator.py`

## 📊 支持的数据源

- **akshare**：A股财务数据、基本面信息
- **公开财报**：上市公司定期报告
- **AI分析**：基于LLM的文本分析和行业洞察

## ⚠️ 注意事项

1. **数据准确性**：系统依赖公开数据源，请验证关键财务数据
2. **API配额**：注意LLM API的调用频率和配额限制
3. **投资风险**：本系统仅供研究参考，投资决策请谨慎
4. **实时性**：部分数据可能存在延迟，建议结合最新公告

## 🤝 贡献指南

欢迎提交Issue和Pull Request来改进系统：

1. Fork 本项目
2. 创建特性分支
3. 提交更改
4. 发起 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 📞 联系支持

如有问题或建议，请通过以下方式联系：
- 提交 GitHub Issue
- 发送邮件至项目维护者

---

**免责声明**：本系统生成的研报仅供学习和研究使用，不构成投资建议。投资有风险，决策需谨慎。
"# company_research_report" 
