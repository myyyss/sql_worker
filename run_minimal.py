#!/usr/bin/env python3
"""
SQL管理工具 - 极简版本启动器
避免使用复杂依赖，解决编译问题
"""

import os
import sys
import json
import uuid
import sqlite3
import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import base64
import hashlib
import jwt
from datetime import datetime, timedelta
import subprocess
import re

# 全局配置
PORT = 5000
DB_FILE = 'sql_manager_minimal.db'
SECRET_KEY = 'your-secure-secret-key-here'

# 初始化数据库
def init_db():
    """初始化SQLite数据库"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # 创建用户表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        display_name TEXT NOT NULL,
        photo_url TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # 创建SQL语句表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sql_snippets (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        category TEXT DEFAULT '未分类',
        tags TEXT DEFAULT '[]',
        notes TEXT,
        created_by TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT CURRENT_TIMESTAMP,
        updated_by TEXT NOT NULL,
        updated_at TIMESTAMP DEFAULT CURRENT_timestamp
    )
    ''')
    
    # 创建分类表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS categories (
        id TEXT PRIMARY KEY,
        name TEXT UNIQUE NOT NULL,
        created_by TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT CURRENT_TIMESTAMP
    )
    ''')
    
    # 创建标签表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tags (
        id TEXT PRIMARY KEY,
        name TEXT UNIQUE NOT NULL,
        created_by TEXT NOT NULL,
        created_at TIMESTAMP default current_timestamp
    )
    ''')
    
    # 创建评论表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS comments (
        id TEXT PRIMARY KEY,
        sql_snippet_id TEXT NOT NULL,
        text TEXT NOT NULL,
        created_by TEXT NOT NULL,
        created_at TIMESTAMP default CURRENT CURRENT_TIMESTAMP
    )
    ''')
    
    # 添加默认用户（仅用于开发测试）
    cursor.execute("SELECT * FROM users WHERE email = 'test@example.com'")
    if not cursor.fetchone():
        # 密码: password123 (简单哈希)
        password_hash = hashlib.sha256('password123'.encode()).hexdigest()
        cursor.execute('''
        INSERT INTO users (id, email, password, display_name, photo_url)
        VALUES (?, ?, ?, ?, ?)
        ''', (
            str(uuid.uuid4()),
            'test@example.com',
            password_hash,
            'Test User',
            'https://ui-avatars.com/api/?name=Test+User'
        ))
        
        # 添加默认分类
        user_id = cursor.lastrowid
        default_categories = ['常用查询', '报表统计', '数据清理', '系统管理']
        for cat_name in default_categories:
            cursor.execute('''
            INSERT INTO categories (id, name, created_by)
            VALUES (?, ?, ?)
            ''', (str(uuid.uuid4()), cat_name, user_id))
        
        # 添加默认标签
        default_tags = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'JOIN', 'SUBQUERY']
        for tag_name in default_tags:
            cursor.execute('''
            INSERT INTO tags (id, name, created_by)
            VALUES (?, ?, ?)
            ''', (str(uuid.uuid4()), tag_name, user_id))
        
        # 添加示例SQL语句
        cursor.execute('''
        INSERT INTO sql_snippets (id, title, content, category, tags, notes, created_by, updated_by)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            str(uuid.uuid4()),
            '获取用户列表',
            'SELECT id, name, email, created_at FROM users WHERE status = "active" LIMIT 10;',
            '常用查询',
            json.dumps(['SELECT', 'LIMIT']),
            '获取活跃用户列表，限制前10条记录',
            user_id,
            user_id
        ))
    
    conn.commit()
    conn.close()

# 简单HTTP请求处理器
class SQLManagerHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory='sql-manager', **kwargs)
    
    def do_GET(self):
        parsed_path = urlparse(self.path)
        
        # API路由处理
        if parsed_path.path.startswith('/api'):
            self.handle_api_request(parsed_path)
        else:
            # 静态文件处理
            super().do_GET()
    
    def do_POST(self):
        parsed_path = urlparse(self.path)
        
        # API路由处理
        if parsed_path.path.startswith('/api'):
            self.handle_api_request(parsed_path)
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')
    
    def handle_api_request(self, parsed_path):
        """处理API请求"""
        path = parsed_path.path
        query_params = parse_qs(parsed_path.query)
        
        # 获取请求体
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else ''
        
        # 解析JSON数据
        try:
            data = json.loads(post_data) if post_data else {}
        except json.JSONDecodeError:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'message': 'Invalid JSON'}).encode())
            return
        
        # 路由处理
        if path == '/api/login':
            self.handle_login(data)
        elif path == '/api/user':
            self.handle_get_user(data)
        elif path == '/api/sql-snippets':
            if self.command == 'GET':
                self.handle_get_sql_snippets()
            elif self.command == 'POST':
                self.handle_create_sql_snippet(data)
        elif path.startswith('/api/sql-snippets/'):
            parts = path.split('/')
            if len(parts) >= 4 and parts[3]:
                snippet_id = parts[3]
                if self.command == 'GET':
                    self.handle_get_sql_snippet(snippet_id)
                elif self.command == 'PUT':
                    self.handle_update_sql_snippet(snippet_id, data)
                elif self.command == 'DELETE':
                    self.handle_delete_sql_snippet(snippet_id)
        elif path == '/api/categories':
            if self.command == 'GET':
                self.handle_get_categories()
            elif self.command == 'POST':
                self.handle_create_category(data)
        elif path.startswith('/api/categories/') and self.command == 'DELETE':
            parts = path.split('/')
            if len(parts) >= 4 and parts[3]:
                category_id = parts[3]
                self.handle_delete_category(category_id)
        elif path == '/api/tags':
            if self.command == 'GET':
                self.handle_get_tags()
            elif self.command == 'POST':
                self.handle_create_tag(data)
        elif path.startswith('/api/tags/') and self.command == 'DELETE':
            parts = path.split('/')
            if len(parts) >= 4 and parts[3]:
                tag_id = parts[3]
                self.handle_delete_tag(tag_id)
        elif path.startswith('/api/sql-snippets/') and '/comments' in path:
            parts = path.split('/')
            if len(parts) >= 5 and parts[3] and parts[4] == 'comments':
                snippet_id = parts[3]
                if self.command == 'GET':
                    self.handle_get_comments(snippet_id)
                elif self.command == 'POST':
                    self.handle_create_comment(snippet_id, data)
        elif path.startswith('/api/comments/') and self.command == 'DELETE':
            parts = path.split('/')
            if len(parts) >= 4 and parts[3]:
                comment_id = parts[3]
                self.handle_delete_comment(comment_id)
        elif path == '/api/execute-sql' and self.command == 'POST':
            self.handle_execute_sql(data)
        else:
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'message': 'API endpoint not found'}).encode())
    
    def get_current_user(self):
        """从请求头获取当前用户"""
        auth_header = self.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            try:
                payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
                user_id = payload.get('user_id')
                
                conn = sqlite3.connect(DB_FILE)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
                user = cursor.fetchone()
                
                conn.close()
                
                if user:
                    return dict(user)
            except Exception as e:
                print(f"Token verification failed: {e}")
        
        return None
    
    def send_json_response(self, data, status_code=200):
        """发送JSON响应"""
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def handle_login(self, data):
        """处理登录请求"""
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            self.send_json_response({'message': 'Missing required fields'}, 400)
            return
        
        # 简单密码验证（实际应用中应该使用更安全的方法）
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE email = ? AND password = ?', (email, password_hash))
        user = cursor.fetchone()
        
        conn.close()
        
        if user:
            user_dict = dict(user)
            
            # 生成JWT token
            token = jwt.encode({
                'user_id': user_dict['id'],
                'exp': datetime.utcnow() + timedelta(days=1)
            }, SECRET_KEY, algorithm="HS256")
            
            # 移除密码字段
            del user_dict['password']
            
            # 格式化用户数据
            response_user = {
                'id': user_dict['id'],
                'email': user_dict['email'],
                'displayName': user_dict['display_name'],
                'photoURL': user_dict['photo_url'],
                'createdAt': user_dict['created_at']
            }
            
            self.send_json_response({
                'token': token,
                'user': response_user
            })
        else:
            self.send_json_response({'message': 'Invalid email or password'}, 401)
    
    def handle_get_user(self, data):
        """获取当前用户信息"""
        user = self.get_current_user()
        
        if user:
            # 移除密码字段
            user_dict = dict(user)
            del user_dict['password']
            
            response_user = {
                'id': user_dict['id'],
                'email': user_dict['email'],
                'displayName': user_dict['display_name'],
                'photoURL': user_dict['photo_url'],
                'createdAt': user_dict['created_at']
            }
            
            self.send_json_response(response_user)
        else:
            self.send_json_response({'message': 'Authentication required'}, 401)
    
    def handle_get_sql_snippets(self):
        """获取所有SQL语句"""
        user = self.get_current_user()
        
        if not user:
            self.send_json_response({'message': 'Authentication required'}, 401)
            return
        
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT s.*, u1.display_name as creator_name, u1.photo_url as creator_photo,
               u2.display_name as updater_name, u2.photo_url as updater_photo
        FROM sql_snippets s
        JOIN users u1 ON s.created_by = u1.id
        JOIN users u2 ON s.updated_by = u2.id
        ORDER BY s.updated_at DESC
        ''')
        
        snippets = []
        for row in cursor.fetchall():
            row_dict = dict(row)
            
            # 解析JSON字段
            try:
                tags = json.loads(row_dict['tags']) if row_dict['tags'] else []
            except json.JSONDecodeError:
                tags = []
            
            snippet = {
                'id': row_dict['id'],
                'title': row_dict['title'],
                'content': row_dict['content'],
                'category': row_dict['category'],
                'tags': tags,
                'notes': row_dict['notes'],
                'createdBy': {
                    'id': row_dict['created_by'],
                    'displayName': row_dict['creator_name'],
                    'photoURL': row_dict['creator_photo']
                },
                'createdAt': row_dict['created_at'],
                'updatedBy': {
                    'id': row_dict['updated_by'],
                    'displayName': row_dict['updater_name'],
                    'photoURL': row_dict['updater_photo']
                },
                'updatedAt': row_dict['updated_at']
            }
            
            snippets.append(snippet)
        
        conn.close()
        self.send_json_response(snippets)
    
    def handle_create_sql_snippet(self, data):
        """创建SQL语句"""
        user = self.get_current_user()
        
        if not user:
            self.send_json_response({'message': 'Authentication required'}, 401)
            return
        
        title = data.get('title')
        content = data.get('content')
        
        if not title or not content:
            self.send_json_response({'message': 'Missing required fields'}, 400)
            return
        
        snippet_id = str(uuid.uuid4())
        category = data.get('category', '未分类')
        tags = json.dumps(data.get('tags', []))
        notes = data.get('notes', '')
        
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            INSERT INTO sql_snippets 
            (id, title, content, category, tags, notes, created_by, updated_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                snippet_id, title, content, category, tags, notes,
                user['id'], user['id']
            ))
            
            conn.commit()
            
            # 获取创建的记录
            cursor.execute('SELECT * FROM sql_snippets WHERE id = ?', (snippet_id,))
            row = cursor.fetchone()
            
            response = {
                'id': row['id'],
                'title': row['title'],
                'content': row['content'],
                'category': row['category'],
                'tags': json.loads(row['tags']) if row['tags'] else [],
                'notes': row['notes'],
                'createdBy': {
                    'id': user['id'],
                    'displayName': user['display_name'],
                    'photoURL': user['photo_url']
                },
                'createdAt': row['created_at'],
                'updatedBy': {
                    'id': user['id'],
                    'displayName': user['display_name'],
                    'photoURL': user['photo_url']
                },
                'updatedAt': row['updated_at']
            }
            
            self.send_json_response(response, 201)
            
        except Exception as e:
            conn.rollback()
            self.send_json_response({'message': f'Error creating snippet: {str(e)}'}, 500)
        finally:
            conn.close()
    
    def handle_get_sql_snippet(self, snippet_id):
        """获取单个SQL语句"""
        user = self.get_current_user()
        
        if not user:
            self.send_json_response({'message': 'Authentication required'}, 401)
            return
        
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT s.*, u1.display_name as creator_name, u1.photo_url as creator_photo,
               u2.display_name as updater_name, u2.photo_url as updater_photo
        FROM sql_snippets s
        JOIN users u1 ON s.created_by = u1.id
        JOIN users u2 ON s.updated_by = u2.id
        WHERE s.id = ?
        ''', (snippet_id,))
        
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            self.send_json_response({'message': 'SQL snippet not found'}, 404)
            return
        
        row_dict = dict(row)
        
        # 解析JSON字段
        try:
            tags = json.loads(row_dict['tags']) if row_dict['tags'] else []
        except json.JSONDecodeError:
            tags = []
        
        snippet = {
            'id': row_dict['id'],
            'title': row_dict['title'],
            'content': row_dict['content'],
            'category': row_dict['category'],
            'tags': tags,
            'notes': row_dict['notes'],
            'createdBy': {
                'id': row_dict['created_by'],
                'displayName': row_dict['creator_name'],
                'photoURL': row_dict['creator_photo']
            },
            'createdAt': row_dict['created_at'],
            'updatedBy': {
                'id': row_dict['updated_by'],
                'displayName': row_dict['updater_name'],
                'photoURL': row_dict['updater_photo']
            },
            'updatedAt': row_dict['updated_at']
        }
        
        conn.close()
        self.send_json_response(snippet)
    
    def handle_update_sql_snippet(self, snippet_id, data):
        """更新SQL语句"""
        user = self.get_current_user()
        
        if not user:
            self.send_json_response({'message': 'Authentication required'}, 401)
            return
        
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 检查SQL语句是否存在
        cursor.execute('SELECT * FROM sql_snippets WHERE id = ?', (snippet_id,))
        snippet = cursor.fetchone()
        
        if not snippet:
            conn.close()
            self.send_json_response({'message': 'SQL snippet not found'}, 404)
            return
        
        # 检查权限
        if snippet['created_by'] != user['id']:
            conn.close()
            self.send_json_response({'message': 'You do not have permission to update this snippet'}, 403)
            return
        
        try:
            # 更新字段
            updates = []
            params = []
            
            if 'title' in data:
                updates.append('title = ?')
                params.append(data['title'])
            
            if 'content' in data:
                updates.append('content = ?')
                params.append(data['content'])
            
            if 'category' in data:
                updates.append('category = ?')
                params.append(data['category'])
            
            if 'tags' in data:
                updates.append('tags = ?')
                params.append(json.dumps(data['tags']))
            
            if 'notes' in data:
                updates.append('notes = ?')
                params.append(data['notes'])
            
            # 添加更新者和更新时间
            updates.append('updated_by = ?')
            params.append(user['id'])
            
            updates.append('updated_at = CURRENT_TIMESTAMP')
            
            if updates:
                sql = f"UPDATE sql_snippets SET {', '.join(updates)} WHERE id = ?"
                params.append(snippet_id)
                
                cursor.execute(sql, params)
                conn.commit()
            
            # 获取更新后的记录
            cursor.execute('''
            SELECT s.*, u1.display_name as creator_name, u1.photo_url as creator_photo,
                   u2.display_name as updater_name, u2.photo_url as updater_photo
            FROM sql_snippets s
            JOIN users u1 ON s.created_by = u1.id
            JOIN users u2 ON s.updated_by = u2.id
            WHERE s.id = ?
            ''', (snippet_id,))
            
            row = cursor.fetchone()
            row_dict = dict(row)
            
            # 解析JSON字段
            try:
                tags = json.loads(row_dict['tags']) if row_dict['tags'] else []
            except json.JSONDecodeError:
                tags = []
            
            response = {
                'id': row_dict['id'],
                'title': row_dict['title'],
                'content': row_dict['content'],
                'category': row_dict['category'],
                'tags': tags,
                'notes': row_dict['notes'],
                'createdBy': {
                    'id': row_dict['created_by'],
                    'displayName': row_dict['creator_name'],
                    'photoURL': row_dict['creator_photo']
                },
                'createdAt': row_dict['created_at'],
                'updatedBy': {
                    'id': row_dict['updated_by'],
                    'displayName': row_dict['updater_name'],
                    'photoURL': row_dict['updater_photo']
                },
                'updatedAt': row_dict['updated_at']
            }
            
            self.send_json_response(response)
            
        except Exception as e:
            conn.rollback()
            self.send_json_response({'message': f'Error updating snippet: {str(e)}'}, 500)
        finally:
            conn.close()
    
    def handle_delete_sql_snippet(self, snippet_id):
        """删除SQL语句"""
        user = self.get_current_user()
        
        if not user:
            self.send_json_response({'message': 'Authentication required'}, 401)
            return
        
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        try:
            # 检查SQL语句是否存在
            cursor.execute('SELECT * FROM sql_snippets WHERE id = ?', (snippet_id,))
            snippet = cursor.fetchone()
            
            if not snippet:
                conn.close()
                self.send_json_response({'message': 'SQL snippet not found'}, 404)
                return
            
            # 检查权限
            if snippet['created_by'] != user['id']:
                conn.close()
                self.send_json_response({'message': 'You do not have permission to delete this snippet'}, 403)
                return
            
            # 删除相关评论
            cursor.execute('DELETE FROM comments WHERE sql_snippet_id = ?', (snippet_id,))
            
            # 删除SQL语句
            cursor.execute('DELETE FROM sql_snippets WHERE id = ?', (snippet_id,))
            
            conn.commit()
            self.send_json_response({'message': 'SQL snippet deleted successfully'})
            
        except Exception as e:
            conn.rollback()
            self.send_json_response({'message': f'Error deleting snippet: {str(e)}'}, 500)
        finally:
            conn.close()
    
    def handle_get_categories(self):
        """获取所有分类"""
        user = self.get_current_user()
        
        if not user:
            self.send_json_response({'message': 'Authentication required'}, 401)
            return
        
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT c.*, u.display_name as creator_name, u.photo_url as creator_photo
        FROM categories c
        JOIN users u ON c.created_by = u.id
        ORDER BY c.name
        ''')
        
        categories = []
        for row in cursor.fetchall():
            row_dict = dict(row)
            
            category = {
                'id': row_dict['id'],
                'name': row_dict['name'],
                'createdBy': {
                    'id': row_dict['created_by'],
                    'displayName': row_dict['creator_name'],
                    'photoURL': row_dict['creator_photo']
                },
                'createdAt': row_dict['created_at']
            }
            
            categories.append(category)
        
        conn.close()
        
        # 添加默认分类
        result = [{'id': 'default', 'name': '未分类'}]
        result.extend(categories)
        
        self.send_json_response(result)
    
    def handle_create_category(self, data):
        """创建分类"""
        user = self.get_current_user()
        
        if not user:
            self.send_json_response({'message': 'Authentication required'}, 401)
            return
        
        name = data.get('name')
        
        if not name:
            self.send_json_response({'message': 'Missing required fields'}, 400)
            return
        
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        try:
            # 检查分类是否已存在
            cursor.execute('SELECT * FROM categories WHERE name = ?', (name,))
            if cursor.fetchone():
                conn.close()
                self.send_json_response({'message': 'Category already exists'}, 400)
                return
            
            # 创建新分类
            category_id = str(uuid.uuid4())
            cursor.execute('''
            INSERT INTO categories (id, name, created_by)
            VALUES (?, ?, ?)
            ''', (category_id, name, user['id']))
            
            conn.commit()
            
            # 获取创建的记录
            cursor.execute('''
            SELECT c.*, u.display_name as creator_name, u.photo_url as creator_photo
            FROM categories c
            JOIN users u ON c.created_by = u.id
            WHERE c.id = ?
            ''', (category_id,))
            
            row = cursor.fetchone()
            row_dict = dict(row)
            
            response = {
                'id': row_dict['id'],
                'name': row_dict['name'],
                'createdBy': {
                    'id': row_dict['created_by'],
                    'displayName': row_dict['creator_name'],
                    'photoURL': row_dict['creator_photo']
                },
                'createdAt': row_dict['created_at']
            }
            
            self.send_json_response(response, 201)
            
        except Exception as e:
            conn.rollback()
            self.send_json_response({'message': f'Error creating category: {str(e)}'}, 500)
        finally:
            conn.close()
    
    def handle_delete_category(self, category_id):
        """删除分类"""
        user = self.get_current_user()
        
        if not user:
            self.send_json_response({'message': 'Authentication required'}, 401)
            return
        
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        try:
            # 检查分类是否存在
            cursor.execute('SELECT * FROM categories WHERE id = ?', (category_id,))
            category = cursor.fetchone()
            
            if not category:
                conn.close()
                self.send_json_response({'message': 'Category not found'}, 404)
                return
            
            # 更新使用此分类的SQL语句
            cursor.execute('''
            UPDATE sql_snippets 
            SET category = '未分类', updated_by = ?
            WHERE category = ?
            ''', (user['id'], category['name']))
            
            # 删除分类
            cursor.execute('DELETE FROM categories WHERE id = ?', (category_id,))
            
            conn.commit()
            self.send_json_response({'message': 'Category deleted successfully'})
            
        except Exception as e:
            conn.rollback()
            self.send_json_response({'message': f'Error deleting category: {str(e)}'}, 500)
        finally:
            conn.close()
    
    def handle_get_tags(self):
        """获取所有标签"""
        user = self.get_current_user()
        
        if not user:
            self.send_json_response({'message': 'Authentication required'}, 401)
            return
        
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT t.*, u.display_name as creator_name, u.photo_url as creator_photo
        FROM tags t
        JOIN users u ON t.created_by = u.id
        ORDER BY t.name
        ''')
        
        tags = []
        for row in cursor.fetchall():
            row_dict = dict(row)
            
            tag = {
                'id': row_dict['id'],
                'name': row_dict['name'],
                'createdBy': {
                    'id': row_dict['created_by'],
                    'displayName': row_dict['creator_name'],
                    'photoURL': row_dict['creator_photo']
                },
                'createdAt': row_dict['created_at']
            }
            
            tags.append(tag)
        
        conn.close()
        self.send_json_response(tags)
    
    def handle_create_tag(self, data):
        """创建标签"""
        user = self.get_current_user()
        
        if not user:
            self.send_json_response({'message': 'Authentication required'}, 401)
            return
        
        name = data.get('name')
        
        if not name:
            self.send_json_response({'message': 'Missing required fields'}, 400)
            return
        
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        try:
            # 检查标签是否已存在
            cursor.execute('SELECT * FROM tags WHERE name = ?', (name,))
            if cursor.fetchone():
                conn.close()
                self.send_json_response({'message': 'Tag already exists'}, 400)
                return
            
            # 创建新标签
            tag_id = str(uuid.uuid4())
            cursor.execute('''
            INSERT INTO tags (id, name, created_by)
            VALUES (?, ?, ?)
            ''', (tag_id, name, user['id']))
            
            conn.commit()
            
            # 获取创建的记录
            cursor.execute('''
            SELECT t.*, u.display_name as creator_name, u.photo_url as creator_photo
            FROM tags t
            JOIN users u ON t.created_by = u.id
            WHERE t.id = ?
            ''', (tag_id,))
            
            row = cursor.fetchone()
            row_dict = dict(row)
            
            response = {
                'id': row_dict['id'],
                'name': row_dict['name'],
                'createdBy': {
                    'id': row_dict['created_by'],
                    'displayName': row_dict['creator_name'],
                    'photoURL': row_dict['creator_photo']
                },
                'createdAt': row_dict['created_at']
            }
            
            self.send_json_response(response, 201)
            
        except Exception as e:
            conn.rollback()
            self.send_json_response({'message': f'Error creating tag: {str(e)}'}, 500)
        finally:
            conn.close()
    
    def handle_delete_tag(self, tag_id):
        """删除标签"""
        user = self.get_current_user()
        
        if not user:
            self.send_json_response({'message': 'Authentication required'}, 401)
            return
        
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        try:
            # 检查标签是否存在
            cursor.execute('SELECT * FROM tags WHERE id = ?', (tag_id,))
            tag = cursor.fetchone()
            
            if not tag:
                conn.close()
                self.send_json_response({'message': 'Tag not found'}, 404)
                return
            
            # 从所有SQL语句中移除此标签
            cursor.execute('SELECT id, tags FROM sql_snippets')
            snippets = cursor.fetchall()
            
            for snippet in snippets:
                try:
                    tags = json.loads(snippet['tags']) if snippet['tags'] else []
                    if tag['name'] in tags:
                        tags.remove(tag['name'])
                        cursor.execute('''
                        UPDATE sql_snippets 
                        SET tags = ?, updated_by = ?
                        WHERE id = ?
                        ''', (json.dumps(tags), user['id'], snippet['id']))
                except json.JSONDecodeError:
                    continue
            
            # 删除标签
            cursor.execute('DELETE FROM tags WHERE id = ?', (tag_id,))
            
            conn.commit()
            self.send_json_response({'message': 'Tag deleted successfully'})
            
        except Exception as e:
            conn.rollback()
            self.send_json_response({'message': f'Error deleting tag: {str(e)}'}, 500)
        finally:
            conn.close()
    
    def handle_get_comments(self, snippet_id):
        """获取SQL语句的评论"""
        user = self.get_current_user()
        
        if not user:
            self.send_json_response({'message': 'Authentication required'}, 401)
            return
        
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 检查SQL语句是否存在
        cursor.execute('SELECT * FROM sql_snippets WHERE id = ?', (snippet_id,))
        if not cursor.fetchone():
            conn.close()
            self.send_json_response({'message': 'SQL snippet not found'}, 404)
            return
        
        # 获取评论
        cursor.execute('''
        SELECT c.*, u.display_name as creator_name, u.photo_url as creator_photo
        FROM comments c
        JOIN users u ON c.created_by = u.id
        WHERE c.sql_snippet_id = ?
        ORDER BY c.created_at ASC
        ''', (snippet_id,))
        
        comments = []
        for row in cursor.fetchall():
            row_dict = dict(row)
            
            comment = {
                'id': row_dict['id'],
                'sqlSnippetId': row_dict['sql_snippet_id'],
                'text': row_dict['text'],
                'createdBy': {
                    'id': row_dict['created_by'],
                    'displayName': row_dict['creator_name'],
                    'photoURL': row_dict['creator_photo']
                },
                'createdAt': row_dict['created_at']
            }
            
            comments.append(comment)
        
        conn.close()
        self.send_json_response(comments)
    
    def handle_create_comment(self, snippet_id, data):
        """创建评论"""
        user = self.get_current_user()
        
        if not user:
            self.send_json_response({'message': 'Authentication required'}, 401)
            return
        
        text = data.get('text')
        
        if not text:
            self.send_json_response({'message': 'Missing required fields'}, 400)
            return
        
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        try:
            # 检查SQL语句是否存在
            cursor.execute('SELECT * FROM sql_snippets WHERE id = ?', (snippet_id,))
            if not cursor.fetchone():
                conn.close()
                self.send_json_response({'message': 'SQL snippet not found'}, 404)
                return
            
            # 创建新评论
            comment_id = str(uuid.uuid4())
            cursor.execute('''
            INSERT INTO comments (id, sql_snippet_id, text, created_by)
            VALUES (?, ?, ?, ?)
            ''', (comment_id, snippet_id, text, user['id']))
            
            conn.commit()
            
            # 获取创建的记录
            cursor.execute('''
            SELECT c.*, u.display_name as creator_name, u.photo_url as creator_photo
            FROM comments c
            JOIN users u ON c.created_by = u.id
            WHERE c.id = ?
            ''', (comment_id,))
            
            row = cursor.fetchone()
            row_dict = dict(row)
            
            response = {
                'id': row_dict['id'],
                'sqlSnippetId': row_dict['sql_snippet_id'],
                'text': row_dict['text'],
                'createdBy': {
                    'id': row_dict['created_by'],
                    'displayName': row_dict['creator_name'],
                    'photoURL': row_dict['creator_photo']
                },
                'createdAt': row_dict['created_at']
            }
            
            self.send_json_response(response, 201)
            
        except Exception as e:
            conn.rollback()
            self.send_json_response({'message': f'Error creating comment: {str(e)}'}, 500)
        finally:
            conn.close()
    
    def handle_delete_comment(self, comment_id):
        """删除评论"""
        user = self.get_current_user()
        
        if not user:
            self.send_json_response({'message': 'Authentication required'}, 401)
            return
        
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        try:
            # 检查评论是否存在
            cursor.execute('SELECT * FROM comments WHERE id = ?', (comment_id,))
            comment = cursor.fetchone()
            
            if not comment:
                conn.close()
                self.send_json_response({'message': 'Comment not found'}, 404)
                return
            
            # 检查权限
            if comment['created_by'] != user['id']:
                conn.close()
                self.send_json_response({'message': 'You do not have permission to delete this comment'}, 403)
                return
            
            # 删除评论
            cursor.execute('DELETE FROM comments WHERE id = ?', (comment_id,))
            
            conn.commit()
            self.send_json_response({'message': 'Comment deleted successfully'})
            
        except Exception as e:
            conn.rollback()
            self.send_json_response({'message': f'Error deleting comment: {str(e)}'}, 500)
        finally:
            conn.close()
    
    def handle_execute_sql(self, data):
        """执行SQL语句（模拟）"""
        user = self.get_current_user()
        
        if not user:
            self.send_json_response({'message': 'Authentication required'}, 401)
            return
        
        sql = data.get('sql', '')
        
        if not sql:
            self.send_json_response({'message': 'Missing required fields'}, 400)
            return
        
        lower_sql = sql.lower()
        
        # 模拟错误
        if 'error' in lower_sql:
            self.send_json_response({
                'error': '模拟错误: 这是一个测试错误',
                'success': False
            }, 400)
            return
        
        # 模拟SELECT语句
        if lower_sql.startswith('select'):
            import re
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
                        'created_at': (datetime.now() - timedelta(days=30 * i)).isoformat()
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
                        'order_date': (datetime.now() - timedelta(days=i)).isoformat(),
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
            
            self.send_json_response({
                'columns': columns,
                'rows': rows,
                'success': True,
                'message': f'Successfully executed query, returned {len(rows)} rows'
            })
        else:
            # 模拟其他SQL语句执行
            self.send_json_response({
                'success': True,
                'message': 'SQL statement executed successfully'
            })

def get_current_pip_version():
    """获取当前pip版本"""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "--version"],
            capture_output=True,
            text=True,
            check=True
        )
        output = result.stdout.strip()
        # 从输出中提取版本号
        match = re.search(r'pip\s+(\d+\.\d+\.?\d*)', output)
        if match:
            return match.group(1)
        return None
    except subprocess.CalledProcessError:
        return None
    except Exception:
        return None

def parse_version(version_str):
    """解析版本字符串为元组"""
    try:
        return tuple(map(int, version_str.split('.')))
    except ValueError:
        return (0, 0, 0)

def is_version_less_than(current, target):
    """检查当前版本是否小于目标版本"""
    current_tuple = parse_version(current)
    target_tuple = parse_version(target)
    
    # 确保两个版本元组长度相同
    max_len = max(len(current_tuple), len(target_tuple))
    current_tuple += (0,) * (max_len - len(current_tuple))
    target_tuple += (0,) * (max_len - len(target_tuple))
    
    return current_tuple < target_tuple

def check_and_upgrade_pip():
    """检查并升级pip"""
    try:
        current_version = get_current_pip_version()
        
        if current_version and is_version_less_than(current_version, "25.2"):
            print("=" * 50)
            print(f"检测到pip版本较旧 (当前: {current_version})")
            print("建议升级到最新版本以避免兼容性问题")
            print("=" * 50)
            
            # 询问用户是否升级
            try:
                choice = input("是否升级pip? (y/n, 默认n): ").lower()
                if choice == 'y':
                    print("正在升级pip...")
                    subprocess.check_call([
                        sys.executable, "-m", "pip", "install", "--upgrade", "pip"
                    ])
                    print("pip升级成功！")
                    print("请重新运行启动脚本")
                    sys.exit(0)
                else:
                    print("已选择不升级pip，继续启动应用...")
            except KeyboardInterrupt:
                print("\n已取消pip升级")
            except subprocess.CalledProcessError:
                print("pip升级失败，继续启动应用...")
    except Exception:
        # 任何错误都继续启动应用
        pass

def main():
    """主函数"""
    print("=" * 50)
    print("SQL管理工具 - 极简版本")
    print("=" * 50)
    
    # 检查并升级pip
    check_and_upgrade_pip()
    
    # 初始化数据库
    print("正在初始化数据库...")
    init_db()
    
    # 启动服务器
    print(f"服务器正在启动，端口: {PORT}")
    print(f"请访问: http://localhost:{PORT}")
    print("按 Ctrl+C 停止服务器")
    
    try:
        server = HTTPServer(('', PORT), SQLManagerHandler)
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n服务器已停止")
        server.server_close()

if __name__ == "__main__":
    main()
