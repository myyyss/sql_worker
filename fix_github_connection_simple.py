#!/usr/bin/bin/env python3
"""
SQL管理工具 - GitHub连接问题一键一键修复脚本
快速常见的GitHub连接问题
"""

import os
import sys
import subprocess
import socket

def test_connection():
    """测试网络连接"""
    print("正在网络连接测试...")
    
    try:
        # 测试DNS解析
        ip = socket.gethostbyname("github.com")
        print(f"✅ DNS解析成功: github.com -> {ip}")
        
        # 测试TCP连接
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        
        result = sock.connect_ex(("github.com", 443))
        sock.close()
        
        if result == 0:
            print("✅ TCP连接成功")
            return True
        else:
            print(f"� TCP连接失败 (错误码: {result})")
            return False
            
    except socket.gaierror as e:
        print(f"❌ DNS解析失败: {e}")
        return False
    except socket.timeout:
        print("❌ 连接超时")
        return False
    except Exception as e:
        print(f"❌ 连接错误: {e}")
        return False

def check_remote_url():
    """检查远程仓库URL"""
    try:
        result = subprocess.run(
            ['git', 'remote', 'get-url', 'origin'],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return None
    except Exception:
        return None

def switch_to_ssh():
    """切换到SSH协议"""
    print("\n尝试切换到SSH协议...")
    
    current_url = check_remote_url()
    
    if not current_url:
        print("❌ 未配置远程仓库")
        return False
    
    print(f"当前URL: {current_url}")
    
    # 如果已经是SSH URL，直接返回成功
    if current_url.startswith('git@'):
        print("✅ 已经使用SSH协议")
        return True
    
    # 尝试从HTTPS URL转换为SSH URL
    if current_url.startswith('https://github.com/'):
        try:
            # https://github.com/username/repo.git -> git@github.com:username/repo.git
            ssh_url = current_url.replace('https://github.com/', 'git@github.com:')
            
            print(f"建议的SSH URL: {ssh_url}")
            
            # 生成SSH密钥
            print("\n正在生成SSH密钥...")
            subprocess.run(['ssh-keygen', '-t', 'ed25519', '-C', 'sql-manager@example.com', '-N', ''], 
                          capture_output=True, check=True)
            
            # 显示公钥
            pub_key_path = os.path.expanduser("~/.ssh/id_ed25519.pub")
            with open(pub_key_path, 'r') as f:
                pub_key = f.read().strip()
            
            print("\n" + "=" * 70)
            print("请将以下SSH公钥添加到GitHub:")
            print(pub_key)
            print("=" * 70)
            print("添加步骤:")
            print("1. 登录GitHub")
            print("2. 访问: https://github.com/settings/keys")
            print("3. 点击'New SSH key'")
            print("4. 粘贴公钥内容")
            print("5. 点击'Add SSH key'")
            
            input("\n添加完成后按回车键继续...")
            
            # 更新远程仓库URL
            subprocess.run(['git', 'remote', 'set-url', 'origin', ssh_url], check=True)
            print(f"✅ 远程仓库URL已更新为SSH协议")
            
            # 测试SSH连接
            print("\n测试SSH连接...")
            test_result = subprocess.run(
                ['ssh', '-T', 'git@github.com'],
                capture_output=True,
                text=True
            )
            
            if test_result.returncode in [0, 1]:  # GitHub SSH测试成功返回码是1
                print("✅ SSH连接测试成功")
                return True
            else:
                print(f"❌ SSH连接测试失败")
                print(test_result.stderr)
                return False
                
        except Exception as e:
            print(f"❌ 切换到SSH协议时出错: {e}")
            return False
    else:
        print(f"❌ 无法识别的URL格式: {current_url}")
        return False

def remove_proxy_config():
    """移除Git代理配置"""
    print("\n尝试移除Git代理配置...")
    
    try:
        # 检查是否配置了代理
        proxy_types = ['http', 'https', 'core']
        removed = False
        
        for proxy_type in proxy_types:
            result = subprocess.run(
                ['git', 'config', '--global', f'{proxy_type}.proxy'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0 and result.stdout.strip():
                subprocess.run(['git', 'config', '--global', '--unset', f'{proxy_type}.proxy'], check=True)
                print(f"✅ 已移除{proxy_type}.proxy配置")
                removed = True
        
        if not removed:
            print("✅ 未配置Git代理")
            
        return True
        
    except Exception as e:
        print(f"❌ 移除代理配置时出错: {e}")
        return False

def test_git_fetch():
    """测试Git fetch操作"""
    print("\n测试Git fetch操作...")
    
    try:
        result = subprocess.run(
            ['git', 'fetch', '--dry-run'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print("✅ Git fetch测试成功")
            return True
        else:
            print(f"❌ Git fetch测试失败")
            print(f"错误输出: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Git fetch操作超时")
        return False
    except Exception as e:
        print(f"❌ Git fetch测试时出错: {e}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("SQL管理工具 - GitHub连接问题一键修复")
    print("=" * 60)
    print("解决: Failed to connect to github.com port 443")
    print("=" * 60)
    
    # 测试当前连接
    print("\n1. 测试当前网络连接...")
    connection_ok = test_connection()
    
    if not connection_ok:
        print("\n2. 尝试常见解决方案...")
        
        # 方案1: 移除代理配置
        print("\n方案1: 移除Git代理配置")
        remove_proxy_config()
        
        # 重新测试连接
        print("\n重新测试连接...")
        if test_connection():
            print("✅ 移除代理配置后连接成功")
        else:
            # 方案2: 切换到SSH协议
            print("\n方案2: 切换到SSH协议 (推荐)")
            if switch_to_ssh():
                print("✅ 切换到SSH协议成功")
            else:
                print("❌ 所有方案尝试失败")
    
    # 最终测试
    print("\n3. 最终测试Git操作...")
    if test_git_fetch():
        print("\n🎉 GitHub连接问题已解决！")
        print("您现在可以正常使用git sync命令同步代码了")
    else:
        print("\n❌ GitHub连接问题仍未解决")
        print("\n建议的下一步:")
        print("1. 检查您的网络连接和防火墙设置")
        print("2. 确认您可以访问其他网站")
        print("3. 尝试使用浏览器访问https://github.com")
        print("4. 如果使用VPN，请尝试断开VPN")
        print("5. 运行完整诊断工具: python fix_github_connection.py")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
