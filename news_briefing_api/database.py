import sqlite3
import logging
from datetime import datetime
from config import DB_NAME

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_db_connection():
    """建立与SQLite数据库的连接"""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # 返回类似字典的对象
    return conn

def init_db():
    """初始化数据库并创建必要的表"""
    try:
        with get_db_connection() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS briefings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    source_url TEXT UNIQUE NOT NULL,
                    publication_date TEXT,
                    scrape_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    raw_content TEXT,
                    summary TEXT,
                    keywords TEXT,
                    source_site TEXT NOT NULL,
                    category TEXT
                )
            ''')
            conn.commit()
            logging.info("数据库初始化成功。")
    except sqlite3.Error as e:
        logging.error(f"数据库初始化错误: {e}")
        raise

def url_exists(url):
    """检查给定URL的简报是否已存在"""
    sql = "SELECT 1 FROM briefings WHERE source_url = ? LIMIT 1"
    try:
        with get_db_connection() as conn:
            cursor = conn.execute(sql, (url,))
            return cursor.fetchone() is not None
    except sqlite3.Error as e:
        logging.error(f"检查URL存在时出错 {url}: {e}")
        return False  # 假设不存在，以允许潜在处理

def add_briefing(data):
    """添加新简报到数据库。如果添加成功返回True，如果重复或出错返回False"""
    sql = '''
        INSERT INTO briefings(
            title, source_url, publication_date, raw_content, 
            summary, keywords, source_site, category
        ) VALUES(?,?,?,?,?,?,?,?)
    '''
    try:
        with get_db_connection() as conn:
            keywords_str = ",".join(data.get('keywords', []))
            conn.execute(sql, (
                data.get('title'),
                data.get('source_url'),
                data.get('publication_date'),
                data.get('raw_content'),
                data.get('summary'),
                keywords_str,
                data.get('source_site'),
                data.get('category', '')
            ))
            conn.commit()
            logging.info(f"添加简报: {data.get('title', 'N/A')[:50]}...")
            return True
    except sqlite3.IntegrityError:
        logging.warning(f"跳过重复简报: {data.get('source_url')}")
        return False
    except sqlite3.Error as e:
        logging.error(f"添加简报时出错 {data.get('source_url')}: {e}")
        return False

def get_latest_briefings(limit=1, keyword=None, category=None):
    """获取最新简报，可选择按关键词或类别筛选"""
    try:
        with get_db_connection() as conn:
            query = "SELECT * FROM briefings"
            params = []
            conditions = []
            
            if keyword:
                # 在标题、摘要和关键词中搜索
                conditions.append("(title LIKE ? OR summary LIKE ? OR keywords LIKE ?)")
                keyword_like = f"%{keyword}%"
                params.extend([keyword_like, keyword_like, keyword_like])
                
            if category:
                conditions.append("category = ?")
                params.append(category)
                
            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            query += " ORDER BY scrape_timestamp DESC LIMIT ?"
            params.append(limit)

            cursor = conn.execute(query, params)
            briefings = cursor.fetchall()
            # 将Row对象转换为标准字典并将关键词拆分回列表
            result = []
            for briefing in briefings:
                briefing_dict = dict(briefing)
                if briefing_dict.get('keywords'):
                    briefing_dict['keywords'] = briefing_dict['keywords'].split(',')
                else:
                    briefing_dict['keywords'] = []
                result.append(briefing_dict)
            return result
    except sqlite3.Error as e:
        logging.error(f"获取简报时出错: {e}")
        return []  # 出错时返回空列表

