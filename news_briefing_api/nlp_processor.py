import logging
import nltk
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
import yake
from config import SUMMARY_SENTENCE_COUNT, KEYWORD_COUNT, DOMAIN_KEYWORDS

# 下载必要的NLTK数据（只需运行一次）
try:
    nltk.data.find('tokenizers/punkt')
except nltk.downloader.DownloadError:
    logging.info("下载NLTK 'punkt'分词器数据...")
    nltk.download('punkt')

def process_text(text, domain=None):
    """对输入文本进行摘要和关键词提取处理"""
    summary = ""
    keywords = []
    domain_category = ""

    if not text or not isinstance(text, str):
        logging.warning("NLP处理收到空或无效文本。")
        return {'summary': summary, 'keywords': keywords, 'category': domain_category}

    # --- 使用sumy进行摘要 ---
    try:
        parser = PlaintextParser.from_string(text, Tokenizer("english"))  # 可根据需要调整语言
        summarizer = LsaSummarizer()
        summary_sentences = summarizer(parser.document, SUMMARY_SENTENCE_COUNT)
        summary = " ".join(str(sentence) for sentence in summary_sentences)
    except Exception as e:
        logging.error(f"摘要过程中出错: {e}")
        # 失败时留空摘要

    # --- 使用YAKE!进行关键词提取 ---
    try:
        # 根据需要调整参数（语言，n-gram大小等）
        kw_extractor = yake.KeywordExtractor(lan="en", n=3, dedupLim=0.9, top=KEYWORD_COUNT, features=None)
        raw_keywords = kw_extractor.extract_keywords(text)
        keywords = [kw[0] for kw in raw_keywords]  # 仅获取关键词文本
    except Exception as e:
        logging.error(f"关键词提取过程中出错: {e}")
        # 失败时留空关键词列表

    # --- 内容分类 ---
    if domain is None:
        # 自动检测领域分类
        domain_category = categorize_content(text, keywords)
    else:
        domain_category = domain
        
    return {
        'summary': summary,
        'keywords': keywords,
        'category': domain_category
    }

def categorize_content(text, extracted_keywords=None):
    """根据文本内容和提取的关键词自动分类内容领域"""
    # 如果没有提供提取的关键词，使用空列表
    if extracted_keywords is None:
        extracted_keywords = []
    
    # 将文本和提取的关键词合并为一个字符串进行分析
    combined_text = text.lower() + " " + " ".join(extracted_keywords).lower()
    
    # 计算每个领域关键词的匹配数量
    domain_scores = {}
    for domain, keywords in DOMAIN_KEYWORDS.items():
        score = 0
        for keyword in keywords:
            if keyword.lower() in combined_text:
                score += 1
        domain_scores[domain] = score
    
    # 选择得分最高的领域（如果有多个得分相同的最高领域，选择第一个）
    if domain_scores:
        max_score = max(domain_scores.values())
        if max_score > 0:  # 至少要有一个关键词匹配
            for domain, score in domain_scores.items():
                if score == max_score:
                    return domain
    
    # 如果没有明确匹配，返回空字符串
    return ""

