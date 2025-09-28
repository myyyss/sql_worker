#!/usr/bin/env python3
"""
SQL管理工具 - 更新脚本
提供多种更新选项，解决依赖问题
"""

import os
import sys
import subprocess
import json
import shutil
import platform

def get_python_executable():
    """获取Python可执行文件路径"""
    return sys.executable

def run_command(command, description="执行命令"):
    """运行系统命令"""
    print(f"\n{description}: {' '.join(command)}")
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True
        )
        print(f"成功: {result.stdout}")
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        print(f"失败: {e.stderr}")
        return False, e.stderr
    except Exception as e:
        print(f"错误: {str(e)}")
        return False, str(e)

def backup_database():
    """备份数据库文件"""
    print("\n=== 备份数据库 ===")
    
    databases = [
        ('sql-manager-backend/sql_manager.db', 'sql_manager_backup.db'),
        ('sql_manager_minimal.db', 'sql_manager_minimal_backup.db')
    ]
    
    for src, dest in databases:
        if os.path.exists(src):
            try:
                shutil.copy2(src, dest)
                print(f"已备份: {src} -> {dest}")
            except Exception as e:
                print(f"备份失败 {src}: {str(e)}")
        else:
            print(f"数据库文件不存在: {src}")

def update_dependencies():
    """更新依赖包"""
    print("\n=== 更新依赖包 ===")
    
    options = [
        ("requirements_sqlite.txt", "SQLite版本（推荐，无pyodbc依赖）"),
        ("requirements_compatible.txt", "兼容版本（解决版本冲突）"),
        ("requirements_minimal.txt", "极简版本（仅PyJWT）"),
        ("requirements_new.txt", "UTF-8编码版本（解决编码问题）"),
        ("requirements.txt", "原始版本")
    ]
    
    print("请选择要使用的requirements文件:")
    for i, (file, desc) in enumerate(options, 1):
        print(f"{i}. {file} - {desc}")
    
    choice = input("\n请输入选项 (1-5): ").strip()
    
    try:
        index = int(choice) - 1
        if 0 <= index < len(options):
            req_file = options[index][0]
            
            if not os.path.exists(req_file):
                print(f"错误: 文件 {req_file} 不存在")
                return False
            
            print(f"\n正在使用 {req_file} 更新依赖...")
            
            # 升级pip
            print("\n1. 升级pip到最新版本")
            success, _ = run_command([
                get_python_executable(), "-m", "pip", "install", "--upgrade", "pip"
            ], "升级pip")
            
            # 安装依赖
            print(f"\n2. 安装依赖包 ({req_file})")
            success, _ = run_command([
                get_python_executable(), "-m", "pip", "install", "-r", req_file
            ], f"安装依赖 {req_file}")
            
            if success:
                print("\n依赖包更新完成！")
                return True
            else:
                print("\n依赖包更新失败，请检查错误信息")
                return False
        else:
            print("无效选项")
            return False
    except ValueError:
        print("无效输入，请输入数字")
        return False

def update_to_latest_version():
    """更新到最新版本"""
    print("\n=== 更新到最新版本 ===")
    
    # 检查是否有git
    try:
        subprocess.run(['git', '--version'], capture_output=True, text=True, check=True)
        has_git = True
    except:
        has_git = False
    
    if has_git:
        print("使用git更新...")
        
        # 检查是否在git仓库中
        if os.path.exists('.git'):
            print("1. 拉取最新代码")
            success, output = run_command(['git', 'pull'], "拉取最新代码")
            
            if success:
                print("2. 更新依赖包")
                return update_dependencies()
            else:
                print("拉取代码失败，是否继续更新依赖?")
                choice = input("继续? (y/n): ").lower()
                if choice == 'y':
                    return update_dependencies()
                else:
                    return False
        else:
            print("当前目录不是git仓库，无法使用git更新")
            print("请手动下载最新版本或使用其他更新方式")
            return False
    else:
        print("未安装git，无法自动更新代码")
        print("请手动下载最新版本或安装git")
        return False

