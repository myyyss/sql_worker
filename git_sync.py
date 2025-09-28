#!/usr/bin/env python3
"""
SQL管理工具 - GitHub同步工具
帮助用户将项目同步到GitHub仓库
"""

import os
import sys
import subprocess
import platform
import json

def check_git_installed():
    """检查Git是否安装"""
    try:
        result = subprocess.run(
            ['git', '--version'],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False

def get_git_config():
    """获取Git配置"""
    config = {}
    
    try:
        # 获取用户名
        user_name = subprocess.run(
            ['git', 'config', 'user.name'],
            capture_output=True,
            text=True
        ).stdout.strip()
        
        # 获取邮箱
        user_email = subprocess.run(
            ['git', 'config', 'user.email'],
            capture_output=True,
            text=True
        ).stdout.strip()
        
        config['user_name'] = user_name
        config['user_email'] = user_email
        
        return config
    except Exception as e:
        print(f"获取Git配置时出错: {e}")
        return config

def setup_git_config():
    """设置Git配置"""
    print("\n=== 设置Git用户信息 ===")
    
    name = input("请输入您的GitHub用户名: ").strip()
    email = input("请输入您的GitHub邮箱: ").strip()
    
    if not name or not email:
        print("用户名和邮箱不能为空")
        return False
    
    try:
        subprocess.run(['git', 'config', '--global', 'user.name', name], check=True)
        subprocess.run(['git', 'config', '--global', 'user.email', email], check=True)
        
        print("Git用户信息设置成功！")
        return True
    except subprocess.CalledProcessError as e:
        print(f"设置Git配置失败: {e}")
        return False

def initialize_git_repo():
    """初始化Git仓库"""
    print("\n=== 初始化Git仓库 ===")
    
    try:
        # 初始化仓库
        subprocess.run(['git', 'init'], check=True)
        print("Git仓库初始化成功")
        
        # 创建.gitignore文件
        create_gitignore()
        
        # 添加所有文件
        subprocess.run(['git', 'add', '.'], check=True)
        print("已添加所有文件到暂存区")
        
        # 第一次提交
        commit_message = "Initial commit - SQL管理工具"
        subprocess.run(['git', 'commit', '-m', commit_message], check=True)
        print(f"提交成功: {commit_message}")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"Git操作失败: {e}")
        return False

def create_gitignore():
    """创建.gitignore文件"""
    gitignore_content = '''# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
*.egg-info/
.installed.cfg
*.egg

# SQLite
*.db
*.sqlite3
*.db-journal

# 日志
*.log

# 缓存
__pycache__/
.pytest_cache/
.cache/

# 环境变量
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# IDE
.idea/
.vscode/
*.swp
*.swo

# 操作系统
.DS_Store
Thumbs.db

# 其他
*.zip
*.tar.gz
*.tar.bz2
*.tar.xz
'''
    
    with open('.gitignore', 'w') as f:
        f.write(gitignore_content)
    
    print(".gitignore文件创建成功")

