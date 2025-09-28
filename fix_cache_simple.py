#!/usr/bin/env python3
"""
简化HTTP 304响应问题 - 简化版
使用更简单的方法添加缓存控制
避免

import os
import sys

def read_file_safe(file_path):
    """安全读取文件，尝试不同编码"""
    encodings = ['utf-8', 'gbk', 'gb2312', 'latin-1']
    
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read(), encoding
        except UnicodeDecodeError:
            continue
    
    print(f"错误: 无法读取文件 {file_path}")
    return None, None

def write_file_safe(file_path, content, original_encoding=None):
    """安全写入文件"""
    try:
        # 尝试使用原始编码
        if original_encoding:
            with open(file_path, 'w', encoding=original_encoding) as f:
                f.write(content)
            return True
    except:
        pass
    
    # 尝试使用UTF-8
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"使用UTF-8编码保存文件 {file_path}")
        return True
    except Exception as e:
        print(f"保存文件 {file_path} 失败: {e}")
        return False

def add_nocache_middleware():
    """添加NoCache中间件到app.py"""
    app_file = "sql-manager-backend/app.py"
    
    if not os.path.exists(app_file):
        print(f"错误: {app_file} 文件不存在")
        return False
    
    print(f"正在更新 {app_file}...")
    
    # 读取文件
    content, encoding = read_file_safe(app_file)
    
    if content is None:
        return False
    
    # 检查是否已经添加了中间件
    if 'nocache_middleware' in content:
        print("中间件已经已经存在，跳过")
        return True
    
    # 创建中间件代码
    middleware_code = '''
# 缓存控制中间件
from flask import make_response

@app.after_request
def add_nocache_headers(response):
    """为所有响应添加NoCache头"""
    # 只HTML和静态文件添加NoCache头
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

'''
    
    # 在app.run之前添加中间件
    run_pattern = 'if __name__ == \'__main__\''
    if run_pattern in content:
        # 分割内容
        parts = content.split(run_pattern)
        if len(parts) >= 2:
            # 在run之前添加中间件代码
            new_content = parts[0] + middleware_code + run_pattern + parts[1]
            
            # 保存文件
            if write_file_safe(app_file, new_content, encoding):
                print(f"{app_file} 更新完成")
                return True
    else:
        # 如果找不到run模式，在文件末尾添加
        new_content = content + '\n\n' + middleware_code
        
        if write_file_safe(app_file, new_content, encoding):
            print(f"{app_file} 更新完成")
            return True
    
    return False

def add_version_to_html():
    """为HTML中的静态资源添加版本参数"""
    html_file = "sql-manager/index.html"
    
    if not os.path.exists(html_file):
        print(f"错误: {html_file} 文件不存在")
        return False
    
    print(f"正在更新 {html_file}...")
    
    # 读取文件
    content, encoding = read_file_safe(html_file)
    
    if content is None:
        return False
    
    # 检查是否已经添加了版本参数
    if '?v=' in content:
        print("版本参数已经存在，跳过")
        return True
    
    # 生成简单的版本号（使用当前时间）
    import time
    version = str(int(time.time()))
    
    # 简单替换：为所有.css和.js文件添加版本参数
    # 使用更简单的字符串替换，避免复杂的正则表达式
    new_content = content.replace('.css"', f'.css?v={version}"')
    new_content = new_content.replace('.js"', f'.js?v={version}"')
    new_content = new_content.replace('.css\'', f'.css?v={version}\'')
    new_content = new_content.replace('.js\'', f'.js?v={version}\'')
    
    if new_content != content:
        if write_file_safe(html_file, new_content, encoding):
            print(f"{html_file} 更新完成")
            return True
    else:
        print("未找到需要更新的静态资源链接")
        return True
    
    return False

def main():
    print("=" * 60)
    print("修复HTTP 304响应问题 - 简化版")
    print("=" * 60)
    
    # 检查Python版本
    if sys.version_info < (3, 6):
        print("错误: 需要Python 3.6或更高版本")
        sys.exit(1)
    
    print("\n1. 为app.py添加缓存控制中间件...")
    success1 = add_nocache_middleware()
    
    print("\n2. 为HTML静态资源添加版本参数...")
    success2 = add_version_to_html()
    
    print("\n" + "=" * 60)
    
    if success1 or success2:
        print("修复完成！")
        print("\n更新内容：")
        print("- 为所有响应添加了NoCache头，防止浏览器缓存")
        print("- 为HTML中的CSS/JS文件添加了版本参数")
        print("\n请重新启动应用程序以应用更改：")
        print("  cd sql-manager-backend")
        print("  python app.py")
    else:
        print("没有进行任何更新")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
