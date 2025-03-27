import os
from dotenv import load_dotenv

load_dotenv()

DB_NAME = "briefings.db"

# --- 爬取目标网站配置 ---
POST_CRAWL_SELECTORS = {
    # === 政府/监管 (高权威) ===
    "moa_china": {
        "allowed_domains": ["moa.gov.cn"],
        "start_urls": ["http://www.moa.gov.cn/xw/"],  # 新闻中心
        "article_url_pattern": ".html",  # 常见政府网站文章URL模式
        "selectors": {
            "title": "h1.arc_title",  # 需根据实际网站结构调整
            "date": "span.pub_time",  # 需根据实际网站结构调整
            "content_placeholder": "div.arc_body"  # 需根据实际网站结构调整
        },
        "notes": "中文网站，确保UTF-8编码处理。"
    },
    "nhc_china": {
        "allowed_domains": ["nhc.gov.cn"],
        "start_urls": [
            "http://www.nhc.gov.cn/xwzb/xwzblist.shtml",  # 新闻列表
        ],
        "article_url_pattern": ".shtml",
        "selectors": {
            "title": "div.tit",  # 需根据实际网站结构调整
            "date": "div.source > span.time",  # 需根据实际网站结构调整
            "content_placeholder": "div#xw_box"  # 需根据实际网站结构调整
        },
        "notes": "中文网站，标准可能是PDF格式需要特殊处理。"
    },
    "fda_news": {
        "allowed_domains": ["fda.gov"],
        "start_urls": ["https://www.fda.gov/news-events/fda-newsroom/press-announcements"],
        "article_url_pattern": "/news-events/press-announcements/",
        "selectors": {
            "title": "h1#page-title",  # 需根据实际网站结构调整
            "date": "div.field--name-field-published-date > time",  # 需根据实际网站结构调整
            "content_placeholder": "article div.field--type-text-with-summary"  # 需根据实际网站结构调整
        },
        "notes": "重点关注新闻发布。"
    },
    "usda_news": {
        "allowed_domains": ["usda.gov"],
        "start_urls": ["https://www.usda.gov/media/press-releases"],
        "article_url_pattern": "/media/press-releases",
        "selectors": {
            "title": "h1.page-title",  # 需根据实际网站结构调整
            "date": "p.usda-page-meta__date",  # 需根据实际网站结构调整
            "content_placeholder": "div.usda-prose"  # 需根据实际网站结构调整
        },
        "notes": "美国农业部新闻。"
    },
    "efsa_news": {
        "allowed_domains": ["efsa.europa.eu"],
        "start_urls": ["https://www.efsa.europa.eu/en/news"],
        "article_url_pattern": "/news/",
        "selectors": {
            "title": "h1",  # 需根据实际网站结构调整
            "date": "div.date-display-single",  # 需根据实际网站结构调整
            "content_placeholder": "div.field--name-field-text-content"  # 需根据实际网站结构调整
        },
        "notes": "欧洲食品安全局新闻。"
    },
    "fao_news": {
        "allowed_domains": ["fao.org"],
        "start_urls": ["https://www.fao.org/newsroom/en/"],
        "article_url_pattern": "/newsroom/",
        "selectors": {
            "title": "h1.title",  # 需根据实际网站结构调整
            "date": "div.date-and-share span.date",  # 需根据实际网站结构调整
            "content_placeholder": "div.body-content"  # 需根据实际网站结构调整
        },
        "notes": "联合国粮农组织新闻。"
    },

    # === 行业新闻 (时效性高) ===
    "foodnavigator-usa": {
        "allowed_domains": ["foodnavigator-usa.com"],
        "start_urls": [
            "https://www.foodnavigator-usa.com/News/Ingredients",
            "https://www.foodnavigator-usa.com/News/Processing-Packaging"
        ],
        "article_url_pattern": "/Article/",
        "selectors": {
            "title": "h1.detail-title",
            "date": "time.detail-time",
            "content_placeholder": "div.detail-content"
        },
        "notes": "可能有付费墙/注册要求。"
    },
    "food_dive": {
        "allowed_domains": ["fooddive.com"],
        "start_urls": [
            "https://www.fooddive.com/topic/manufacturing/",
            "https://www.fooddive.com/topic/ingredients/"
        ],
        "article_url_pattern": "/news/",
        "selectors": {
            "title": "h1",  # 需根据实际网站结构调整
            "date": "div[class*='published-date']",  # 需根据实际网站结构调整
            "content_placeholder": "div.article-body"  # 需根据实际网站结构调整
        },
        "notes": "检查动态加载或内容限制。"
    },
    "gen_news": {
        "allowed_domains": ["genengnews.com"],
        "start_urls": ["https://www.genengnews.com/news/"],
        "article_url_pattern": None,  # 依靠域名和深度限制
        "selectors": {
            "title": "h1.entry-title",
            "date": "time.entry-date",
            "content_placeholder": "div.entry-content"
        },
        "notes": "生物技术新闻。"
    },
    "foodmate_news": {
        "allowed_domains": ["news.foodmate.net", "www.foodmate.net"],
        "start_urls": ["http://news.foodmate.net/"],
        "article_url_pattern": "show",
        "selectors": {
            "title": "div.l_con > h1",  # 需根据实际网站结构调整
            "date": "div.l_tit > span:nth-of-type(1)",  # 需根据实际网站结构调整
            "content_placeholder": "div.l_text"  # 需根据实际网站结构调整
        },
        "notes": "中文食品行业网站。"
    },

    # === 行业协会 (权威性中高) ===
    "cbia_china": {
        "allowed_domains": ["cobia.org.cn"],
        "start_urls": [
            "http://www.cobia.org.cn/infor/zx.html",  # 协会资讯
            "http://www.cobia.org.cn/infor/hy.html"   # 行业资讯
        ],
        "article_url_pattern": "/infor/",
        "selectors": {
            "title": "div.show_title",  # 需根据实际网站结构调整
            "date": "div.show_time",  # 需根据实际网站结构调整
            "content_placeholder": "div.show_con"  # 需根据实际网站结构调整
        },
        "notes": "中国生物发酵产业协会。"
    },
    "corn_refiners": {
        "allowed_domains": ["corn.org"],
        "start_urls": ["https://corn.org/news-statements/"],
        "article_url_pattern": "/news-statements/",
        "selectors": {
            "title": "h1.entry-title",  # 需根据实际网站结构调整
            "date": "p.blog-date",  # 需根据实际网站结构调整
            "content_placeholder": "div.entry-content"  # 需根据实际网站结构调整
        },
        "notes": "玉米精炼行业协会。"
    },
    "bio_org": {
        "allowed_domains": ["bio.org"],
        "start_urls": [
            "https://www.bio.org/press-releases",
            "https://www.bio.org/blogs"
        ],
        "article_url_pattern": "/press-release/",  # 或 /blogs/ 对于博客文章
        "selectors": {
            "title": "h1#page-title",  # 需根据实际网站结构调整
            "date": "p.submitted > em",  # 需根据实际网站结构调整
            "content_placeholder": "div.content > div.field-items"  # 需根据实际网站结构调整
        },
        "notes": "生物技术创新组织。"
    }
}

