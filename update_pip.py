#!/usr/bin/env python3
"""
pip升级pip升级脚本
自动解决pip升级通知问题
"""

import subprocess
import sys
import re
import platform

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
    except subprocess.CalledProcessError as e:
        print(f"获取pip版本失败: {e}")
        return None
    except Exception as e:
        print(f"获取pip版本时发生错误: {e}")
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

def upgrade_pip():
    """升级pip"""
    print("正在升级pip...")
    try:
        # 使用python -m pip install --upgrade pip
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "--upgrade", "pip"
        ])
        print("pip升级成功！")
        return True
    except subprocess.CalledProcessError as e:
        print(f"pip升级失败: {e}")
        return False
    except Exception as e:
        print(f"pip升级时发生错误: {e}")
        return False

def main():
    """主函数"""
    print("=" * 50)
    print("pip升级工具")
    print("=" * 50)
    
    current_version = get_current_pip_version()
    
    if not current_version:
        print("无法获取获取当前pip版本")
        return
    
    print(f"当前pip版本: {current_version}")
    
    # 检查是否版本是否低于25.2
    if is_version_less_than(current_version, "25.2"):
        print("检测到pip版本版本需要升级 (当前: {current_version}, 推荐: 25.2+)")
        
        # 询问用户用户版本是否已经足够新
        if is_version_less_than(current_version, "25.1.1"):
            print("您版本较旧，建议升级")
            choice = input("是否升级升级pip pippip pip? (y/n): ").lower()
            if choice == 'y':
                upgrade_pip()
            else:
                print("已选择不升级pip")
        else:
            # 版本在25.1.1到25.2之间，虽然需要强制需要升级
            print("pip版本版本接近最新版，可能不需要升级")
            print("如果仍然看到升级通知，可以可以运行: python -m pip install --upgrade pip")
    else:
        print("pip版本版本已是最新或高于需要升级")

if __name__ == "__main__":
    main()
