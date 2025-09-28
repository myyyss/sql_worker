import os
import json
import uuid
import re
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from functools import wraps
import datetime as dt

# 初始化Flask应用
app = Flask(__name__, static_folder='../sql-manager', static_url_path='')
CORS(app)

# 配置SQLite数据库（不依赖pyodbc）
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sql_manager.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secure-secret-key-here-keep-it-safe'  # 建议使用环境变量

# 初始化数据库
db = SQLAlchemy(app)

# JWT认证装饰器
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # 从请求头获取token
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'message': 'Token is missing or invalid'}), 401
        
        if not token:
            return jsonify({'message': 'token is missing!'}), 401
        
        try:
            # 解码token
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.filter_by(id=data['user_id']).first()
            
            if not current_user:
                raise Exception('User not found')
                
        except Exception as e:
            return jsonify({'message': 'token is invalid!', 'error': str(e)}), 401
        
        # 将当前用户传递给被装饰的函数
        return f(current_user, *args, **kwargs)
    
    return decorated

# 数据库模型
class User(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    display_name = db.Column(db.String(120), nullable=False)
    photo_url = db.Column(db.String(256), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'displayName': self.display_name,
            'photoURL': self.photo_url,
            'createdAt': self.created_at.isoformat()
        }

class SqlSnippet(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(120), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(60), default='未分类')
    tags = db.Column(db.JSON, default=[])
    notes = db.Column(db.Text, nullable=True)
    created_by = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_by = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联用户
    creator = db.relationship('User', foreign_keys=[created_by], backref='created_snippets')
    updater = db.relationship('User', foreign_keys=[updated_by], backref='updated_snippets')
    
    def __repr__(self):
        return f'<SqlSnippet {self.title}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'category': self.category,
            'tags': self.tags,
            'notes': self.notes,
            'createdBy': self.creator.to_dict() if self.creator else None,
            'createdAt': self.created_at.isoformat(),
            'updatedBy': self.updater.to_dict() if self.updater else None,
            'updatedAt': self.updated_at.isoformat()
        }

class Category(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(60), unique=True, nullable=False)
    created_by = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关联用户
    creator = db.relationship('User', backref='created_categories')
    
    def __repr__(self):
        return f'<Category {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'createdBy': self.creator.to_dict() if self.creator else None,
            'createdAt': self.created_at.isoformat()
        }

class Tag(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(60), unique=True, nullable=False)
    created_by = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关联用户
    creator = db.relationship('User', backref='created_tags')
    
    def __repr__(self):
        return f'<Tag {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'createdBy': self.creator.to_dict() if self.creator else None,
            'createdAt': self.created_at.isoformat()
        }

