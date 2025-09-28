#!/usr/bin/env python3
"""
GitHub管理工具 - GitHub连接问题修复工具
解决网络连接问题的诊断和解决方案
"""

import os
import sys
import subprocess
import socket
import platform
import json
from datetime import datetime

def print_section(title):
    """打印标题分隔线"""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")

def check_internet_connection():
    """检查网络连接"""
    print_section("检查网络连接")
    
    test_sites = [
        ("GitHub", "github.com", 443),
        ("Google", "www.google.com", 443),
        ("Baidu", "www.baidu.com", 443),
        ("HTTPBin", "httpbin.org", 443)
    ]
    
    results = []
    all_failed = True
    
    for name, host, port in test_sites:
        print(f"\n测试连接到 {name} ({host}:{port})...")
        
        try:
            # 测试DNS解析
            ip_addresses = socket.getaddrinfo(host, port, socket.AF_UNSPEC, socket.SOCK_STREAM)
            ip = ip_addresses[0][4][0]
            print(f"✅ DNS解析成功: {host} -> {ip}")
            
            # 测试TCP连接
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            
            start_time = datetime.now()
            result = sock.connect_ex((host, port))
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds() * 1000
            
            sock.close()
            
            if result == 0:
                print(f"✅ TCP连接成功 (耗时: {duration:.1f}ms)")
                results.append((name, "成功", f"连接耗时: {duration:.1f}ms"))
                all_failed = False
            else:
                print(f"❌ TCP连接失败 (错误码: {result})")
                results.append((name, "失败", f"错误码: {result}"))
                
        except socket.gaierror as e:
            print(f"❌ DNS解析失败: {e}")
            results.append((name, "失败", f"DNS解析错误: {e}"))
        except socket.timeout:
            print(f"❌ 连接超时 (超过10秒)")
            results.append((name, "失败", "连接超时"))
        except Exception as e:
            print(f"❌ 连接错误: {e}")
            results.append((name, "失败", f"错误: {e}"))
    
    print(f"\n{'=' * 60}")
    print("网络连接测试总结:")
    print("-" * 60)
    
    for name, status, details in results:
        status_icon = "✅" if status == "成功" else "❌"
        print(f"{status_icon} {name}: {status} - {details}")
    
    return not all_failed

