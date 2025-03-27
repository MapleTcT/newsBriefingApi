import schedule
import time
import logging
import threading
import asyncio
from bs4 import BeautifulSoup
import json

# 导入crawl4ai组件
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.content_filter_strategy import PruningContentFilter
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator

# 导入项目组件
from config import SCRAPE_INTERVAL_HOURS, POST_CRAWL_SELECTORS
import database
import nlp_processor

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def parse_content_with_bs(html_content, selectors):
    """使用BeautifulSoup从HTML内容中提取特定字段"""
    soup = BeautifulSoup(html_content, 'html.parser')
    data = {}
    try:
        title_element = soup.select_one(selectors['title'])
        data['title'] = title_element.get_text(strip=True) if title_element else None
    except Exception as e:
        logging.warning(f"无法使用选择器'{selectors['title']}'提取标题: {e}")
        data['title'] = None

    try:
        date_element = soup.select_one(selectors['date'])
        # 尝试获取文本或特定属性，比如'datetime'（如果可用）
        if date_element:
             data['publication_date'] = date_element.get('datetime') or date_element.get_text(strip=True)
        else:
             data['publication_date'] = None
    except Exception as e:
        logging.warning(f"无法使用选择器'{selectors['date']}'提取日期: {e}")
        data['publication_date'] = None

    # 如果需要净化内容，可以使用以下代码提取正文段落
    try:
        content_area = soup.select_one(selectors.get('content_placeholder', 'body'))
        if content_area:
             # 提取段落或相关文本
             paragraphs = content_area.find_all('p')
             data['cleaned_content'] = "\n".join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))
        else:
             data['cleaned_content'] = None
    except Exception as e:
         logging.warning(f"无法使用选择器'{selectors.get('content_placeholder')}'净化内容: {e}")
         data['cleaned_content'] = None

    return data