# --- NLP设置 ---
SUMMARY_SENTENCE_COUNT = 5  # 摘要句子数量
KEYWORD_COUNT = 10          # 提取关键词数量

# --- 调度器设置 ---
SCRAPE_INTERVAL_HOURS = 8   # 每8小时爬取一次（每天3次）

# --- 领域关键词 ---
DOMAIN_KEYWORDS = {
    "健康糖": [
        "健康糖", "糖替代品", "甜味剂", "赤藓糖醇", "甜菊糖苷", "阿洛酮糖", 
        "低聚果糖", "木糖醇", "健康甜味", "零热量甜味剂", "糖醇"
    ],
    "小麦产业链": [
        "小麦", "面粉", "制粉", "谷朊粉", "面筋蛋白", "小麦淀粉", "全麦", 
        "麸皮", "小麦加工", "小麦品种", "面粉厂", "面包粉"
    ],
    "玉米产业链": [
        "玉米", "玉米淀粉", "玉米糖浆", "高果糖玉米糖浆", "葡萄糖", 
        "果葡糖浆", "玉米油", "燃料乙醇", "玉米深加工", "湿法研磨", "干法研磨"
    ],
    "合成生物学": [
        "合成生物学", "生物制造", "生物合成", "基因工程", "代谢工程", 
        "细胞工厂", "微生物发酵", "酶工程", "底盘细胞", "生物催化", "生物反应器"
    ],
    "工艺/制造过程": [
        "生产工艺", "制备方法", "提取", "纯化", "分离", "发酵工艺", "酶解", 
        "转化", "合成路线", "工艺优化", "放大生产", "下游处理", "质量控制", "副产物利用"
    ]
}

