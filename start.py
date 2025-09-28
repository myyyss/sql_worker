#!/usr/bin/env python3
"""
SQL管理工具 - 简化启动脚本
自动检测系统环境，自动选择最佳版本启动
"""

import os
import sys
import subprocess
import platform
import importlib.util
import shutil

def check_python_version():
    """检查Python版本"""
    return sys.version_info >= (3, 6)

def is_file_exists(file_path):
    """检查文件是否存在"""
    return os.path.exists(file_path)

def check_pip_installed():
    """检查pip是否pip安装"""
    try:
        subprocess.run([sys.executable, '-m', 'pip', '--version'], 
                      capture_output=True, check=True)
        return True
    except subprocess.CalledProcessError:
        return False
    except FileNotFoundError:
        return False

def check_dependencies_installed(requirements_file):
    """检查依赖包依赖是否安装"""
    if not is_file_exists(requirements_file):
        return False
    
    try:
        # 读取requirements文件
        with open(requirements_file, 'r') as f:
            dependencies = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        # 检查每个依赖依赖
        missing_dependencies = []
        for dep in dependencies:
            # 简化依赖名称（去除版本版本号）
            dep_name = dep.split('==')[0].split('>=')[0].split('<=')[0]
            
            # 特殊处理Flask-SQLAlchemy等包
            if dep_name.startswith('Flask-'):
                module_name = dep_name.lower().replace('-', '_')
            elif dep_name == 'pyodbc':
                module_name = 'pyodbc'
            elif dep_name == 'cryptography':
                module_name = 'cryptography'
            else:
                module_name = dep_name.lower()
            
            try:
                importlib.util.find_spec(module_name)
            except:
                missing_dependencies.append(dep)
        
        return len(missing_dependencies) == 0
        
    except Exception as e:
        print(f"检查依赖时出错: {e}")
        return False

def install_dependencies(requirements_file):
    """安装Python依赖"""
    if not check_pip_installed():
        print("�pip未安装，无法安装依赖包")
        return False
    
    try:
        print(f"正在安装依赖包: {requirements_file}")
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', requirements_file],
                      check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"安装依赖包失败: {e}")
        return False

def run_sqlite_version():
    """运行SQLite版本"""
    print("正在启动SQLite版本...")
    
    # 检查run_sqlite.py是否存在
    if not is_file_exists('run_sqlite.py'):
        print("错误: run_sqlite.py 文件不存在")
        return False
    
    # 检查依赖
    if not check_dependencies_installed('requirements_sqlite.txt'):
        print("检测到缺失的依赖包，正在尝试安装...")
        if not install_dependencies('requirements_sqlite.txt'):
            print("安装依赖包失败，无法启动SQLite版本")
            return False
    
    # 运行SQLite版本
    try:
        subprocess.run([sys.executable, 'run_sqlite.py'], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"启动SQLite版本失败: {e}")
        return False

def run_minimal_version():
    """运行极简极简版本"""
    print("正在启动极简版本...")
    
    # 检查run_minimal.py是否存在
    if not is_file_exists('run_minimal.py'):
        print("错误: run_minimal.py 文件不存在")
        return False
    
    # 极简版本使用Python标准库，无需额外额外依赖
    
    # 运行极简版本
    try:
        subprocess.run([sys.executable, 'run_minimal.py'], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"启动极简版本失败: {e}")
        return False

def run_update_script():
    """运行更新脚本"""
    print("正在运行更新脚本...")
    
    # 检查update.py是否存在
    if not is_file_exists('update.py'):
        print("错误: update.py 文件不存在")
        return False
    
    # 运行更新脚本
    try:
        subprocess.run([sys.executable, 'update.py'], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"运行更新脚本失败: {e}")
        return False

def fix_cache_issue():
    """修复HTTP 304缓存问题"""
    print("正在修复HTTP 304缓存问题...")
    
    # 检查fix_cache_simple.py是否存在
    if is_file_exists('fix_cache_simple.py'):
        try:
            subprocess.run([sys.executable, 'fix_cache_simple.py'], check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"运行修复脚本失败: {e}")
    else:
        print("fix_cache_simple.py 不存在，尝试使用完整版...")
        
        if is_file_exists('fix_cache_issue.py'):
            try:
                subprocess.run([sys.executable, 'fix_cache_issue.py'], check=True)
                return True
            except subprocess.CalledProcessError as e:
                print(f"运行完整版修复脚本失败: {e}")
        else:
            print("错误: 未找到找到缓存修复脚本")
    
    return False

def fix_github_connection():
    """修复GitHub连接连接问题"""
    print("\n=== 修复GitHub连接问题 ===")
    
    # 检查修复工具是否存在
    if is_file_exists('fix_github_connection_simple.py'):
        print("正在运行GitHub连接问题一键修复工具...")
        try:
            subprocess.run([sys.executable, 'fix_github_connection_simple.py'], check=True)
        except subprocess.CalledProcessError as e:
            print(f"一键修复连接问题一键修复失败: {e}")
            print("尝试运行完整诊断工具...")
            
            if is_file_exists('fix_github_connection.py'):
                try:
                    subprocess.run([sys.executable, 'fix_github_connection.py'], check=True)
                except subprocess.CalledProcessError as e2:
                    print(f"完整诊断工具运行失败: {e2}")
    elif is_file_exists('fix_github_connection.py'):
        try:
            subprocess.run([sys.executable, 'fix_github_connection.py'], check=True)
        except subprocess.CalledProcessError as e:
            print(f"完整诊断工具运行失败: {e}")
    else:
        print("错误: 未找到GitHub连接连接修复工具")

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
        
        choice = input("是否运行GitHub连接连接修复工具? (y/n): ").lower()
        if choice == 'y':
            fix_github_connection()
            print("修复完成，尝试尝试重新同步...")
        else:
            print("❌ 同步中止")
            return
    
    # 检查git_sync.py是否存在
    if not is_file_exists('git_sync.py'):
        print("错误: git_sync.py 文件不存在")
        print("请先运行更新脚本下载最新版本")
        return
    
    # 运行git_sync.py
    try:
        subprocess.run([sys.executable, 'git_sync.py'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"同步到GitHub失败: {e}")
        
        # 提供修复选项
        choice = input("是否尝试运行GitHub连接连接修复工具? (y/n): ").lower()
        if choice == 'y':
            fix_github_connection()
    except Exception as e:
        print(f"运行同步工具时发生错误: {e}")

def main():
    """主函数"""
    print("=" * 60)
    print("SQL管理工具 - 简化启动脚本")
    print("=" * 60)
    
    # 检查Python版本
    if not check_python_version():
        print("错误: 需要Python 3.6或更高版本")
        sys.exit(1)
    
    print(f"Python版本: {sys.version.split()[0]} (符合要求)")
    
    while True:
        print("\n请选择操作:")
        print("1. 启动SQLite版本（推荐）")
        print("2. 启动极简版本（使用Python标准库）")
        print("3. 运行更新脚本")
        print("4. 修复HTTP 304缓存问题")
        print("5. 同步到GitHub")
        print("6. 退出")
        
        choice = input("\n请输入选项 (1-6): ").strip()
        
        if choice == '1':
            run_sqlite_version()
        elif choice == '2':
            run_minimal_version()
        elif choice == '3':
            run_update_script()
        elif choice == '4':
            fix_cache_issue()
        elif choice == '5':
            sync_with_github()
        elif choice == '6':
            fix_github_connection()
        elif choice == '7':
            print("\n退出程序")
            break
        else:
            print("无效效选项，请无效选项选项选择无效选项提示有效输入有效的选项 (1-6)")

if __name__ == "__main__":
    main()