async def crawl_site(site_key, site_config):
    """为单个站点执行爬取操作"""
    logging.info(f"开始爬取站点: {site_key}")
    items_processed = 0
    items_added = 0
    items_skipped = 0
    
    browser_config = BrowserConfig(
        headless=True,
        verbose=False
    )
    
    run_config = CrawlerRunConfig(
        cache_mode=CacheMode.ENABLED,
        markdown_generator=DefaultMarkdownGenerator(
            content_filter=PruningContentFilter(threshold=0.45)
        ),
    )
    
    try:
        # 使用AsyncWebCrawler
        async with AsyncWebCrawler(config=browser_config) as crawler:
            # 深度爬取站点，并处理每个页面
            visited_urls = set()
            for start_url in site_config['start_urls']:
                # 为每个起始URL执行爬取
                result = await crawler.arun(
                    url=start_url,
                    config=run_config
                )
                
                # 处理当前页面
                url = start_url
                if not database.url_exists(url):
                    items_processed += 1
                    
                    # 从HTML中提取所需信息
                    html_content = result.html
                    parsed_data = parse_content_with_bs(html_content, site_config['selectors'])
                    
                    if parsed_data.get('title'):
                        # 使用crawl4ai提取的markdown内容进行NLP处理
                        text_for_nlp = result.markdown.raw_markdown or parsed_data.get('cleaned_content', html_content)
                        nlp_results = nlp_processor.process_text(text_for_nlp)
                        
                        # 准备数据库数据
                        db_data = {
                            'title': parsed_data['title'],
                            'source_url': url,
                            'publication_date': parsed_data.get('publication_date', 'N/A'),
                            'raw_content': html_content,
                            'summary': nlp_results['summary'],
                            'keywords': nlp_results['keywords'],
                            'source_site': site_key,
                            'category': nlp_results['category']
                        }
                        
                        # 添加到数据库
                        if database.add_briefing(db_data):
                            items_added += 1
                        else:
                            items_skipped += 1
                    else:
                        logging.warning(f"无法为{url}提取标题。跳过。")
                        items_skipped += 1
                else:
                    items_skipped += 1
                
                visited_urls.add(url)
                
                # 爬取页面中的链接
                # 注意：此处我们可以使用crawl4ai的deep crawl功能，但为了更好的控制，
                # 我们实现了一个简单的自定义链接爬取
                if 'links' in result.__dict__:
                    for link in result.links:
                        link_url = link.get('href')
                        if link_url and link_url not in visited_urls:
                            # 检查链接是否在允许的域内并匹配文章模式
                            is_allowed_domain = any(domain in link_url for domain in site_config['allowed_domains'])
                            pattern = site_config.get('article_url_pattern')
                            is_article = not pattern or pattern in link_url
                            
                            if is_allowed_domain and is_article:
                                # 爬取链接页面
                                link_result = await crawler.arun(
                                    url=link_url,
                                    config=run_config
                                )
                                
                                if not database.url_exists(link_url):
                                    items_processed += 1
                                    
                                    # 从HTML中提取所需信息
                                    link_html = link_result.html
                                    link_parsed_data = parse_content_with_bs(link_html, site_config['selectors'])
                                    
                                    if link_parsed_data.get('title'):
                                        # 使用crawl4ai提取的markdown内容进行NLP处理
                                        link_text_for_nlp = link_result.markdown.raw_markdown or link_parsed_data.get('cleaned_content', link_html)
                                        link_nlp_results = nlp_processor.process_text(link_text_for_nlp)
                                        
                                        # 准备数据库数据
                                        link_db_data = {
                                            'title': link_parsed_data['title'],
                                            'source_url': link_url,
                                            'publication_date': link_parsed_data.get('publication_date', 'N/A'),
                                            'raw_content': link_html,
                                            'summary': link_nlp_results['summary'],
                                            'keywords': link_nlp_results['keywords'],
                                            'source_site': site_key,
                                            'category': link_nlp_results['category']
                                        }
                                        
                                        # 添加到数据库
                                        if database.add_briefing(link_db_data):
                                            items_added += 1
                                        else:
                                            items_skipped += 1
                                    else:
                                        logging.warning(f"无法为{link_url}提取标题。跳过。")
                                        items_skipped += 1
                                else:
                                    items_skipped += 1
                                
                                visited_urls.add(link_url)
                                
                                # 限制每个起始URL抓取的链接数
                                if len(visited_urls) >= 10:  # 可在配置中设置
                                    break
        
        logging.info(f"站点{site_key}处理完成。处理：{items_processed}，添加：{items_added}，跳过：{items_skipped}")
        return items_processed, items_added, items_skipped
                
    except Exception as e:
        logging.error(f"站点{site_key}的爬取或处理过程中出错: {e}", exc_info=True)
        return items_processed, items_added, items_skipped

async def run_crawl_job_async():
    """异步执行爬取任务"""
    logging.info("开始crawl4ai爬取任务...")
    
    total_processed = 0
    total_added = 0
    total_skipped = 0
    
    # 对所有站点执行顺序爬取
    # 注意：可以使用asyncio.gather进行并行爬取，但可能导致资源过载
    for site_key, site_config in POST_CRAWL_SELECTORS.items():
        items_processed, items_added, items_skipped = await crawl_site(site_key, site_config)
        
        total_processed += items_processed
        total_added += items_added
        total_skipped += items_skipped
    
    logging.info(f"爬取任务完成。总计处理：{total_processed}，添加：{total_added}，跳过：{total_skipped}")

def run_crawl_job():
    """为配置的站点运行crawl4ai爬取过程"""
    try:
        # 使用asyncio.run运行异步任务
        asyncio.run(run_crawl_job_async())
    except Exception as e:
        logging.error(f"运行爬取任务时发生错误: {e}", exc_info=True)

def start_scheduler():
    """配置并启动调度器循环"""
    logging.info(f"安排每{SCRAPE_INTERVAL_HOURS}小时运行一次爬取任务。")
    schedule.every(SCRAPE_INTERVAL_HOURS).hours.do(run_crawl_job)

    logging.info("运行初始爬取任务...")
    run_crawl_job()  # 立即运行一次
    logging.info("初始爬取任务完成。")

    logging.info("启动调度器循环...")
    while True:
        schedule.run_pending()
        time.sleep(60)

def run_scheduler_in_thread():
    """在单独的线程中运行调度器"""
    scheduler_thread = threading.Thread(target=start_scheduler, daemon=True)
    scheduler_thread.start()
    logging.info("调度器在后台线程中启动。")
