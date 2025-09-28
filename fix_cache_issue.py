#!/usr/bin/env python3
"""
修复HTTP 304响应问题
添加缓存控制头，防止浏览器缓存导致的页面不更新问题
"""

import os
import fileinput

def fix_app_py():
    """修复app.py文件，添加缓存控制"""
    app_file = "sql-manager-backend/app.py"
    
    if not os.path.exists(app_file):
        print(f"错误: {app_file} 文件不存在")
        return False
    
    print(f"正在修复 {app_file}...")
    
    # 读取文件内容
    with open(app_file, 'r') as f:
        content = f.read()
    
    # 检查是否已经添加了缓存控制代码
    if 'from flask import make_response' in content:
        print("缓存控制代码已存在，无需修改")
        return True
    
    # 修改1: 添加make_response导入
    content_start = 'from flask import Flask, request, jsonify, send_from_directory'
    import_end = 'from flask import Flask, request, jsonify, send_from_directory, make_response'
    
    # 修改2: 添加缓存控制装饰器
    cache_decorator = '''
# 缓存控制装饰器
def no_cache(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        response = make_response(f(*args, **kwargs))
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
        return response
    return decorated_function

'''
    
    # 修改3: 为静态文件路由添加缓存控制
    static_route_start = '@app.route(\'/<path:path>\')'
    static_route_end = '@app.route(\'/<path:path>\')\n@no_cache'
    
    # 应用修改
    content = content.replace(import_start, import_end)
    
    # 在路由定义前添加装饰器
    route_section_start = '# API路由'
    if route_section_start in content:
        content = content.replace(route_section_start, cache_decorator + route_section_start)
    else:
        # 如果找不到API路由标记，在文件开头添加
        content = cache_decorator + content
    
    # 为静态文件路由添加装饰器
    content = content.replace(static_route_start, static_route_end)
    
    # 为index路由添加装饰器
    index_route_start = '@app.route(\'/\')'
    index_route_end = '@app.route(\'/\')\n@no_cache'
    content = content.replace(index_route_start, index_route_end)
    
    # 保存修改
    with open(app_file, 'w') as f:
        f.write(content)
    
    print(f"{app_file} 修复完成")
    return True

def fix_index_html():
    """修复index.html文件，添加版本参数"""
    html_file = "sql-manager/index.html"
    
    if not os.path.exists(html_file):
        print(f"错误: {html_file} 文件不存在")
        return False
    
    print(f"正在修复 {html_file}...")
    
    # 读取文件内容
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 生成版本号（使用文件修改时间）
    import time
    version = str(int(os.path.getmtime(html_file)))
    
    # 为所有外部资源添加版本参数
    # 匹配CSS和JS文件
    import re
    
    # 修复CSS链接
    content = re.sub(
        r'(<link\s+[^>]*href\s*=\s*["\'])([^"\']+\.(css|js))(["\'])',
        r'\1\2?v=' + version + r'\4',
        content
    )
    
    # 修复Script标签
    content = re.sub(
        r'(<script\s+[^>]*src\s*=\s*["\'])([^"\']+\.js)(["\'])',
        r'\1\2?v=' + version + r'\3',
        content
    )
    
    # 保存修改
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"{html_file} 修复完成")
    return True

def create_nocache_middleware():
    """创建NoCache中间件"""
    middleware_file = "sql-manager-backend/nocache_middleware.py"
    
    if os.path.exists(middleware_file):
        print(f"{middleware_file} 已存在，跳过创建")
        return True
    
    middleware_content = '''
"""
NoCache中间件
防止浏览器缓存静态文件
"""

from flask import make_response
from functools import wraps

def nocache_middleware(app):
    """为应用添加NoCache中间件"""
    
    @app.after_request
    def add_nocache_headers(response):
        """为所有响应添加NoCache头"""
        # 只对HTML和静态文件添加NoCache头
        if response.content_type and (
            'text/html' in response.content_type or
            'text/css' in response.content_type or
            'application/javascript' in response.content_type or
            'image/' in response.content_type
        ):
            response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '-1'
        
        return response
    
    return app
'''
    
    with open(middleware_file, 'w') as f:
        f.write(middleware_content)
    
    print(f"{middleware_file} 创建完成")
    
    # 更新app.py以使用中间件
    app_file = "sql-manager-backend/app.py"
    if os.path.exists(app_file):
        with open(app_file, 'r') as f:
            content = f.read()
        
        # 添加导入
        if 'from nocache_middleware import nocache_middleware' not in content:
            content = content.replace(
                'app = Flask(__name__, static_folder=\'../sql-manager\', static_url_path=\'\')',
                'app = Flask(__name__, static_folder=\'../sql-manager\', static_url_path=\'\')\nfrom nocache_middleware import nocache_middleware\napp = nocache_middleware(app)'
            )
            
            with open(app_file, 'w') as f:
                f.write(content)
            
            print(f"{app_file} 更新为使用NoCache中间件")
    
    return True

def main():
    print("=" * 60)
    print("修复HTTP 304响应问题")
    print("=" * 60)
    
    print("\n1. 修复app.py文件，添加缓存控制...")
    fix_app_py()
    
    print("\n2. 修复index.html文件，添加版本参数...")
    fix_index_html()
    
    print("\n3. 创建NoCache中间件...")
    create_nocache_middleware()
    
    print("\n" + "=" * 60)
    print("修复完成！")
    print("\n更新内容：")
    print("- 为所有路由添加了NoCache头")
    print("- 为静态文件添加了版本参数")
    print("- 创建了NoCache中间件确保浏览器不缓存")
    print("\n请重新启动应用程序以应用更改。")
    print("=" * 60)

if __name__ == "__main__":
    main()
