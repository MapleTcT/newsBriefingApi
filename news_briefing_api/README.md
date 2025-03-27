# 行业信息简报API

行业信息简报API是一个自动化爬取、处理和提供行业相关信息简报的服务。系统专注于健康糖、小麦产业链、玉米产业链和合成生物领域的最新资讯，使用先进的网页爬虫和自然语言处理技术，定期从权威来源获取信息，自动生成简报并通过API提供。

## 功能特点

- **多源数据采集**：从政府机构、行业协会、专业媒体等权威来源自动爬取信息
- **智能内容处理**：使用NLP技术自动提取摘要和关键词
- **自动内容分类**：基于领域关键词自动对内容进行分类归档
- **定时更新**：系统定期运行爬虫（默认为每8小时一次），确保信息的时效性
- **简易API访问**：通过RESTful API轻松获取最新简报和历史数据
- **关键词搜索**：支持按关键词和类别筛选简报内容

## 技术架构

- **爬虫引擎**：基于crawl4ai实现高效网页爬取
- **内容提取**：使用BeautifulSoup进行HTML解析和内容提取
- **文本处理**：使用sumy进行文本摘要，yake进行关键词提取
- **数据存储**：SQLite数据库保存所有简报内容
- **API服务**：基于Flask构建RESTful API
- **定时调度**：使用schedule实现定时任务

## 安装指南

### 环境要求

- Python 3.8或更高版本
- pip包管理工具

### 安装步骤

1. 克隆仓库：

```bash
git clone https://github.com/yourusername/news_briefing_api.git
cd news_briefing_api
```

2. 安装依赖：

```bash
pip install -r requirements.txt
```

3. 运行crawl4ai设置：

```bash
crawl4ai-setup
crawl4ai-doctor
```

## 使用方法

### 启动服务

```bash
python main.py
```

启动后，服务将：
- 初始化数据库
- 立即执行第一次爬取任务
- 设置定时爬取计划（每8小时一次）
- 启动API服务（默认端口5000）

### API端点

1. **获取最新简报**：
   - URL: `/api/latest_briefing`
   - 方法: GET
   - 参数: 
     - `keyword` (可选)：按关键词筛选
     - `category` (可选)：按类别筛选
   - 示例: `http://localhost:5000/api/latest_briefing?keyword=发酵&category=合成生物学`

2. **获取多个简报**：
   - URL: `/api/briefings`
   - 方法: GET
   - 参数: 
     - `limit` (可选)：返回数量，默认10条，最大50条
     - `keyword` (可选)：按关键词筛选
     - `category` (可选)：按类别筛选
   - 示例: `http://localhost:5000/api/briefings?limit=5&category=健康糖`

3. **获取所有类别**：
   - URL: `/api/categories`
   - 方法: GET
   - 示例: `http://localhost:5000/api/categories`

## 配置说明

主要配置选项位于`config.py`文件中：

- `DB_NAME`：数据库文件名
- `POST_CRAWL_SELECTORS`：爬取目标网站配置
- `SUMMARY_SENTENCE_COUNT`：摘要句子数量
- `KEYWORD_COUNT`：提取关键词数量
- `SCRAPE_INTERVAL_HOURS`：爬取间隔时间（小时）
- `DOMAIN_KEYWORDS`：领域关键词设置

## 自定义爬取目标

要添加新的爬取目标，请在`config.py`的`POST_CRAWL_SELECTORS`中添加新条目，格式如下：

```python
"site_key": {
    "allowed_domains": ["example.com"],
    "start_urls": ["https://www.example.com/news/"],
    "article_url_pattern": "/article/",
    "selectors": {
        "title": "h1.title",
        "date": "div.date",
        "content_placeholder": "div.content"
    },
    "notes": "站点说明"
}
```

**注意**：请确保使用浏览器开发者工具(F12)验证选择器的准确性。

## 定制和扩展

项目模块化设计便于定制和扩展：

- `database.py`：修改存储逻辑或数据结构
- `nlp_processor.py`：定制NLP处理方法或集成其他AI模型
- `scheduler.py`：调整爬取策略或添加更多处理步骤
- `api.py`：扩展API功能或添加新端点

## 贡献指南

欢迎贡献代码、报告问题或提出改进建议。请遵循以下步骤：

1. Fork本仓库
2. 创建您的特性分支 (`git checkout -b feature/your-feature`)
3. 提交您的改动 (`git commit -m 'Add some feature'`)
4. 推送到分支 (`git push origin feature/your-feature`)
5. 创建新的Pull Request

## 许可证

本项目采用MIT许可证 - 详见LICENSE文件 