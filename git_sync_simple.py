#!/usr/bin/env python3
"""
SQL管理工具 - GitHub一键同步脚本
简化版同步工具，一键完成代码同步
"""

import os
import sys
import subprocess
import datetime

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

def is_git_repo():
    """检查是否是Git仓库"""
    return os.path.exists('.git')

def has_remote_repo():
    """检查是否配置了远程仓库"""
    try:
        result = subprocess.run(
            ['git', 'remote', 'get-url', 'origin'],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except:
        return False

def get_current_branch():
    """获取当前分支"""
    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            capture_output=True,
            text=True
        )
        return result.stdout.strip() if result.returncode == 0 else 'main'
    except:
        return 'main'

def sync_with_github():
    """同步到GitHub"""
    print("=" * 60)
    print("SQL管理工具 - GitHub一键同步")
    print("=" * 60)
    
    # 检查Git是否安装
    if not check_git_installed():
        print("\n❌ 错误: 未安装Git！")
        print("\n请先安装Git，然后再运行此脚本。")
        print("\n安装方法:")
        print("Windows: https://git-scm.com/download/win")
        print("macOS: brew install git 或 https://git-scm.com/download/mac")
        print("Linux: sudo apt install git (Ubuntu/Debian)")
        return False
    
    print("✅ Git已安装")
    
    # 检查是否是Git仓库
    if not is_git_repo():
        print("\n❌ 当前目录不是Git仓库")
        print("请先运行完整的同步工具进行初始化:")
        print("python git_sync.py")
        return False
    
    print("✅ 已检测到Git仓库")
    
    # 检查是否有远程仓库
    if not has_remote_repo():
        print("\n❌ 未配置远程GitHub仓库")
        print("请先运行完整的同步工具配置远程仓库:")
        print("python git_sync.py")
        return False
    
    print("✅ 已检测到远程仓库配置")
    
    current_branch = get_current_branch()
    print(f"✅ 当前分支: {current_branch}")
    
    try:
        # 拉取最新代码
        print("\n🔄 正在拉取远程仓库的最新代码...")
        pull_result = subprocess.run(
            ['git', 'pull', 'origin', current_branch],
            capture_output=True,
            text=True
        )
        
        if pull_result.returncode == 0:
            print("✅ 拉取成功")
            if "Already up to date" in pull_result.stdout:
                print("ℹ️  本地代码已是最新版本")
        else:
            print(f"⚠️  拉取时出现问题: {pull_result.stderr}")
            print("ℹ️  尝试使用--allow-unrelated-histories参数...")
            
            # 尝试使用允许不相关历史的拉取
            pull_result = subprocess.run(
                ['git', 'pull', 'origin', current_branch, '--allow-unrelated-histories'],
                capture_output=True,
                text=True
            )
            
            if pull_result.returncode != 0:
                print(f"❌ 拉取失败: {pull_result.stderr}")
                print("ℹ️  这可能是因为远程仓库有不同的历史记录")
                print("ℹ️  建议使用完整同步工具处理: python git_sync.py")
                return False
        
        # 检查是否有更改
        status_result = subprocess.run(
            ['git', 'status', '--porcelain'],
            capture_output=True,
            text=True
        )
        
        if status_result.stdout.strip():
            print("\n📝 检测到本地更改")
            
            # 添加所有更改
            print("🔍 正在添加更改...")
            subprocess.run(['git', 'add', '.'], capture_output=True)
            
            # 自动生成提交信息
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            commit_msg = f"Auto-sync at {timestamp}"
            
            # 提交更改
            print(f"💾 正在提交更改: {commit_msg}")
            commit_result = subprocess.run(
                ['git', 'commit', '-m', commit_msg],
                capture_output=True,
                text=True
            )
            
            if commit_result.returncode != 0:
                print(f"❌ 提交失败: {commit_result.stderr}")
                return False
            
            print("✅ 提交成功")
        else:
            print("\nℹ️  未检测到本地更改，无需提交")
        
        # 推送代码
        print("\n🚀 正在推送到GitHub...")
        push_result = subprocess.run(
            ['git', 'push', 'origin', current_branch],
            capture_output=True,
            text=True
        )
        
        if push_result.returncode == 0:
            print("✅ 推送成功！")
            print("\n🎉 项目已成功同步到GitHub")
            print(f"📅 同步时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            return True
        else:
            print(f"❌ 推送失败: {push_result.stderr}")
            
            # 尝试设置上游分支
            if "The current branch has no upstream branch" in push_result.stderr:
                print("ℹ️  正在设置上游分支...")
                push_result = subprocess.run(
                    ['git', 'push', '-u', 'origin', current_branch],
                    capture_output=True,
                    text=True
                )
                
                if push_result.returncode == 0:
                    print("✅ 推送成功！")
                    print("\n🎉 项目已成功同步到GitHub")
                    print(f"📅 同步时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    return True
                else:
                    print(f"❌ 设置上游分支后推送仍失败: {push_result.stderr}")
            
            return False
    
    except Exception as e:
        print(f"\n❌ 同步过程中发生错误: {e}")
        print("ℹ️  建议使用完整同步工具进行故障排除: python git_sync.py")
        return False

def main():
    """主函数"""
    success = sync_with_github()
    
    print("\n" + "=" * 60)
    
    if success:
        print("✅ GitHub同步完成！")
        print("ℹ️  您的代码已安全备份到GitHub")
        print("ℹ️  下次同步请直接运行: python git_sync_simple.py")
    else:
        print("❌ GitHub同步失败")
        print("ℹ️  请检查错误信息并尝试解决")
        print("ℹ️  或使用完整同步工具: python git_sync.py")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
