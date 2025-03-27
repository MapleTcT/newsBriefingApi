# 行业信息简报API

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

自动爬取、处理和提供行业相关信息简报的服务API。专注于健康糖、小麦产业链、玉米产业链和合成生物领域的最新资讯，使用先进的网页爬虫和自然语言处理技术生成信息简报。

## 项目特点

- **多源数据采集**：从政府机构、行业协会、专业媒体等获取信息
- **智能内容处理**：自动提取摘要和关键词
- **自动内容分类**：按领域自动分类
- **定时更新**：定期爬取最新信息
- **简易API访问**：通过RESTful API获取简报
- **关键词搜索**：按关键词和类别筛选

## 快速开始

```bash
# 安装依赖
pip install -r news_briefing_api/requirements.txt

# 安装crawl4ai浏览器
crawl4ai-setup
crawl4ai-doctor

# 运行服务
cd news_briefing_api
python main.py
```

## 详细文档

完整使用文档请参见 [news_briefing_api/README.md](news_briefing_api/README.md)。

## 技术架构

- **爬虫引擎**：crawl4ai
- **内容提取**：BeautifulSoup
- **文本处理**：sumy、yake
- **数据存储**：SQLite
- **API服务**：Flask
- **定时调度**：schedule

## 许可证

本项目采用MIT许可证 - 详见[LICENSE](news_briefing_api/LICENSE)文件。 