def fix_frontend_issues():
    """修复前端问题"""
    print("\n=== 修复前端问题 ===")
    
    frontend_file = "sql-manager/index.html"
    
    if not os.path.exists(frontend_file):
        print(f"错误: 前端文件 {frontend_file} 不存在")
        return False
    
    try:
        # 读取文件
        with open(frontend_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 修复1: 移除事件监听器上错误的catch语句
        # 错误模式: .addEventListener('click', () => {}).catch(...)
        import re
        
        # 修复事件监听器后的错误catch语句
        content = re.sub(
            r'\.addEventListener\((.*?)\)\.catch\(function\(error\)\s*\{[^}]*\}\)',
            r'.addEventListener(\1)',
            content,
            flags=re.DOTALL
        )
        
        # 修复2: 确保auth-modal在页面加载时显示
        # 在initialize函数中添加showAuthModal()调用
        if 'function initialize() {' in content and 'showAuthModal();' not in content:
            # 在initEventListeners()后添加
            content = content.replace(
                '    // 初始化事件监听\n    initEventListeners();\n',
                '    // 初始化事件监听\n    initEventListeners();\n    \n    // 显示登录模态框\n    showAuthModal();\n'
            )
        
        # 修复3: 确保用户菜单在未登录时显示登录按钮
        # 找到用户菜单的HTML并修改
        content = content.replace(
            '<button id="user-menu" class="hidden flex items-center space-x-2 text-white hover:text-gray-300 transition-all-200">',
            '<button id="user-menu" class="flex items-center space-x-2 text-white hover:text-gray-300 transition-all-200">'
        )
        
        # 保存修改
        with open(frontend_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("前端问题修复完成！")
        return True
        
    except Exception as e:
        print(f"修复前端问题失败: {str(e)}")
        return False

def switch_between_versions():
    """版本切换"""
    print("\n=== 版本切换 ===")
    
    options = [
        ("run_sqlite.py", "SQLite版本（使用Flask，推荐）"),
        ("run_minimal.py", "极简版本（使用Python标准库）"),
        ("run_simple.py", "简单版本"),
        ("run.py", "原始版本")
    ]
    
    print("请选择要使用的版本:")
    for i, (script, desc) in enumerate(options, 1):
        exists = "✓" if os.path.exists(script) else "✗"
        print(f"{i}. {script} - {desc} {exists}")
    
    choice = input("\n请输入选项 (1-4): ").strip()
    
    try:
        index = int(choice) - 1
        if 0 <= index < len(options):
            script, desc = options[index]
            
            if not os.path.exists(script):
                print(f"错误: 启动脚本 {script} 不存在")
                return False
            
            print(f"\n已选择: {desc}")
            print(f"启动命令: python {script}")
            
            # 创建快捷方式
            if os.path.exists('run_current.py'):
                os.remove('run_current.py')
            
            # 创建符号链接或复制文件
            if platform.system() == 'Windows':
                # Windows不支持符号链接，使用复制
                shutil.copy2(script, 'run_current.py')
            else:
                # Unix系统使用符号链接
                os.symlink(script, 'run_current.py')
            
            print(f"\n已创建快捷方式: run_current.py -> {script}")
            print(f"现在可以使用: python run_current.py 启动应用")
            
            return True
        else:
            print("无效选项")
            return False
    except ValueError:
        print("无效输入，请输入数字")
        return False

def fix_github_connection():
    """修复GitHub连接连接问题"""
    print("\n=== 修复GitHub连接问题 ===")
    
    # 检查修复工具是否存在
    if os.path.exists('fix_github_connection_simple.py'):
        print("正在运行GitHub连接问题一键修复工具...")
        try:
            subprocess.run([get_python_executable(), 'fix_github_connection_simple.py'], check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"一键修复连接问题一键修复失败: {e}")
            print("尝试运行完整诊断工具...")
    
    if os.path.exists('fix_github_connection.py'):
        try:
            subprocess.run([get_python_executable(), 'fix_github_connection.py'], check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"GitHub连接问题完整诊断工具运行失败: {e}")
    
    print("错误: 未找到GitHub连接连接修复工具")
    return False

def sync_with_github():
    """同步到GitHub"""
    print("\n=== 同步到GitHub ===")
    
    # 先检查网络连接
    try:
        import socket
        socket.create_connection(("github.com", 443), timeout=10)
    except Exception as e:
        print(f"⚠️  GitHub连接测试失败: {e}")
        print("建议尝试修复连接问题...")
        
        if fix_github_connection():
            print("尝试尝试重新同步...")
        else:
            print("❌ 无法修复GitHub连接问题，同步中止")
            return False
    
    # 检查git_sync.py是否存在
    if not os.path.exists('git_sync.py'):
        print("错误: git_sync.py 文件不存在")
        print("请先运行 update.py 下载最新版本的同步工具")
        return False
    
    # 运行git_sync.py
    try:
        subprocess.run([get_python_executable(), 'git_sync.py'], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"同步到GitHub失败: {e}")
        
        # 提供修复选项
        choice = input("是否尝试运行GitHub连接连接修复工具? (y/n): ").lower()
        if choice == 'y':
            fix_github_connection()
        
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("SQL管理工具 - 更新脚本")
    print("=" * 60)
    
    print("\n请选择更新选项:")
    print("1. 备份数据库")
    print("2. 更新依赖包")
    print("3. 更新到最新版本（需要git）")
    print("4. 修复前端问题（按钮无响应、登录按钮不显示等）")
    print("5. 版本切换（完整版/极简版）")
    print("6. 同步到GitHub")
    print("7. 修复GitHub连接问题")
    print("8. 退出")
    
    while True:
        choice = input("\n请输入选项 (1-6): ").strip()
        
        if choice == '1':
            backup_database()
        elif choice == '2':
            update_dependencies()
        elif choice == '3':
            update_to_latest_version()
        elif choice == '4':
            fix_frontend_issues()
        elif choice == '5':
            switch_between_versions()
        elif choice == '6':
            sync_with_github()
        elif choice == '7':
            fix_github_connection()
        elif choice == '8':
            print("\n退出更新脚本")
            break
        else:
            print("无效选项，请重新输入")
        
        if choice in ['1', '2', '3', '4', '5']:
            print("\n" + "=" * 60)
            print("操作完成！")
            print("=" * 60)

if __name__ == "__main__":
    main()
