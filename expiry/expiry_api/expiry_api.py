import os
import configparser
import logging
import pymysql
from datetime import datetime
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# 获取配置文件路径
config_path = os.path.join(os.path.dirname(__file__), 'config', 'config.ini')

# 读取配置文件
config = configparser.ConfigParser()
config.read(config_path)

# 获取数据库配置值
db_host = config.get('Database', 'host')
db_user = config.get('Database', 'user')
db_password = config.get('Database', 'password')
db_database = config.get('Database', 'database')

# 设置数据库连接URI
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql://{db_user}:{db_password}@{db_host}/{db_database}"

# 设置日志记录
log_level = config.get('Logging', 'level')
log_path = config.get('Logging', 'path')
logging.basicConfig(level=log_level, filename=log_path, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

# 创建数据库
def create_database():
    logger.info('创建数据库')
    conn = pymysql.connect(host=db_host, user=db_user, password=db_password)
    cursor = conn.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_database}")
    conn.commit()
    conn.close()

# 创建数据库表
def create_tables():
    logger.info('创建数据库表')
    with app.app_context():
        db.create_all()

# 创建db对象
db = SQLAlchemy(app)

# 定义证件模型
class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    expiry = db.Column(db.Date, nullable=False)

    def __repr__(self):
        return f"<Document {self.name}>"

    def as_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'expiry': self.expiry.strftime('%Y-%m-%d')
        }

# 获取证件列表
@app.route('/expiry-api/documents', methods=['GET'])
def get_documents():
    logger.info('获取证件列表')
    documents = Document.query.all()
    documents_list = [doc.as_dict() for doc in documents]
    return jsonify(documents_list)

# 添加证件
@app.route('/expiry-api/documents', methods=['POST'])
def add_document():
    logger.info('添加证件')
    data = request.get_json()
    name = data['name']
    expiry_str = data['expiry']
    expiry = datetime.strptime(expiry_str, '%Y-%m-%d').date()
    new_document = Document(name=name, expiry=expiry)
    db.session.add(new_document)
    db.session.commit()
    return jsonify(new_document.as_dict())

# 更新证件
@app.route('/expiry-api/documents/<int:id>', methods=['PUT'])
def update_document(id):
    logger.info('更新证件')
    document = Document.query.get(id)
    if document:
        data = request.get_json()
        document.name = data['name']
        document.expiry = datetime.strptime(data['expiry'], '%Y-%m-%d').date()
        db.session.commit()
        return jsonify(document.as_dict())
    else:
        return jsonify({"message": "证件不存在"}), 404

# 删除证件
@app.route('/expiry-api/documents/<int:id>', methods=['DELETE'])
def delete_document(id):
    logger.info('删除证件')
    document = Document.query.get(id)
    if document:
        db.session.delete(document)
        db.session.commit()
        return jsonify({"message": "删除成功"})
    else:
        return jsonify({"message": "证件不存在"}), 404

# 创建数据库
logger.info('开始创建数据库')
create_database()
logger.info('数据库创建完成')

# 创建数据库表
logger.info('开始创建数据库表')
create_tables()
logger.info('数据库表创建完成')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
