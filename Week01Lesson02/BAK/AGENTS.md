# AI 知识库助手项目 - Agent 架构文档

## 1. 项目概述
本项目是一个自动化 AI 知识库助手，能够从 GitHub Trending 和 Hacker News 等平台采集 AI/LLM/Agent 领域的技术动态，通过 AI 分析后结构化存储为 JSON 知识条目，并支持 Telegram、飞书等多渠道分发。

## 2. 技术栈
- Python 3.12
- OpenCode + 国产大模型（如 DeepSeek、GLM、Qwen 等）
- LangGraph（Agent 工作流编排）
- OpenClaw（数据采集与处理）
- 其他依赖：requests, BeautifulSoup4, pydantic, loguru 等

## 3. 编码规范
- 遵循 PEP 8 代码风格
- 变量与函数名使用 snake_case，类名使用 PascalCase
- 文档字符串使用 Google 风格
- 禁止使用裸 `print()`，统一使用日志库（loguru）
- 类型提示（type hints）强制使用
- 配置文件使用 YAML，环境变量使用 `.env` 文件

## 4. 项目结构
```
.opencode/
├── agents/           # Agent 定义文件
├── skills/           # 可复用的技能模块
knowledge/
├── raw/              # 原始采集数据
├── articles/         # 处理后的知识条目
config/               # 配置文件
scripts/              # 工具脚本
tests/                # 单元测试
```

## 5. 知识条目 JSON 格式
```json
{
  "id": "uuid_v4",
  "title": "文章标题",
  "source_url": "https://example.com/article",
  "source_type": "github_trending|hacker_news|blog",
  "content": "原始内容或摘要",
  "summary": "AI 生成的摘要",
  "tags": ["llm", "agent", "framework"],
  "status": "raw|processed|archived",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "metadata": {
    "author": "作者",
    "language": "en|zh",
    "read_time": 5,
    "score": 42
  }
}
```

## 6. Agent 角色概览

| 角色 | 职责 | 工具/技能 | 输出 |
|------|------|-----------|------|
| 采集 Agent | 从 GitHub Trending、Hacker News 等源抓取内容 | 网页爬虫、API 调用、RSS 解析 | 原始数据（raw） |
| 分析 Agent | 对原始内容进行摘要、分类、打标签 | LLM 调用、文本分析、实体识别 | 结构化知识条目 |
| 整理 Agent | 知识去重、质量过滤、存储管理 | 相似度计算、数据验证、数据库操作 | 最终知识库条目 |

## 7. 红线（绝对禁止的操作）
1. **禁止硬编码密钥**：任何 API 密钥、令牌等必须通过环境变量或配置中心管理
2. **禁止直接打印敏感信息**：日志中不得出现密码、令牌、个人数据
3. **禁止未经授权的数据采集**：遵守 robots.txt，尊重源站速率限制
4. **禁止忽略错误处理**：所有网络请求、文件操作必须有 try-catch 和重试机制
5. **禁止提交不完整的代码**：每次提交前必须通过代码检查（lint、type check）和单元测试
6. **禁止在生产环境使用调试日志**：DEBUG 级别日志仅限开发环境
7. **禁止直接修改知识库原始数据**：所有修改必须通过版本化管理（Git）

---

*最后更新：2026-04-18*