def check_git_config():
    """检查Git配置"""
    print_section("检查Git配置")
    
    config_items = [
        ("user.name", "用户名"),
        ("user.email", "邮箱"),
        ("remote.origin.url", "远程仓库URL"),
        ("http.proxy", "HTTP代理"),
        ("https.proxy", "HTTPS代理"),
        ("core.proxy", "Git代理")
    ]
    
    config_results = {}
    
    for config_key, config_desc in config_items:
        try:
            result = subprocess.run(
                ['git', 'config', '--global', config_key],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                value = result.stdout.strip()
                config_results[config_key] = value
                print(f"ℹ️ {config_desc}: {value}")
            else:
                config_results[config_key] = None
                print(f"ℹ️ {config_desc}: 未配置")
                
        except Exception as e:
            config_results[config_key] = None
            print(f"⚠️ 获取{config_desc}时出错: {e}")
    
    return config_results

def check_git_remote():
    """检查Git远程仓库配置"""
    print_section("检查Git远程仓库配置")
    
    try:
        # 检查是否有远程仓库
        result = subprocess.run(
            ['git', 'remote', 'get-url', 'origin'],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            remote_url = result.stdout.strip()
            print(f"✅ 已配置远程仓库: {remote_url}")
            
            # 分析URL类型
            if remote_url.startswith('https://'):
                print(f"ℹ️ URL类型: HTTPS")
                return {'type': 'https', 'url': remote_url, 'status': 'success'}
            elif remote_url.startswith('git@'):
                print(f"ℹ️ URL类型: SSH")
                return {'type': 'ssh', 'url': remote_url, 'status': 'success'}
            else:
                print(f"⚠️ URL类型: 未知")
                return {'type': 'unknown', 'url': remote_url, 'status': 'warning'}
        else:
            print(f"❌ 未配置远程仓库")
            return {'type': None, 'url': None, 'status': 'error'}
            
    except Exception as e:
        print(f"❌ 检查远程仓库时出错: {e}")
        return {'type': None, 'url': None, 'status': 'error'}

def test_git_connectivity():
    """测试Git连接性"""
    print_section("测试Git连接性")
    
    tests = [
        ("Git版本", ["git", "--version"]),
        ("Git配置检查", ["git", "config", "--list"]),
        ("Git远程仓库信息", ["git", "remote", "-v"]),
        ("Git fetch测试", ["git", "fetch", "--dry-run"])
    ]
    
    results = []
    
    for test_name, command in tests:
        print(f"\n运行测试: {test_name}")
        print(f"命令: {' '.join(command)}")
        print("-" * 40)
        
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print(f"✅ 测试成功")
                if result.stdout:
                    print(f"输出:\n{result.stdout[:500]}...")  # 只显示前500字符
                results.append((test_name, "成功"))
            else:
                print(f"❌ 测试失败 (返回码: {result.returncode})")
                print(f"错误输出:\n{result.stderr}")
                results.append((test_name, "失败"))
                
        except subprocess.TimeoutExpired:
            print(f"❌ 测试超时 (超过30秒)")
            results.append((test_name, "超时"))
        except Exception as e:
            print(f"❌ 测试出错: {e}")
            results.append((test_name, "错误"))
    
    return results

def suggest_solutions(network_test_results, git_config, remote_info):
    """提供解决方案建议"""
    print_section("解决方案建议")
    
    solutions = []
    
    # 网络连接问题
    if not network_test_results:
        solutions.append({
            "priority": "高",
            "title": "检查基本网络连接",
            "steps": [
                "确认您的网络连接正常",
                "检查路由器和网络设备",
                "尝试连接其他网站确认网络是否正常",
                "如果使用VPN，请尝试断开VPN后重试"
            ]
        })
    
    # GitHub特定连接问题
    if any("GitHub" in result[0] and result[1] == "失败" for result in network_test_results):
        solutions.append({
            "priority": "高",
            "title": "解决GitHub连接问题",
            "steps": [
                "检查是否可以访问其他网站 (如https://www.google.com)",
                "尝试使用浏览器访问https://github.com确认是否被屏蔽",
                "检查防火墙设置，确保允许访问GitHub",
                "尝试更换网络环境 (如使用手机热点)"
            ]
        })
    
    # HTTPS连接问题
    if remote_info and remote_info['type'] == 'https':
        solutions.append({
            "priority": "中",
            "title": "HTTPS连接优化",
            "steps": [
                "尝试使用SSH协议替代HTTPS",
                "配置Git使用特定的SSL证书",
                "更新CA证书库"
            ]
        })
    
    # 代理配置问题
    if git_config.get('http.proxy') or git_config.get('https.proxy'):
        solutions.append({
            "priority": "中",
            "title": "代理配置检查",
            "steps": [
                "确认代理服务器是否正常工作",
                "检查代理配置是否正确",
                "如果不需要代理，可以移除代理配置"
            ]
        })
    else:
        solutions.append({
            "priority": "低",
            "title": "尝试使用代理",
            "steps": [
                "如果您在企业网络中，可能需要配置代理",
                "联系网络管理员获取代理设置"
            ]
        })
    
    # 协议切换建议
    solutions.append({
        "priority": "高",
        "title": "切换到SSH协议 (推荐)",
        "steps": [
            "生成SSH密钥: ssh-keygen -t ed25519 -C \"your_email@example.com\"",
            "将公钥添加到GitHub: https://github.com/settings/keys",
            "更新远程仓库URL: git remote set-url origin git@github.com:username/repo.git"
        ]
    })
    
    # 备用方案
    solutions.append({
        "priority": "中",
        "title": "使用GitHub镜像或CDN",
        "steps": [
            "尝试使用GitHub镜像站点",
            "配置hosts文件指向GitHub的IP地址"
        ]
    })
    
    # 显示解决方案
    for i, solution in enumerate(solutions, 1):
        print(f"\n{i}. [{solution['priority']}] {solution['title']}")
        for j, step in enumerate(solution['steps'], 1):
            print(f"   {j}. {step}")
    
    return solutions

def create_detailed_report(network_results, git_config, remote_info, test_results, solutions):
    """创建详细报告"""
    print_section("生成详细报告")
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "system": {
            "os": platform.system(),
            "os_version": platform.version(),
            "python_version": sys.version.split()[0],
            "platform": platform.platform()
        },
        "network_tests": network_results,
        "git_config": git_config,
        "remote_repository": remote_info,
        "git_tests": test_results,
        "solutions": solutions
    }
    
    # 保存报告到文件
    report_filename = f"github_connection_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    try:
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 详细报告已保存到: {report_filename}")
        return report_filename
        
    except Exception as e:
        print(f"❌ 保存报告时出错: {e}")
        return None

def apply_fix_ssh_switch():
    """应用SSH切换修复"""
    print_section("应用SSH切换修复")
    
    try:
        # 检查是否已配置远程仓库
        result = subprocess.run(
            ['git', 'remote', 'get-url', 'origin'],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print("❌ 未配置远程仓库，请先配置")
            return False
        
        current_url = result.stdout.strip()
        print(f"当前远程仓库URL: {current_url}")
        
        # 检查是否已经是SSH URL
        if current_url.startswith('git@'):
            print("✅ 已经使用SSH协议")
            return True
        
        # 尝试从HTTPS URL转换为SSH URL
        if current_url.startswith('https://github.com/'):
            # https://github.com/username/repo.git -> git@github.com:username/repo.git
            ssh_url = current_url.replace('https://github.com/', 'git@github.com:').replace('.git', '') + '.git'
            
            print(f"建议的SSH URL: {ssh_url}")
            
            # 询问用户是否要切换
            choice = input("是否要切换到SSH协议? (y/n): ").lower()
            
            if choice == 'y':
                # 检查SSH密钥是否存在
                ssh_key_path = os.path.expanduser("~/.ssh/id_ed25519")
                
                if not os.path.exists(ssh_key_path):
                    print("ℹ️  未找到SSH密钥，正在生成...")
                    
                    # 生成SSH密钥
                    email = input("请输入您的GitHub邮箱: ").strip()
                    
                    if not email:
                        print("❌ 邮箱不能为空")
                        return False
                    
                    subprocess.run(['ssh-keygen', '-t', 'ed25519', '-C', email, '-N', ''], check=True)
                    print("✅ SSH密钥生成成功")
                
                # 显示公钥内容
                pub_key_path = os.path.expanduser("~/.ssh/id_ed25519.pub")
                with open(pub_key_path, 'r') as f:
                    pub_key = f.read().strip()
                
                print(f"\n请将以下SSH公钥添加到GitHub:")
                print("=" * 60)
                print(pub_key)
                print("=" * 60)
                print("添加地址: https://github.com/settings/keys")
                print("密钥名称建议: sql-manager-machine")
                
                input("\n添加完成后按回车键继续...")
                
                # 更新远程仓库URL
                subprocess.run(['git', 'remote', 'set-url', 'origin', ssh_url], check=True)
                print(f"✅ 远程仓库URL已更新为: {ssh_url}")
                
                # 测试SSH连接
                print("\n测试SSH连接到GitHub...")
                test_result = subprocess.run(
                    ['ssh', '-T', 'git@github.com'],
                    capture_output=True,
                    text=True
                )
                
                if test_result.returncode == 1:  # SSH测试成功返回码是1
                    print("✅ SSH连接测试成功")
                    print(test_result.stdout)
                    return True
                else:
                    print(f"❌ SSH连接测试失败")
                    print(test_result.stderr)
                    return False
            else:
                print("ℹ️  已取消切换到SSH协议")
                return False
        else:
            print(f"❌ 无法识别的URL格式: {current_url}")
            return False
            
    except Exception as e:
        print(f"❌ 应用修复时出错: {e}")
        return False

def apply_fix_remove_proxy():
    """应用移除代理修复"""
    print_section("应用移除代理修复")
    
    try:
        # 检查是否配置了代理
        proxy_configs = []
        
        for proxy_type in ['http', 'https', 'core']:
            result = subprocess.run(
                ['git', 'config', '--global', f'{proxy_type}.proxy'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0 and result.stdout.strip():
                proxy_configs.append(proxy_type)
        
        if not proxy_configs:
            print("✅ 未配置Git代理")
            return True
        
        print(f"检测到配置的代理: {', '.join(proxy_configs)}")
        
        # 询问用户是否要移除
        choice = input("是否要移除所有Git代理配置? (y/n): ").lower()
        
        if choice == 'y':
            for proxy_type in proxy_configs:
                subprocess.run(['git', 'config', '--global', '--unset', f'{proxy_type}.proxy'], check=True)
                print(f"✅ 已移除{proxy_type}.proxy配置")
            
            print("✅ 所有代理配置已移除")
            return True
        else:
            print("ℹ️  已取消移除代理配置")
            return False
            
    except Exception as e:
        print(f"❌ 移除代理配置时出错: {e}")
        return False

def main():
    """主函数"""
    print("=" * 80)
    print("SQL管理工具 - GitHub连接问题修复工具")
    print("=" * 80)
    print("诊断和解决GitHub连接问题 (Failed to connect to github.com port 443)")
    print("=" * 80)
    
    # 运行诊断
    network_ok = check_internet_connection()
    git_config = check_git_config()
    remote_info = check_git_remote()
    git_tests = test_git_connectivity()
    
    # 生成解决方案
    solutions = suggest_solutions(git_tests, git_config, remote_info)
    
    # 创建详细报告
    report_file = create_detailed_report(network_ok, git_config, remote_info, git_tests, solutions)
    
    # 提供修复选项
    print_section("快速修复选项")
    
    while True:
        print("\n请选择要应用的修复:")
        print("1. 切换到SSH协议 (推荐)")
        print("2. 移除Git代理配置")
        print("3. 手动配置代理")
        print("4. 测试连接")
        print("5. 查看详细报告")
        print("6. 退出")
        
        choice = input("\n请输入选项 (1-6): ").strip()
        
        if choice == '1':
            apply_fix_ssh_switch()
        elif choice == '2':
            apply_fix_remove_proxy()
        elif choice == '3':
            print("\n手动配置代理:")
            http_proxy = input("请输入HTTP代理 (如 http://proxy:port): ").strip()
            https_proxy = input("请输入HTTPS代理 (如 https://proxy:port): ").strip()
            
            if http_proxy:
                subprocess.run(['git', 'config', '--global', 'http.proxy', http_proxy])
                print(f"✅ 已配置HTTP代理: {http_proxy}")
            
            if https_proxy:
                subprocess.run(['git', 'config', '--global', 'https.proxy', https_proxy])
                print(f"✅ 已配置HTTPS代理: {https_proxy}")
        elif choice == '4':
            test_git_connectivity()
        elif choice == '5':
            if report_file and os.path.exists(report_file):
                print(f"\n详细报告位置: {os.path.abspath(report_file)}")
                print("您可以查看此文件获取完整的诊断信息")
            else:
                print("❌ 未找到详细报告")
        elif choice == '6':
            print("\n退出修复工具")
            break
        else:
            print("无效选项，请重新输入")
    
    print("\n" + "=" * 80)
    print("GitHub连接问题修复工具已完成")
    print("=" * 80)

if __name__ == "__main__":
    main()
