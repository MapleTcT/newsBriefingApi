from flask import Flask, jsonify, request
import logging
import database
from config import DOMAIN_KEYWORDS

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

@app.route('/api/latest_briefing', methods=['GET'])
def get_latest():
    """API端点，获取最新简报"""
    keyword = request.args.get('keyword', None)
    category = request.args.get('category', None)
    try:
        # 默认获取单个最新简报
        briefings = database.get_latest_briefings(limit=1, keyword=keyword, category=category)
        if briefings:
            # get_latest_briefings返回列表，取第一个元素
            return jsonify(briefings[0])
        else:
            return jsonify({"message": "未找到匹配的简报。"}), 404
    except Exception as e:
        logging.error(f"获取最新简报时API出错: {e}")
        return jsonify({"error": "内部服务器错误"}), 500

@app.route('/api/briefings', methods=['GET'])
def get_multiple_briefings():
    """API端点，获取多个最新简报"""
    try:
        limit = int(request.args.get('limit', 10))  # 默认10个简报
        keyword = request.args.get('keyword', None)
        category = request.args.get('category', None)
        if limit > 50:  # 安全限制
            limit = 50
        briefings = database.get_latest_briefings(limit=limit, keyword=keyword, category=category)
        return jsonify(briefings)
    except ValueError:
        return jsonify({"error": "无效的limit参数。必须是整数。"}), 400
    except Exception as e:
        logging.error(f"获取多个简报时API出错: {e}")
        return jsonify({"error": "内部服务器错误"}), 500

@app.route('/api/categories', methods=['GET'])
def get_categories():
    """API端点，获取所有可用的类别"""
    try:
        # 从配置中提取领域关键词的键作为类别
        categories = list(DOMAIN_KEYWORDS.keys())
        return jsonify({"categories": categories})
    except Exception as e:
        logging.error(f"获取类别时API出错: {e}")
        return jsonify({"error": "内部服务器错误"}), 500

def run_api(host='0.0.0.0', port=5000, debug=False):
    """运行Flask开发服务器"""
    # 生产环境应使用Gunicorn或uWSGI等适当的WSGI服务器
    logging.info("启动Flask API服务器...")
    # host='0.0.0.0'使其在网络上可访问
    app.run(host=host, port=port, debug=debug)