def add_remote_repo():
    """添加远程仓库"""
    print("\n=== 添加远程GitHub仓库 ===")
    
    while True:
        repo_url = input("请输入您的GitHub仓库URL (例如: https://github.com/yourusername/yourrepo.git): ").strip()
        
        if not repo_url:
            print("仓库URL不能为空")
            continue
        
        # 验证URL格式
        if not (repo_url.startswith('https://github.com/') or repo_url.startswith('git@github.com:')):
            print("无效的GitHub仓库URL")
            continue
        
        try:
            # 检查是否已存在远程仓库
            result = subprocess.run(
                ['git', 'remote', 'get-url', 'origin'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                current_remote = result.stdout.strip()
                print(f"已存在远程仓库: {current_remote}")
                
                choice = input(f"是否要将远程仓库更改为 {repo_url}? (y/n): ").lower()
                if choice == 'y':
                    subprocess.run(['git', 'remote', 'set-url', 'origin', repo_url], check=True)
                    print(f"远程仓库已更新为: {repo_url}")
                else:
                    print("保持现有远程仓库")
            else:
                # 添加新的远程仓库
                subprocess.run(['git', 'remote', 'add', 'origin', repo_url], check=True)
                print(f"远程仓库添加成功: {repo_url}")
            
            return True
        except subprocess.CalledProcessError as e:
            print(f"添加远程仓库失败: {e}")
            
            # 尝试修复可能的问题
            try:
                subprocess.run(['git', 'remote', 'remove', 'origin'], capture_output=True)
                print("已移除现有远程仓库配置")
            except:
                pass
            
            retry = input("是否重试? (y/n): ").lower()
            if retry != 'y':
                return False

def push_to_github():
    """推送到GitHub"""
    print("\n=== 推送到GitHub ===")
    
    try:
        # 检查是否有远程仓库
        result = subprocess.run(
            ['git', 'remote', 'get-url', 'origin'],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print("未配置远程仓库，请先添加远程仓库")
            return False
        
        # 拉取最新代码（如果有）
        print("正在拉取远程仓库的最新代码...")
        pull_result = subprocess.run(
            ['git', 'pull', 'origin', 'main', '--allow-unrelated-histories'],
            capture_output=True,
            text=True
        )
        
        if pull_result.returncode != 0:
            print(f"拉取代码时出现问题: {pull_result.stderr}")
            print("这可能是因为远程仓库有不同的历史记录")
            
            choice = input("是否继续强制推送? (y/n): ").lower()
            if choice != 'y':
                return False
        
        # 推送代码
        print("正在推送到GitHub...")
        subprocess.run(['git', 'push', '-u', 'origin', 'main'], check=True)
        
        print("推送成功！")
        print("您的代码已成功同步到GitHub仓库")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"推送失败: {e}")
        print("错误详情:")
        print(e.stderr)
        
        # 提供常见问题解决方案
        print("\n常见问题解决方案:")
        print("1. 检查您的GitHub仓库URL是否正确")
        print("2. 确保您有权限访问该仓库")
        print("3. 检查您的网络连接")
        print("4. 如果使用HTTPS，请确保您的凭据正确")
        print("5. 如果使用SSH，请确保您的SSH密钥已添加到GitHub")
        
        return False

def update_code():
    """更新代码（拉取最新更改）"""
    print("\n=== 更新代码 ===")
    
    try:
        # 检查是否有远程仓库
        result = subprocess.run(
            ['git', 'remote', 'get-url', 'origin'],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print("未配置远程仓库")
            return False
        
        # 拉取最新代码
        print("正在拉取远程仓库的最新代码...")
        subprocess.run(['git', 'pull', 'origin', 'main'], check=True)
        
        print("代码更新成功！")
        return True
    except subprocess.CalledProcessError as e:
        print(f"更新代码失败: {e}")
        return False

def create_github_install_guide():
    """创建GitHub安装指南"""
    guide_content = '''# GitHub安装指南

## Windows系统

1. 下载Git for Windows:
   https://git-scm.com/download/win

2. 运行安装程序，按照默认设置安装

3. 安装完成后，打开Git Bash（可以在开始菜单中找到）

4. 在Git Bash中配置您的GitHub信息:
   ```bash
   git config --global user.name "您的GitHub用户名"
   git config --global user.email "您的GitHub邮箱"
   ```

## macOS系统

1. 使用Homebrew安装（推荐）:
   ```bash
   brew install git
   ```

2. 或者从官网下载:
   https://git-scm.com/download/mac

3. 配置您的GitHub信息:
   ```bash
   git config --global user.name "您的GitHub用户名"
   git config --global user.email "您的GitHub邮箱"
   ```

## Linux系统

### Ubuntu/Debian:
```bash
sudo apt update
sudo apt install git
```

### CentOS/RHEL:
```bash
sudo yum install git
```

### Fedora:
```bash
sudo dnf install git
```

### 配置GitHub信息:
```bash
git config --global user.name "您的GitHub用户名"
git config --global user.email "您的GitHub邮箱"
```

## 验证安装

安装完成后，运行以下命令验证:
```bash
git --version
```

您应该看到Git的版本信息。

## 创建GitHub仓库

1. 登录您的GitHub账号: https://github.com

2. 点击右上角的"+"图标，选择"New repository"

3. 填写仓库名称（例如: sql-manager）

4. 添加描述（可选）

5. 选择"Public"或"Private"

6. 不要勾选"Initialize this repository with a README"

7. 点击"Create repository"

8. 复制仓库URL（HTTPS或SSH）
'''
    
    with open('GITHUB_INSTALL_GUIDE.md', 'w') as f:
        f.write(guide_content)
    
    print("GitHub安装指南已创建: GITHUB_INSTALL_GUIDE.md")

def main():
    """主函数"""
    print("=" * 60)
    print("SQL管理工具 - GitHub同步工具")
    print("=" * 60)
    
    # 检查Git是否安装
    if not check_git_installed():
        print("\n错误: 未安装Git！")
        print("\n请先安装Git，然后再运行此脚本。")
        
        # 创建安装指南
        create_github_install_guide()
        
        print("\n您可以参考以下资源安装Git:")
        print("1. 官方网站: https://git-scm.com/downloads")
        print("2. 我们已为您创建了详细的安装指南: GITHUB_INSTALL_GUIDE.md")
        
        sys.exit(1)
    
    print("\nGit已安装，继续操作...")
    
    # 获取Git配置
    git_config = get_git_config()
    
    # 检查Git配置
    if not git_config.get('user_name') or not git_config.get('user_email'):
        print("\nGit用户信息未配置")
        choice = input("是否现在配置? (y/n): ").lower()
        
        if choice == 'y':
            if not setup_git_config():
                print("Git配置失败，无法继续")
                sys.exit(1)
        else:
            print("Git配置是必需的，请重新运行脚本并配置")
            sys.exit(1)
    
    # 检查是否是Git仓库
    if not os.path.exists('.git'):
        print("\n当前目录不是Git仓库")
        choice = input("是否初始化新的Git仓库? (y/n): ").lower()
        
        if choice == 'y':
            if not initialize_git_repo():
                print("初始化Git仓库失败")
                sys.exit(1)
        else:
            print("操作取消")
            sys.exit(0)
    
    # 主菜单
    while True:
        print("\n" + "=" * 60)
        print("请选择操作:")
        print("1. 推送到GitHub（更新代码）")
        print("2. 从GitHub拉取最新代码")
        print("3. 添加/更改远程GitHub仓库")
        print("4. 查看Git状态")
        print("5. 退出")
        
        choice = input("\n请输入选项 (1-5): ").strip()
        
        if choice == '1':
            # 推送代码
            # 先检查是否有远程仓库
            result = subprocess.run(
                ['git', 'remote', 'get-url', 'origin'],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                print("未配置远程仓库，请先添加")
                if add_remote_repo():
                    push_to_github()
            else:
                # 检查是否有更改
                status_result = subprocess.run(
                    ['git', 'status', '--porcelain'],
                    capture_output=True,
                    text=True
                )
                
                if status_result.stdout.strip():
                    print("检测到代码更改，需要先提交")
                    
                    # 添加所有更改
                    subprocess.run(['git', 'add', '.'])
                    
                    # 提示输入提交信息
                    commit_msg = input("请输入提交信息: ").strip()
                    if not commit_msg:
                        commit_msg = "Update code"
                    
                    # 提交更改
                    try:
                        subprocess.run(['git', 'commit', '-m', commit_msg], check=True)
                        print(f"提交成功: {commit_msg}")
                    except subprocess.CalledProcessError as e:
                        print(f"提交失败: {e}")
                        continue
                
                # 推送代码
                push_to_github()
        
        elif choice == '2':
            # 拉取代码
            update_code()
        
        elif choice == '3':
            # 添加/更改远程仓库
            add_remote_repo()
        
        elif choice == '4':
            # 查看Git状态
            subprocess.run(['git', 'status'])
        
        elif choice == '5':
            # 退出
            print("\n感谢使用GitHub同步工具！")
            print("=" * 60)
            break
        
        else:
            print("无效选项，请重新输入")

if __name__ == "__main__":
    main()