class Comment(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    sql_snippet_id = db.Column(db.String(36), db.ForeignKey('sql_snippet.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    created_by = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关联
    sql_snippet = db.relationship('SqlSnippet', backref='comments')
    creator = db.relationship('User', backref='created_comments')
    
    def __repr__(self):
        return f'<Comment {self.id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'sqlSnippetId': self.sql_snippet_id,
            'text': self.text,
            'createdBy': self.creator.to_dict() if self.creator else None,
            'createdAt': self.created_at.isoformat()
        }

# API路由
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # 检查必填字段
    if not all(k in data for k in ('email', 'password', 'displayName')):
        return jsonify({'message': 'Missing required fields'}), 400
    
    # 检查邮箱邮箱是否已存在
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Email already exists'}), 400
    
    # 创建新用户
    hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')
    new_user = User(
        email=data['email'],
        password=hashed_password,
        display_name=data['displayName'],
        photo_url=data.get('photoURL')
    )
    
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({'message': 'User created successfully'}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    
    # 检查必填字段
    if not all(k in data for k in ('email', 'password')):
        return jsonify({'message': 'Missing required fields'}), 400
    
    # 查找用户
    user = User.query.filter_by(email=data['email']).first()
    
    # 检查用户是否存在和密码是否正确
    if not user or not check_password_hash(user.password, data['password']):
        return jsonify({'message': 'Invalid email or password'}), 401
    
    # 生成JWT token
    token = jwt.encode({
        'user_id': user.id,
        'exp': dt.datetime.utcnow() + dt.timedelta(days=1)
    }, app.config['SECRET_KEY'], algorithm="HS256")
    
    return jsonify({
        'token': token,
        'user': user.to_dict()
    }), 200

@app.route('/api/user', methods=['GET'])
@token_required
def get_user(current_user):
    return jsonify(current_user.to_dict()), 200

# SQL Snippet路由
@app.route('/api/sql-snippets', methods=['GET'])
@token_required
def get_sql_snippets(current_user):
    snippets = SqlSnippet.query.order_by(SqlSnippet.updated_at.desc()).all()
    return jsonify([snippet.to_dict() for snippet in snippets]), 200

@app.route('/api/sql-snippets', methods=['POST'])
@token_required
def create_sql_snippet(current_user):
    data = request.get_json()
    
    # 检查必填字段
    if not all(k in data for k in ('title', 'content')):
        return jsonify({'message': 'Missing required fields'}), 400
    
    new_snippet = SqlSnippet(
        title=data['title'],
        content=data['content'],
        category=data.get('category', '未分类'),
        tags=data.get('tags', []),
        notes=data.get('notes', ''),
        created_by=current_user.id,
        updated_by=current_user.id
    )
    
    db.session.add(new_snippet)
    db.session.commit()
    
    return jsonify(new_snippet.to_dict()), 201

@app.route('/api/sql-snippets/<snippet_id>', methods=['GET'])
@token_required
def get_sql_snippet(current_user, snippet_id):
    snippet = SqlSnippet.query.get(snippet_id)
    
    if not snippet:
        return jsonify({'message': 'SQL snippet not found'}), 404
    
    return jsonify(snippet.to_dict()), 200

@app.route('/api/sql-snippets/<snippet_id>', methods=['PUT'])
@token_required
def update_sql_snippet(current_user, snippet_id):
    snippet = SqlSnippet.query.get(snippet_id)
    
    if not snippet:
        return jsonify({'message': 'SQL snippet not found'}), 404
    
    # 检查权限
    if snippet.created_by != current_user.id:
        return jsonify({'message': 'You do not have permission to update this snippet'}), 403
    
    data = request.get_json()
    
    # 更新字段
    if 'title' in data:
        snippet.title = data['title']
    if 'content' in data:
        snippet.content = data['content']
    if 'category' in data:
        snippet.category = data['category']
    if 'tags' in data:
        snippet.tags = data['tags']
    if 'notes' in data:
        snippet.notes = data['notes']
    
    snippet.updated_by = current_user.id
    
    db.session.commit()
    
    return jsonify(snippet.to_dict()), 200

@app.route('/api/sql-snippets/<snippet_id>', methods=['DELETE'])
@token_required
def delete_sql_snippet(current_user, snippet_id):
    snippet = SqlSnippet.query.get(snippet_id)
    
    if not snippet:
        return jsonify({'message': 'SQL snippet not found'}), 404
    
    # 检查权限
    if snippet.created_by != current_user.id:
        return jsonify({'message': 'You do not have permission to delete this snippet'}), 403
    
    # 删除相关评论
    Comment.query.filter_by(sql_snippet_id=snippet_id).delete()
    
    db.session.delete(snippet)
    db.session.commit()
    
    return jsonify({'message': 'SQL snippet deleted successfully'}), 200

# Category路由
@app.route('/api/categories', methods=['GET'])
@token_required
def get_categories(current_user):
    categories = Category.query.order_by(Category.name).all()
    # 添加默认分类
    result = [{'id': 'default', 'name': '未分类'}]
    result.extend([category.to_dict() for category in categories])
    return jsonify(result), 200

@app.route('/api/categories', methods=['POST'])
@token_required
def create_category(current_user):
    data = request.get_json()
    
    if not 'name' in data:
        return jsonify({'message': 'Missing required fields'}), 400
    
    # 检查分类是否已存在
    if Category.query.filter_by(name=data['name']).first():
        return jsonify({'message': 'Category already exists'}), 400
    
    new_category = Category(
        name=data['name'],
        created_by=current_user.id
    )
    
    db.session.add(new_category)
    db.session.commit()
    
    return jsonify(new_category.to_dict()), 201

@app.route('/api/categories/<category_id>', methods=['DELETE'])
@token_required
def delete_category(current_user, category_id):
    category = Category.query.get(category_id)
    
    if not category:
        return jsonify({'message': 'Category not found'}), 404
    
    # 更新使用此分类的SQL语句
    snippets = SqlSnippet.query.filter_by(category=category.name).all()
    for snippet in snippets:
        snippet.category = '未分类'
        snippet.updated_by = current_user.id
    
    db.session.delete(category)
    db.session.commit()
    
    return jsonify({'message': 'Category deleted successfully'}), 200

# Tag路由
@app.route('/api/tags', methods=['GET'])
@token_required
def get_tags(current_user):
    tags = Tag.query.order_by(Tag.name).all()
    return jsonify([tag.to_dict() for tag in tags]), 200

@app.route('/api/tags', methods=['POST'])
@token_required
def create_tag(current_user):
    data = request.get_json()
    
    if not 'name' in data:
        return jsonify({'message': 'Missing required fields'}), 400
    
    # 检查标签是否已存在
    if Tag.query.filter_by(name=data['name']).first():
        return jsonify({'message': 'Tag already exists'}), 400
    
    new_tag = Tag(
        name=data['name'],
        created_by=current_user.id
    )
    
    db.session.add(new_tag)
    db.session.commit()
    
    return jsonify(new_tag.to_dict()), 201

@app.route('/api/tag/<tag_id>', methods=['DELETE'])
@token_required
def delete_tag(current_user, tag_id):
    tag = Tag.query.get(tag_id)
    
    if not tag:
        return jsonify({'message': 'Tag not found'}), 404
    
    # 从所有SQL语句中移除此标签
    snippets = SqlSnippet.query.all()
    for snippet in snippets:
        if tag.name in snippet.tags:
            snippet.tags.remove(tag.name)
            snippet.updated_by = current_user.id
    
    db.session.delete(tag)
    db.session.commit()
    
    return jsonify({'message': 'Tag deleted successfully'}), 200

# Comment路由
@app.route('/api/sql-snippets/<snippet_id>/comments', methods=['GET'])
@token_required
def get_comments(current_user, snippet_id):
    comments = Comment.query.filter_by(sql_snippet_id=snippet_id).order_by(Comment.created_at.asc()).all()
    return jsonify([comment.to_dict() for comment in comments]), 200

@app.route('/api/sql-snippets/<snippet_id>/comments', methods=['POST'])
@token_required
def create_comment(current_user, snippet_id):
    # 检查SQL语句是否存在
    snippet = SqlSnippet.query.get(snippet_id)
    if not snippet:
        return jsonify({'message': 'SQL snippet not found'}), 404
    
    data = request.get_json()
    
    if not 'text' in data:
        return jsonify({'message': 'Missing required fields'}), 400
    
    new_comment = Comment(
        sql_snippet_id=snippet_id,
        text=data['text'],
        created_by=current_user.id
    )
    
    db.session.add(new_comment)
    db.session.commit()
    
    return jsonify(new_comment.to_dict()), 201

@app.route('/api/comments/<comment_id>', methods=['DELETE'])
@token_required
def delete_comment(current_user, comment_id):
    comment = Comment.query.get(comment_id)
    
    if not comment:
        return jsonify({'message': 'Comment not found'}), 404
    
    # 检查权限
    if comment.created_by != current_user.id:
        return jsonify({'message': 'You do not have permission to delete this comment'}), 403
    
    db.session.delete(comment)
    db.session.commit()
    
    return jsonify({'message': 'Comment deleted successfully'}), 200

# SQL执行路由
@app.route('/api/execute-sql', methods=['POST'])
@token_required
def execute_sql(current_user):
    data = request.get_json()
    
    if not 'sql' in data:
        return jsonify({'message': 'Missing required fields'}), 400
    
    sql = data['sql']
    lower_sql = sql.lower()
    
    # 模拟错误
    if 'error' in lower_sql:
        return jsonify({
            'error': '模拟错误: 这是一个测试错误',
            'success': False
        }), 400
    
    # 模拟SELECT语句
    if lower_sql.startswith('select'):
        # 尝试解析表名
        table_name = 'users'  # 默认表名
        from_match = re.search(r'from\s+(\w+)', lower_sql)
        if from_match and from_match.group(1):
            table_name = from_match.group(1)
        
        # 根据不同表名返回不同数据
        columns = []
        rows = []
        
        if table_name == 'users':
            columns = ['id', 'name', 'email', 'created_at']
            for i in range(1, 11):
                rows.append({
                    'id': i,
                    'name': f'User {i}',
                    'email': f'user{i}@example.com',
                    'created_at': (datetime.now() - dt.timedelta(days=30 * i)).isoformat()
                })
        elif table_name == 'products':
            columns = ['id', 'product_name', 'price', 'stock', 'category']
            categories = ['Electronics', 'Books', 'Clothing', 'Home', 'Beauty']
            for i in range(1, 11):
                rows.append({
                    'id': i,
                    'product_name': f'Product {i}',
                    'price': round(10 + (i * 10.5), 2),
                    'stock': 100 - i,
                    'category': categories[i % len(categories)]
                })
        elif table_name == 'orders':
            columns = ['id', 'user_id', 'order_date', 'total_amount', 'status']
            statuses = ['Pending', 'Processing', 'Shipped', 'Delivered', 'Cancelled']
            for i in range(1, 11):
                rows.append({
                    'id': i,
                    'user_id': (i % 5) + 1,
                    'order_date': (datetime.now() - dt.timedelta(days=i)).isoformat(),
                    'total_amount': round(100 + (i * 20.5), 2),
                    'status': statuses[i % len(statuses)]
                })
        elif table_name == 'customers':
            columns = ['customer_id', 'first_name', 'last_name', 'phone', 'address']
            first_names = ['John', 'Jane', 'Michael', 'Emily', 'David', 'Sarah', 'Robert', 'Lisa']
            last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Miller', 'Davis', 'Garcia']
            for i in range(1, 11):
                rows.append({
                    'customer_id': i,
                    'first_name': first_names[i % len(first_names)],
                    'last_name': last_names[i % len(last_names)],
                    'phone': f'+1-555-{100 + i}-{1000 + i}',
                    'address': f'{100 + i} Main St, City, Country'
                })
        else:
            # 自定义表名，返回默认数据
            columns = ['id', 'column1', 'column2', 'column3']
            for i in range(1, 6):
                rows.append({
                    'id': i,
                    'column1': f'Value {i}-1',
                    'column2': f'Value {i}-2',
                    'column3': f'Value {i}-3'
                })
        
        return jsonify({
            'columns': columns,
            'rows': rows,
            'success': True,
            'message': f'Successfully executed query, returned {len(rows)} rows'
        }), 200
    else:
        # 模拟其他SQL语句执行
        return jsonify({
            'success': True,
            'message': 'SQL statement executed successfully'
        }), 200

# 前端路由
@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def static_file(path):
    return send_from_directory(app.static_folder, path)

# 初始化数据库
with app.app_context():
    db.create_all()
    
    # 添加默认用户（仅用于开发测试）
    if not User.query.filter_by(email='test@example.com').first():
        hashed_password = generate_password_hash('password123', method='pbkdf2:sha256')
        default_user = User(
            email='test@example.com',
            password=hashed_password,
            display_name='Test User',
            photo_url='https://ui-avatars.com/api/?name=Test+User'
        )
        db.session.add(default_user)
        db.session.commit()
        
        # 添加默认分类
        default_categories = ['常用查询', '报表统计', '数据清理', '系统管理']
        for cat_name in default_categories:
            if not Category.query.filter_by(name=cat_name).first():
                category = Category(
                    name=cat_name,
                    created_by=default_user.id
                )
                db.session.add(category)
        
        # 添加默认标签
        default_tags = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'JOIN', 'SUBQUERY']
        for tag_name in default_tags:
            if not Tag.query.filter_by(name=tag_name).first():
                tag = Tag(
                    name=tag_name,
                    created_by=default_user.id
                )
                db.session.add(tag)
        
        # 添加示例SQL语句
        example_sql = SqlSnippet(
            title='获取用户列表',
            content='SELECT id, name, email, created_at FROM users WHERE status = "active" LIMIT 10;',
            category='常用查询',
            tags=['SELECT', 'LIMIT'],
            notes='获取活跃用户列表，限制前10条记录',
            created_by=default_user.id,
            updated_by=default_user.id
        )
        db.session.add(example_sql)
        
        db.session.commit()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
