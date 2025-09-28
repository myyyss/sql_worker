#!//bin#!//env python3
"""
测试HTTP缓存问题修复
验证HTTP请求并验证缓存控制头是否是否正确设置
"""

import requests
import time
import sys

def test_cache_headers(url):
    """测试缓存控制头"""
    print(f"测试 {url} 的缓存控制头...")
    
    try:
        # 第一次请求
        response = requests.get(url)
        
        print(f"状态码: {response.status_code}")
        print(f"响应头:")
        for key, value in response.headers.items():
            if key.lower() in ['cache-control', 'pragma', 'expires']:
                print(f"  {key}: {value}")
        
        # 检查是否包含缓存控制头
        cache_control = response.headers.get('Cache-Control', '')
        pragma = response.headers.get('Pragma', '')
        expires = response.headers.get('Expires', '')
        
        print(f"\n缓存控制检查:")
        if 'no-store' in cache_control and 'no-cache' in cache_control:
            print("✓ Cache-Control头正确设置为no-store, no-cache")
        else:
            print("✗ Cache-Control头设置不正确")
            print(f"  实际值: {cache_control}")
        
        if pragma == 'no-cache':
            print("✓ Pragma头正确设置为no-cache")
        else:
            print("✗ Pragma头设置不正确")
            print(f"  实际值: {pragma}")
        
        if expires == '-1' or expires == '0':
            print("✓ Expires头设置为立即")
        else:
            print("✗ Expires头设置不正确")
            print(f"  实际值: {expires}")
        
        return True
        
    except Exception as e:
        print(f"测试失败: {str(e)}")
        return False

def test_static_files(url):
    """测试静态文件缓存"""
    print(f"\n测试静态文件缓存...")
    
    static_files = [
        '/index.html',
        '/',
    ]
    
    all_passed = True
    
    for path in static_files:
        print(f"\n测试 {path}:")
        full_url = url + path
        
        try:
            # 第一次请求
            response1 = requests.get(full_url)
            etag1 = response1.headers.get('ETag')
            last_modified1 = response1.headers.get('Last-Modified')
            
            print(f"  状态码: {response1.status_code}")
            print(f"  ETag: {etag1}")
            print(f"  Last-Modified: {last_modified1}")
            
            # 等待1秒
            time.sleep(1)
            
            # 第二次请求（应该不会缓存）
            response2 = requests.get(full_url)
            status_code2 = response2.status_code
            
            print(f"  第二次请求状态码: {status_code2}")
            
            # 检查是否返回304（如果返回304表示缓存生效，这是我们不想要的）
            if status_code2 == 304:
                print("  ✗ 警告: 服务器返回304，缓存仍然生效")
                all_passed = False
            elif status_code2 == 200:
                print("  ✓ 成功: 服务器返回200，缓存已生效")
            else:
                print(f"  ? 未知状态码: {status_code2}")
                
        except Exception as e:
            print(f"  测试失败: {str(e)}")
            all_passed = False
    
    return all_passed

def test_version_parameters():
    """测试HTML文件中的版本参数"""
    print(f"\n测试HTML文件中的版本参数...")
    
    html_file = "sql-manager/index.html"
    
    if not os.path.exists(html_file):
        print(f"✗ 错误: {html_file} 文件不存在")
        return False
    
    try:
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否包含版本参数
        import re
        
        # 检查CSS和JS文件是否有?v=参数
        css_matches = re.findall(r'<link\s+[^>]*href\s*=\s*["\'].*?\.css\?v=\d+["\']', content)
        js_matches = re.findall(r'<script\s+[^>]*src\s*=\s*["\'].*?\.js\?v=\d+["\']', content)
        
        print(f"  带版本参数的CSS文件: {len(css_matches)}")
        print(f"  带版本参数的JS文件: {len(js_matches)}")
        
        if len(css_matches) > 0 and len(js_matches) > 0:
            print("  ✓ 成功: HTML文件已添加版本参数")
            return True
        else:
            print("  ✗ 失败: HTML文件未添加版本参数")
            
            # 显示一些示例
            print(f"\n  示例CSS链接:")
            css_samples = re.findall(r'<link\s+[^>]*href\s*=\s*["\'].*?\.css["\']', content)[:3]
            for sample in css_samples:
                print(f"    {sample}")
            
            print(f"\n  示例JS链接:")
            js_samples = re.findall(r'<script\s+[^>]*src\s*=\s*["\'].*?\.js["\']', content)[:3]
            for sample in js_samples:
                print(f"    {sample}")
            
            return False
            
    except Exception as e:
        print(f"✗ 测试失败: {str(e)}")
        return False

def main():
    print("=" * 60)
    print("测试HTTP 304缓存问题修复")
    print("=" * 60)
    
    # 检查应用是否应用是否正在运行
    print("\n1. 检查应用状态...")
    
    url = "http://localhost:5000"
    
    try:
        response = requests.get(url, timeout=5)
        print(f"✓ 应用正在运行")
    except requests.exceptions.ConnectionError:
        print("✗ 应用未运行！")
        print("\n请先启动应用程序:")
        print("  cd sql-manager-backend")
        print("  python app.py")
        print("\n或者重新运行测试脚本。")
        sys.exit(1)
    
    # 测试缓存控制头
    print("\n2. 测试缓存控制头...")
    test_cache_headers(url)
    
    # 测试静态文件缓存
    print("\n3. 测试静态文件缓存...")
    test_static_files(url)
    
    # 测试HTML文件版本参数
    print("\n4. 测试HTML文件版本参数...")
    test_version_parameters()
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("\n总结:")
    print("- 如果应用应该返回200状态码，而不是304")
    print("- 响应头应该包含Cache-Control: no-store, no-cache")
    print("- HTML头文件应该包含版本参数(?v=xxx)")
    print("- 浏览器应该缓存页面，每次次请求都是最新版本")
    print("=" * 60)

if __name__ == "__main__":
    main()
